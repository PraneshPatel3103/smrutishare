from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import MediaRequest

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'profile_picture',
            'primary_phone',
            'primary_type',
            'secondary_phone',
            'secondary_type'
        ]

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("⚠️ This username is already taken. Please choose another one.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(label='Username or Phone')
    password = forms.CharField(widget=forms.PasswordInput)


class MediaRequestForm(forms.ModelForm):
    class Meta:
        model = MediaRequest
        fields = [
            'customer_name',
            'customer_email',
            'customer_phone',
            'date',
            'time',
            'location',
            'reference_image',
            'note'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass user from view
        super().__init__(*args, **kwargs)

        if user:
            # Prefill name + email
            self.fields['customer_name'].initial = user.username
            self.fields['customer_email'].initial = user.email

            # Make them readonly
            self.fields['customer_name'].disabled = True
            self.fields['customer_email'].disabled = True
