"""
Example Python client for Face Recognition API

This script demonstrates how to interact with the Face Recognition API
using the requests library.
"""
import requests
import json
from pathlib import Path
from typing import Optional


class FaceRecognitionClient:
    """Client for interacting with the Face Recognition API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"

    def health_check(self) -> dict:
        """
        Check API health status

        Returns:
            Health status information
        """
        response = requests.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()

    def add_face(self, image_path: str, name: str) -> dict:
        """
        Add a known face to the database

        Args:
            image_path: Path to image file
            name: Name to associate with the face

        Returns:
            Result of the operation
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {"name": name}
            response = requests.post(f"{self.api_url}/faces/add", files=files, data=data)
            response.raise_for_status()
            return response.json()

    def recognize_faces(self, image_path: str, tolerance: Optional[float] = None) -> dict:
        """
        Recognize faces in an image

        Args:
            image_path: Path to image file
            tolerance: Optional tolerance value (0.0-1.0)

        Returns:
            Recognition results
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            data = {}
            if tolerance is not None:
                data["tolerance"] = tolerance

            response = requests.post(f"{self.api_url}/recognize", files=files, data=data)
            response.raise_for_status()
            return response.json()

    def list_faces(self) -> dict:
        """
        List all known faces

        Returns:
            List of known faces
        """
        response = requests.get(f"{self.api_url}/faces")
        response.raise_for_status()
        return response.json()

    def remove_face(self, name: str) -> dict:
        """
        Remove a known face from the database

        Args:
            name: Name of the person to remove

        Returns:
            Result of the operation
        """
        response = requests.delete(f"{self.api_url}/faces/{name}")
        response.raise_for_status()
        return response.json()

    def detect_faces(self, image_path: str) -> dict:
        """
        Detect faces in an image without recognition

        Args:
            image_path: Path to image file

        Returns:
            Face detection results
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.api_url}/detect", files=files)
            response.raise_for_status()
            return response.json()

    def get_landmarks(self, image_path: str) -> dict:
        """
        Get facial landmarks from an image

        Args:
            image_path: Path to image file

        Returns:
            Facial landmarks
        """
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.api_url}/landmarks", files=files)
            response.raise_for_status()
            return response.json()


def main():
    """Example usage of the Face Recognition API client"""

    # Initialize client
    client = FaceRecognitionClient("http://localhost:8000")

    print("=" * 60)
    print("Face Recognition API - Python Client Example")
    print("=" * 60)

    # Check API health
    print("\n1. Checking API health...")
    try:
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Version: {health['version']}")
        print(f"   Known faces: {health['known_faces_count']}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Make sure the API is running at http://localhost:8000")
        return

    # Example: Add a known face (you'll need to provide an actual image)
    print("\n2. Adding a known face...")
    print("   Note: Update the image path below with a real image")
    # Uncomment and update the path below:
    # try:
    #     result = client.add_face("path/to/person.jpg", "John Doe")
    #     print(f"   {result['message']}")
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example: List known faces
    print("\n3. Listing known faces...")
    try:
        result = client.list_faces()
        print(f"   Unique people: {result['unique_people']}")
        print(f"   People: {', '.join(result['people']) if result['people'] else 'None'}")
    except Exception as e:
        print(f"   Error: {e}")

    # Example: Recognize faces (you'll need to provide an actual image)
    print("\n4. Recognizing faces...")
    print("   Note: Update the image path below with a real image")
    # Uncomment and update the path below:
    # try:
    #     result = client.recognize_faces("path/to/group_photo.jpg")
    #     print(f"   {result['message']}")
    #     for face in result['faces']:
    #         print(f"   - {face['name']}: {face['confidence']:.2f} confidence")
    # except Exception as e:
    #     print(f"   Error: {e}")

    # Example: Detect faces
    print("\n5. Detecting faces...")
    print("   Note: Update the image path below with a real image")
    # Uncomment and update the path below:
    # try:
    #     result = client.detect_faces("path/to/photo.jpg")
    #     print(f"   Faces found: {result['faces_found']}")
    # except Exception as e:
    #     print(f"   Error: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
