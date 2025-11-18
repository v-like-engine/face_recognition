"""
Real-time face recognition functionality with logging
"""
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional, Set
from pathlib import Path
import json
from threading import Lock

from app.core.face_processor import face_processor
from config.settings import settings


class FaceRecognitionLogger:
    """Logs unique faces identified during recognition sessions"""

    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.lock = Lock()
        self.session_log_file = None
        self.unique_faces_in_session: Set[str] = set()
        self.face_encounters: Dict[str, int] = {}
        self.start_new_session()

    def start_new_session(self):
        """Start a new recognition session"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_file = self.log_dir / f"session_{timestamp}.json"
        self.unique_faces_in_session = set()
        self.face_encounters = {}

        # Initialize session log
        self._write_session_data({
            "session_start": datetime.now().isoformat(),
            "unique_faces": [],
            "encounters": {}
        })

    def log_face(self, name: str, confidence: float, location: dict):
        """
        Log a face detection

        Args:
            name: Name of the person
            confidence: Recognition confidence
            location: Face location in frame
        """
        with self.lock:
            timestamp = datetime.now().isoformat()

            # Track unique faces
            if name not in self.unique_faces_in_session:
                self.unique_faces_in_session.add(name)
                print(f"[NEW FACE DETECTED] {name} at {timestamp} (confidence: {confidence:.2f})")

            # Track encounters
            if name not in self.face_encounters:
                self.face_encounters[name] = 0
            self.face_encounters[name] += 1

            # Update session log
            self._update_session_log(name, confidence, location, timestamp)

    def _write_session_data(self, data: dict):
        """Write session data to log file"""
        try:
            with open(self.session_log_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error writing session log: {e}")

    def _update_session_log(self, name: str, confidence: float, location: dict, timestamp: str):
        """Update session log with new face detection"""
        try:
            # Read current log
            with open(self.session_log_file, "r") as f:
                data = json.load(f)

            # Update unique faces list
            if name not in data["unique_faces"]:
                data["unique_faces"].append(name)

            # Update encounters
            if name not in data["encounters"]:
                data["encounters"][name] = {
                    "first_seen": timestamp,
                    "last_seen": timestamp,
                    "count": 0,
                    "detections": []
                }

            data["encounters"][name]["count"] += 1
            data["encounters"][name]["last_seen"] = timestamp
            data["encounters"][name]["detections"].append({
                "timestamp": timestamp,
                "confidence": confidence,
                "location": location
            })

            # Keep only last 10 detections per person to limit file size
            if len(data["encounters"][name]["detections"]) > 10:
                data["encounters"][name]["detections"] = data["encounters"][name]["detections"][-10:]

            # Write updated log
            self._write_session_data(data)

        except Exception as e:
            print(f"Error updating session log: {e}")

    def get_session_summary(self) -> dict:
        """Get summary of current session"""
        with self.lock:
            return {
                "unique_faces_count": len(self.unique_faces_in_session),
                "unique_faces": sorted(list(self.unique_faces_in_session)),
                "encounters": dict(self.face_encounters),
                "log_file": str(self.session_log_file)
            }

    def print_summary(self):
        """Print session summary to console"""
        summary = self.get_session_summary()
        print("\n" + "=" * 60)
        print("SESSION SUMMARY")
        print("=" * 60)
        print(f"Unique faces detected: {summary['unique_faces_count']}")
        print(f"Faces: {', '.join(summary['unique_faces']) if summary['unique_faces'] else 'None'}")
        print("\nEncounter counts:")
        for name, count in summary['encounters'].items():
            print(f"  - {name}: {count} times")
        print(f"\nLog file: {summary['log_file']}")
        print("=" * 60 + "\n")


class VideoStreamProcessor:
    """Processes video stream for real-time face recognition"""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.capture = None
        self.is_running = False
        self.logger = FaceRecognitionLogger()
        self.frame_skip = 3  # Process every Nth frame for performance
        self.frame_count = 0

    def start_camera(self) -> bool:
        """Start camera capture"""
        try:
            self.capture = cv2.VideoCapture(self.camera_index)
            if not self.capture.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False

            self.is_running = True
            print(f"Camera {self.camera_index} started successfully")
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def stop_camera(self):
        """Stop camera capture"""
        self.is_running = False
        if self.capture:
            self.capture.release()
        print("Camera stopped")
        self.logger.print_summary()

    def read_frame(self) -> Optional[np.ndarray]:
        """Read a frame from camera"""
        if not self.capture or not self.is_running:
            return None

        ret, frame = self.capture.read()
        if not ret:
            return None

        return frame

    def process_frame(self, frame: np.ndarray, perform_recognition: bool = True) -> tuple:
        """
        Process a frame for face recognition

        Args:
            frame: Video frame (BGR format from OpenCV)
            perform_recognition: Whether to perform recognition (can be skipped for some frames)

        Returns:
            Tuple of (processed_frame, faces_data)
        """
        self.frame_count += 1

        # Skip frames for performance
        if perform_recognition and self.frame_count % self.frame_skip != 0:
            perform_recognition = False

        # Convert BGR to RGB for face_recognition library
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces_data = []

        if perform_recognition:
            # Detect faces
            face_locations = face_processor.detect_faces(rgb_frame)

            if face_locations:
                # Get face encodings
                face_encodings = face_processor.get_face_encodings(rgb_frame, face_locations)

                # Recognize each face
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    name = "Unknown"
                    confidence = 0.0

                    if len(face_processor.known_face_encodings) > 0:
                        # Compare with known faces
                        matches = face_processor.compare_faces(
                            face_processor.known_face_encodings,
                            face_encoding
                        )
                        face_distances = face_processor.face_distance(
                            face_processor.known_face_encodings,
                            face_encoding
                        )

                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = face_processor.known_face_names[best_match_index]
                                confidence = 1 - face_distances[best_match_index]

                    location = {
                        "top": int(top),
                        "right": int(right),
                        "bottom": int(bottom),
                        "left": int(left)
                    }

                    faces_data.append({
                        "name": name,
                        "confidence": float(confidence),
                        "location": location
                    })

                    # Log the face
                    if name != "Unknown":
                        self.logger.log_face(name, confidence, location)

                    # Draw rectangle and label on frame
                    color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                    # Draw label background
                    label = f"{name} ({confidence:.2f})" if name != "Unknown" else "Unknown"
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                    cv2.putText(frame, label, (left + 6, bottom - 6),
                               cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        return frame, faces_data

    def get_session_summary(self) -> dict:
        """Get current session summary"""
        return self.logger.get_session_summary()


# Global video processor instance
video_processor = VideoStreamProcessor()
