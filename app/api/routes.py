"""
API route handlers for face recognition endpoints
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path

from app.core import face_processor
from app.models import (
    RecognitionResponse,
    AddFaceResponse,
    RemoveFaceResponse,
    KnownFacesResponse,
    HealthResponse,
    ErrorResponse,
)
from app.utils import save_upload_file, validate_file_extension, cleanup_file
from config.settings import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns the API status and number of known faces loaded
    """
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        known_faces_count=len(face_processor.known_face_names)
    )


@router.post("/recognize", response_model=RecognitionResponse)
async def recognize_faces(
    file: UploadFile = File(..., description="Image file to analyze"),
    tolerance: Optional[float] = Form(None, description="Face matching tolerance (0.0-1.0, lower is stricter)")
):
    """
    Recognize faces in an uploaded image

    Upload an image and get back information about any faces detected,
    including matches against known faces in the database.

    Args:
        file: Image file (jpg, jpeg, png, bmp)
        tolerance: Optional tolerance for face matching (default: 0.6)

    Returns:
        Recognition results with detected faces and their identities
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.allowed_extensions}"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size / (1024*1024)}MB"
        )

    # Reset file pointer
    await file.seek(0)

    temp_file = None
    try:
        # Save uploaded file temporarily
        temp_file = await save_upload_file(file, settings.upload_dir)

        # Process the image
        result = face_processor.recognize_faces(temp_file, tolerance=tolerance)

        return RecognitionResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file:
            cleanup_file(temp_file)


@router.post("/faces/add", response_model=AddFaceResponse)
async def add_known_face(
    file: UploadFile = File(..., description="Image file with a single face"),
    name: str = Form(..., description="Name to associate with this face")
):
    """
    Add a known face to the database

    Upload an image containing a single face and associate it with a name.
    The face encoding will be stored and used for future recognition.

    Args:
        file: Image file containing a single face
        name: Name to associate with the face

    Returns:
        Result of the add operation
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.allowed_extensions}"
        )

    # Check file size
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size / (1024*1024)}MB"
        )

    # Reset file pointer
    await file.seek(0)

    temp_file = None
    try:
        # Save uploaded file temporarily
        temp_file = await save_upload_file(file, settings.upload_dir)

        # Add the face
        result = face_processor.add_known_face(temp_file, name)

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

        return AddFaceResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file:
            cleanup_file(temp_file)


@router.delete("/faces/{name}", response_model=RemoveFaceResponse)
async def remove_known_face(name: str):
    """
    Remove a known face from the database

    Delete all face encodings associated with the given name.

    Args:
        name: Name of the person to remove

    Returns:
        Result of the remove operation
    """
    result = face_processor.remove_known_face(name)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["message"]
        )

    return RemoveFaceResponse(**result)


@router.get("/faces", response_model=KnownFacesResponse)
async def list_known_faces():
    """
    List all known faces in the database

    Returns a list of all people who have been added to the face recognition database,
    along with counts of how many face encodings exist for each person.

    Returns:
        List of known faces with statistics
    """
    result = face_processor.list_known_faces()
    return KnownFacesResponse(**result)


@router.post("/detect")
async def detect_faces(
    file: UploadFile = File(..., description="Image file to analyze")
):
    """
    Detect faces in an image without recognition

    Simply detect and locate faces in an image without attempting to identify them.

    Args:
        file: Image file to analyze

    Returns:
        Locations of detected faces
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.allowed_extensions}"
        )

    temp_file = None
    try:
        # Save uploaded file temporarily
        temp_file = await save_upload_file(file, settings.upload_dir)

        # Load and process image
        image = face_processor.load_image(temp_file)
        face_locations = face_processor.detect_faces(image)

        return {
            "success": True,
            "faces_found": len(face_locations),
            "locations": [
                {
                    "top": int(top),
                    "right": int(right),
                    "bottom": int(bottom),
                    "left": int(left)
                }
                for top, right, bottom, left in face_locations
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file:
            cleanup_file(temp_file)


@router.post("/landmarks")
async def get_face_landmarks(
    file: UploadFile = File(..., description="Image file to analyze")
):
    """
    Get facial landmarks from an image

    Detect faces and return detailed facial landmark information
    (eyes, nose, mouth, etc.)

    Args:
        file: Image file to analyze

    Returns:
        Facial landmarks for each detected face
    """
    # Validate file extension
    if not validate_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {settings.allowed_extensions}"
        )

    temp_file = None
    try:
        # Save uploaded file temporarily
        temp_file = await save_upload_file(file, settings.upload_dir)

        # Load and process image
        image = face_processor.load_image(temp_file)
        landmarks = face_processor.get_face_landmarks(image)

        return {
            "success": True,
            "faces_found": len(landmarks),
            "landmarks": landmarks
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file:
            cleanup_file(temp_file)
