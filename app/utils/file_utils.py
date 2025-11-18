"""
File handling utilities
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import aiofiles

from config.settings import settings


async def save_upload_file(upload_file: UploadFile, destination_dir: str) -> Path:
    """
    Save an uploaded file to the destination directory

    Args:
        upload_file: FastAPI UploadFile object
        destination_dir: Directory to save the file

    Returns:
        Path to the saved file
    """
    # Create destination directory if it doesn't exist
    dest_path = Path(destination_dir)
    dest_path.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = dest_path / unique_filename

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        content = await upload_file.read()
        await f.write(content)

    return file_path


def validate_file_extension(filename: str) -> bool:
    """
    Validate that a file has an allowed extension

    Args:
        filename: Name of the file

    Returns:
        True if extension is allowed, False otherwise
    """
    file_extension = Path(filename).suffix.lower()
    return file_extension in settings.allowed_extensions


def cleanup_file(file_path: Path) -> bool:
    """
    Delete a file

    Args:
        file_path: Path to the file to delete

    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False
