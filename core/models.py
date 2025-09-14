from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
import os
from django.conf import settings
from core.google_drive import list_files_in_folder

phone_validator = RegexValidator(
    r'^\+?[1-9]\d{7,14}$',
    'Enter a valid phone number with country code, e.g. +919876543210'
)

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(username=username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=False)

    primary_phone = models.CharField(max_length=16, validators=[phone_validator])
    primary_type = models.CharField(
        max_length=20,
        choices=[('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('both', 'Both')],
        default='whatsapp'
    )
    secondary_phone = models.CharField(max_length=16, validators=[phone_validator], blank=True, null=True)
    secondary_type = models.CharField(
        max_length=20,
        choices=[('whatsapp', 'WhatsApp'), ('telegram', 'Telegram'), ('both', 'Both')],
        blank=True, null=True
    )

    # Admin-only fields (not exposed to users)
    is_satsangi = models.BooleanField(default=False)
    is_ambrish = models.BooleanField(default=False)
    department_notes = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['primary_phone']

    objects = UserManager()

    def __str__(self):
        return self.username


class SiteSetting(models.Model):
    drive_profile_folder = models.CharField(max_length=255, blank=True, help_text='Drive folder id or full link for profile pictures')
    drive_reference_folder = models.CharField(max_length=255, blank=True, help_text='Drive folder id or full link for reference images')
    drive_data_folder = models.CharField(max_length=255, blank=True, help_text='Drive folder id or full link for data files')

    def __str__(self):
        return 'Site Settings'


class MediaRequest(models.Model):
    REQUEST_STATUS = [('open', 'Open'), ('resolved', 'Resolved')]

    user = models.ForeignKey('core.User', on_delete=models.CASCADE, related_name='requests')
    request_number = models.CharField(max_length=40, unique=True, editable=False)
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=16, validators=[phone_validator])
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    reference_image = models.FileField(upload_to='references/', blank=True, null=True)
    reference_image_drive_id = models.CharField(max_length=128, blank=True)
    note = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=REQUEST_STATUS, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'date', 'time', 'location'], name='unique_request_per_slot')
        ]
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.request_number:
            now = timezone.now()
            prefix = now.strftime('%Y%m%d_%H%M')
            existing = MediaRequest.objects.filter(request_number__startswith=prefix).count() + 1
            self.request_number = f"{prefix}_{existing:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.request_number} ({self.get_status_display()})"

    # 🔑 NEW METHODS
    def get_drive_file(self):
        """Return Google Drive file dict if a matching file exists (request_number + ext)."""
        from core.models import SiteSetting  # avoid circular import

        try:
            site_settings = SiteSetting.objects.first()
            folder_id = site_settings.drive_data_folder
            if not folder_id:
                return None

            files = list_files_in_folder(folder_id)
            for f in files:
                filename, ext = os.path.splitext(f["name"])
                if filename == str(self.request_number):
                    return f  # {"id": "...", "name": "..."}
        except Exception:
            return None
        return None

    def get_drive_file_link(self):
        """Return a Google Drive view link if matching file exists."""
        f = self.get_drive_file()
        if f:
            return f"https://drive.google.com/file/d/{f['id']}/view?usp=sharing"
        return None
