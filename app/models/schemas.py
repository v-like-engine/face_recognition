"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class FaceLocation(BaseModel):
    """Face location coordinates"""
    top: int = Field(..., description="Top coordinate of the face bounding box")
    right: int = Field(..., description="Right coordinate of the face bounding box")
    bottom: int = Field(..., description="Bottom coordinate of the face bounding box")
    left: int = Field(..., description="Left coordinate of the face bounding box")


class RecognizedFace(BaseModel):
    """Information about a recognized face"""
    name: str = Field(..., description="Name of the recognized person or 'Unknown'")
    confidence: float = Field(..., description="Confidence score (0-1)")
    location: FaceLocation = Field(..., description="Face location in the image")


class RecognitionResponse(BaseModel):
    """Response for face recognition"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    faces_found: int = Field(..., description="Number of faces detected")
    faces: List[RecognizedFace] = Field(default=[], description="List of recognized faces")


class AddFaceResponse(BaseModel):
    """Response for adding a known face"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")
    name: str = Field(..., description="Name associated with the face")
    face_location: Optional[tuple] = Field(None, description="Location of the detected face")


class RemoveFaceResponse(BaseModel):
    """Response for removing a known face"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Status message")


class KnownFacesResponse(BaseModel):
    """Response for listing known faces"""
    success: bool = Field(..., description="Whether the operation was successful")
    total_encodings: int = Field(..., description="Total number of face encodings")
    unique_people: int = Field(..., description="Number of unique people")
    people: List[str] = Field(..., description="List of known people names")
    counts: Dict[str, int] = Field(..., description="Count of encodings per person")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    known_faces_count: int = Field(..., description="Number of known faces loaded")


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
