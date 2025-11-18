"""
Core face recognition processing functionality
"""
import face_recognition
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import pickle
import os

from config.settings import settings


class FaceProcessor:
    """Handles all face recognition operations"""

    def __init__(self):
        self.known_faces_dir = Path(settings.known_faces_dir)
        self.known_faces_dir.mkdir(exist_ok=True)
        self.tolerance = settings.tolerance
        self.model = settings.face_detection_model
        self.num_jitters = settings.num_jitters
        self.known_face_encodings = []
        self.known_face_names = []
        self.encodings_file = self.known_faces_dir / "encodings.pkl"
        self._load_known_faces()

    def _load_known_faces(self):
        """Load known face encodings from file"""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, "rb") as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data.get("encodings", [])
                    self.known_face_names = data.get("names", [])
                print(f"Loaded {len(self.known_face_names)} known faces")
            except Exception as e:
                print(f"Error loading known faces: {e}")
                self.known_face_encodings = []
                self.known_face_names = []

    def _save_known_faces(self):
        """Save known face encodings to file"""
        try:
            with open(self.encodings_file, "wb") as f:
                pickle.dump({
                    "encodings": self.known_face_encodings,
                    "names": self.known_face_names
                }, f)
            print(f"Saved {len(self.known_face_names)} known faces")
        except Exception as e:
            print(f"Error saving known faces: {e}")

    def load_image(self, image_source: Union[str, bytes, Path]) -> np.ndarray:
        """
        Load an image from various sources

        Args:
            image_source: File path, bytes, or Path object

        Returns:
            numpy array of the image
        """
        if isinstance(image_source, bytes):
            image = Image.open(io.BytesIO(image_source))
            return np.array(image)
        elif isinstance(image_source, (str, Path)):
            return face_recognition.load_image_file(image_source)
        else:
            raise ValueError("Invalid image source type")

    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect face locations in an image

        Args:
            image: numpy array of the image

        Returns:
            List of face locations as (top, right, bottom, left) tuples
        """
        face_locations = face_recognition.face_locations(image, model=self.model)
        return face_locations

    def get_face_encodings(
        self,
        image: np.ndarray,
        face_locations: Optional[List[Tuple[int, int, int, int]]] = None
    ) -> List[np.ndarray]:
        """
        Get face encodings for faces in an image

        Args:
            image: numpy array of the image
            face_locations: Optional pre-detected face locations

        Returns:
            List of 128-dimensional face encodings
        """
        encodings = face_recognition.face_encodings(
            image,
            known_face_locations=face_locations,
            num_jitters=self.num_jitters
        )
        return encodings

    def compare_faces(
        self,
        known_encodings: List[np.ndarray],
        face_encoding: np.ndarray,
        tolerance: Optional[float] = None
    ) -> List[bool]:
        """
        Compare a face encoding against known face encodings

        Args:
            known_encodings: List of known face encodings
            face_encoding: Face encoding to compare
            tolerance: Optional tolerance value (lower is more strict)

        Returns:
            List of boolean matches
        """
        if tolerance is None:
            tolerance = self.tolerance
        return face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)

    def face_distance(
        self,
        known_encodings: List[np.ndarray],
        face_encoding: np.ndarray
    ) -> np.ndarray:
        """
        Calculate face distances between a face and known faces

        Args:
            known_encodings: List of known face encodings
            face_encoding: Face encoding to compare

        Returns:
            numpy array of distances (lower means more similar)
        """
        return face_recognition.face_distance(known_encodings, face_encoding)

    def add_known_face(
        self,
        image_source: Union[str, bytes, Path],
        name: str
    ) -> Dict[str, any]:
        """
        Add a known face to the database

        Args:
            image_source: Image file path or bytes
            name: Name to associate with the face

        Returns:
            Dictionary with results
        """
        try:
            image = self.load_image(image_source)
            face_locations = self.detect_faces(image)

            if len(face_locations) == 0:
                return {
                    "success": False,
                    "message": "No face detected in the image",
                    "name": name
                }

            if len(face_locations) > 1:
                return {
                    "success": False,
                    "message": f"Multiple faces detected ({len(face_locations)}). Please provide an image with a single face.",
                    "name": name
                }

            encodings = self.get_face_encodings(image, face_locations)

            if len(encodings) > 0:
                self.known_face_encodings.append(encodings[0])
                self.known_face_names.append(name)
                self._save_known_faces()

                return {
                    "success": True,
                    "message": f"Successfully added face for {name}",
                    "name": name,
                    "face_location": face_locations[0]
                }
            else:
                return {
                    "success": False,
                    "message": "Could not encode face",
                    "name": name
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing image: {str(e)}",
                "name": name
            }

    def recognize_faces(
        self,
        image_source: Union[str, bytes, Path],
        tolerance: Optional[float] = None
    ) -> Dict[str, any]:
        """
        Recognize faces in an image against known faces

        Args:
            image_source: Image file path or bytes
            tolerance: Optional tolerance value

        Returns:
            Dictionary with recognition results
        """
        try:
            image = self.load_image(image_source)
            face_locations = self.detect_faces(image)

            if len(face_locations) == 0:
                return {
                    "success": True,
                    "message": "No faces detected in the image",
                    "faces_found": 0,
                    "faces": []
                }

            face_encodings = self.get_face_encodings(image, face_locations)

            faces = []
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = self.compare_faces(
                    self.known_face_encodings,
                    face_encoding,
                    tolerance=tolerance
                )
                name = "Unknown"
                confidence = 0.0

                if len(self.known_face_encodings) > 0:
                    face_distances = self.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        # Convert distance to confidence (0-1 scale)
                        confidence = 1 - face_distances[best_match_index]

                faces.append({
                    "name": name,
                    "confidence": float(confidence),
                    "location": {
                        "top": int(top),
                        "right": int(right),
                        "bottom": int(bottom),
                        "left": int(left)
                    }
                })

            return {
                "success": True,
                "message": f"Detected {len(faces)} face(s)",
                "faces_found": len(faces),
                "faces": faces
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing image: {str(e)}",
                "faces_found": 0,
                "faces": []
            }

    def remove_known_face(self, name: str) -> Dict[str, any]:
        """
        Remove a known face from the database

        Args:
            name: Name of the person to remove

        Returns:
            Dictionary with results
        """
        try:
            if name not in self.known_face_names:
                return {
                    "success": False,
                    "message": f"No face found with name: {name}"
                }

            # Remove all occurrences (in case there are duplicates)
            indices_to_remove = [i for i, n in enumerate(self.known_face_names) if n == name]

            for index in sorted(indices_to_remove, reverse=True):
                del self.known_face_encodings[index]
                del self.known_face_names[index]

            self._save_known_faces()

            return {
                "success": True,
                "message": f"Removed {len(indices_to_remove)} face(s) for {name}"
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error removing face: {str(e)}"
            }

    def list_known_faces(self) -> Dict[str, any]:
        """
        Get a list of all known faces

        Returns:
            Dictionary with list of known face names
        """
        unique_names = list(set(self.known_face_names))
        name_counts = {name: self.known_face_names.count(name) for name in unique_names}

        return {
            "success": True,
            "total_encodings": len(self.known_face_names),
            "unique_people": len(unique_names),
            "people": sorted(unique_names),
            "counts": name_counts
        }

    def get_face_landmarks(self, image: np.ndarray) -> List[Dict]:
        """
        Get facial landmarks for faces in an image

        Args:
            image: numpy array of the image

        Returns:
            List of dictionaries containing facial landmarks
        """
        face_landmarks_list = face_recognition.face_landmarks(image)
        return face_landmarks_list


# Global instance
face_processor = FaceProcessor()
