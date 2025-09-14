import os
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .forms import RegisterForm, LoginForm, MediaRequestForm
from .models import MediaRequest, SiteSetting
from .google_drive import extract_folder_id, upload_file_to_drive


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # upload profile picture to drive folder if configured
            try:
                settings_obj = SiteSetting.objects.first()
                folder_link = settings_obj.drive_profile_folder or settings.GDRIVE_PROFILE_FOLDER_ID if settings_obj else settings.GDRIVE_PROFILE_FOLDER_ID
                folder_id = extract_folder_id(folder_link)
                if user.profile_picture and folder_id:
                    local_path = user.profile_picture.path
                    filename = f"{user.username}_{os.path.basename(local_path)}"
                    upload_file_to_drive(local_path, filename, folder_id)
            except Exception as e:
                messages.warning(request, f"Profile saved but Drive upload failed: {e}")
            messages.success(request, 'Account created. Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        pwd = form.cleaned_data['password']
        user = authenticate(request, username=username, password=pwd)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials')
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    requests_qs = MediaRequest.objects.filter(user=user).order_by('-created_at')

    # Attach Google Drive links (if available)
    requests_with_files = []
    for r in requests_qs:
        drive_link = r.get_drive_file_link()
        requests_with_files.append((r, drive_link))

    return render(
        request,
        'dashboard.html',
        {
            'requests_with_files': requests_with_files
        }
    )


@login_required
def request_create(request):
    if request.method == 'POST':
        form = MediaRequestForm(request.POST, request.FILES, user=request.user)  # pass user
        if form.is_valid():
            media_req = form.save(commit=False)
            media_req.user = request.user
            media_req.customer_name = request.user.username   # auto-fill
            media_req.customer_email = request.user.email     # auto-fill
            try:
                media_req.save()
            except Exception:
                form.add_error(None, 'You already have a request for the same date, time and location.')
                return render(request, 'request_form.html', {'form': form})

            # upload reference image to drive folder if configured
            try:
                settings_obj = SiteSetting.objects.first()
                folder_link = settings_obj.drive_reference_folder or settings.GDRIVE_REFERENCE_FOLDER_ID if settings_obj else settings.GDRIVE_REFERENCE_FOLDER_ID
                folder_id = extract_folder_id(folder_link)
                if media_req.reference_image and folder_id:
                    local_path = media_req.reference_image.path
                    filename = f"{media_req.request_number}_{os.path.basename(local_path)}"
                    drive_id = upload_file_to_drive(local_path, filename, folder_id)
                    media_req.reference_image_drive_id = drive_id
                    media_req.save(update_fields=['reference_image_drive_id'])
            except Exception as e:
                messages.warning(request, f"Uploaded locally, but Drive upload failed: {e}")

            messages.success(request, f"Request sent successfully. Your request number is {media_req.request_number}.")
            return redirect('dashboard')
    else:
        form = MediaRequestForm(user=request.user)  # pass user here too

    return render(request, 'request_form.html', {'form': form})
