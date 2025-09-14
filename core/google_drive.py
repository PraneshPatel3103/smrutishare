# core/google_drive.py

import re
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FOLDER_ID_RE = re.compile(r"/folders/([a-zA-Z0-9_-]{10,})")


def extract_folder_id(link_or_id):
    """Extract folder ID from a Google Drive link or return raw ID."""
    if not link_or_id:
        return None
    match = FOLDER_ID_RE.search(link_or_id)
    if match:
        return match.group(1)
    return link_or_id


def upload_file_to_drive(file_path: str, filename: str, folder_id: str) -> str | None:
    """Upload file to Google Drive using pre-configured credentials."""
    # Get the credentials object directly from settings
    credentials = settings.GOOGLE_DRIVE_CREDENTIALS

    if not credentials:
        print("ERROR: Google Drive credentials are not configured in settings.py.")
        return None

    try:
        service = build("drive", "v3", credentials=credentials)
        file_metadata = {
            "name": filename,
            "parents": [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        created_file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id",
                supportsAllDrives=True,
            )
            .execute()
        )
        return created_file.get("id")
    except Exception as e:
        print(f"An error occurred during Google Drive upload: {e}")
        return None


def list_files_in_folder(folder_id: str):
    """List files in a Google Drive folder using pre-configured credentials."""
    # Get the credentials object directly from settings
    credentials = settings.GOOGLE_DRIVE_CREDENTIALS

    if not credentials:
        print("ERROR: Google Drive credentials are not configured in settings.py.")
        return []

    try:
        service = build("drive", "v3", credentials=credentials)
        query = f"'{folder_id}' in parents and trashed = false"
        results = (
            service.files()
            .list(
                q=query,
                fields="files(id,name)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        return results.get("files", [])
    except Exception as e:
        print(f"An error occurred while listing Google Drive files: {e}")
        return []