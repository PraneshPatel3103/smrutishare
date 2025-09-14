from django.contrib import admin
from django.utils.html import format_html
from .models import User, SiteSetting, MediaRequest


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'primary_phone', 'primary_type', 'is_satsangi', 'is_ambrish')
    readonly_fields = ('profile_preview',)
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'email',
                'profile_picture',
                'profile_preview',
                'primary_phone',
                'primary_type',
                'secondary_phone',
                'secondary_type',
                'is_active',
                'is_staff'
            )
        }),
        ('Admin-only', {
            'fields': ('is_satsangi', 'is_ambrish', 'department_notes'),
            'classes': ('collapse',)
        }),
    )
    search_fields = ('username', 'email', 'primary_phone')

    def profile_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="width:80px;height:80px;border-radius:8px;" />', obj.profile_picture.url)
        return 'No Image'
    profile_preview.short_description = 'Profile Picture'


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('drive_profile_folder', 'drive_reference_folder', 'drive_data_folder')


@admin.register(MediaRequest)
class MediaRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_number',
        'user',
        'customer_name',
        'date',
        'time',
        'location',
        'status',
        'send_whatsapp_button',
    )
    readonly_fields = (
        'request_number',
        'reference_image_drive_id',
        'created_at',
        'updated_at',
        'send_whatsapp_button',
    )
    actions = ['mark_resolved']

    def mark_resolved(self, request, queryset):
        updated = queryset.update(status='resolved')
        self.message_user(request, f"{updated} request(s) marked resolved.")
    mark_resolved.short_description = 'Resolve selected requests'

    def send_whatsapp_button(self, obj):
        """Render a clickable WhatsApp button in admin."""
        if not obj or not obj.user or not obj.user.primary_phone:
            return "No phone number"

        # Format phone number: remove spaces, +91 prefix handling
        phone = str(obj.user.primary_phone).replace(" ", "")
        if not phone.startswith("+"):
            phone = f"+91{phone}"  # default India prefix

        # Prefill message with request_number
        message = f"Hello, regarding your request {obj.request_number}"
        whatsapp_url = f"https://wa.me/{phone}?text={message}"

        return format_html(
            '<a href="{}" target="_blank" '
            'style="padding:6px 12px; background:#25D366; color:white; border-radius:4px; text-decoration:none;">'
            'Send on WhatsApp</a>',
            whatsapp_url
        )
    send_whatsapp_button.short_description = "WhatsApp"
