import os
import re
from django.conf import settings

FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]{10,})")

def _lazy_imports():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    return service_account, build, MediaFileUpload


def extract_folder_id(link_or_id):
    """Extract folder ID from a Google Drive link or return raw ID."""
    if not link_or_id:
        return None
    m = FOLDER_ID_RE.search(link_or_id)
    if m:
        return m.group(1)
    return link_or_id


def _get_service(scopes):
    """Return Google Drive service client or None if not configured."""
    if not settings.GDRIVE_SERVICE_ACCOUNT_FILE or not os.path.exists(settings.GDRIVE_SERVICE_ACCOUNT_FILE):
        return None

    service_account, build, _ = _lazy_imports()
    creds = service_account.Credentials.from_service_account_file(
        settings.GDRIVE_SERVICE_ACCOUNT_FILE, scopes=scopes
    )
    return build("drive", "v3", credentials=creds)


def upload_file_to_drive(file_path: str, filename: str, folder_id: str) -> str | None:
    """Upload file to Google Drive (supports Shared Drives)."""
    service_account, build, MediaFileUpload = _lazy_imports()
    service = _get_service(["https://www.googleapis.com/auth/drive.file"])
    if not service:
        return None

    file_metadata = {"name": filename}
    if folder_id:
        file_metadata["parents"] = [folder_id]

    media = MediaFileUpload(file_path, resumable=True)

    created = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
            supportsAllDrives=True,   # ✅ important
        )
        .execute()
    )
    return created.get("id")


def list_files_in_folder(folder_id: str):
    """List files in Google Drive folder (supports Shared Drives)."""
    service = _get_service(["https://www.googleapis.com/auth/drive.readonly"])
    if not service:
        return []

    q = f"'{folder_id}' in parents and trashed = false"
    results = (
        service.files()
        .list(
            q=q,
            fields="files(id,name)",
            supportsAllDrives=True,          # ✅ important
            includeItemsFromAllDrives=True,  # ✅ important
        )
        .execute()
    )
    return results.get("files", [])
