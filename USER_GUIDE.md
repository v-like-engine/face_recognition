# Face Recognition API - Comprehensive User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Quick Start](#quick-start)
4. [Testing Stand (Real-Time Camera)](#testing-stand-real-time-camera)
5. [API Reference](#api-reference)
6. [Python Client Usage](#python-client-usage)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

---

## Introduction

The Face Recognition API is a comprehensive tool for face detection, recognition, and tracking. It provides:

- **REST API** for image-based face recognition
- **Real-time camera interface** with WebSocket support
- **Face logging system** that tracks unique faces
- **Web-based testing stand** for live demonstrations
- **Session management** for tracking recognition sessions

### Key Features

- ✅ Face detection using HOG or CNN models
- ✅ Face recognition with configurable tolerance
- ✅ Real-time video streaming with WebSocket
- ✅ Unique face tracking and logging
- ✅ Interactive web testing interface
- ✅ Session summaries with statistics
- ✅ Export logs in JSON format

---

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- Webcam (for real-time features)
- 4GB RAM minimum (8GB recommended)
- Linux, macOS, or Windows

### Method 1: Local Installation (Recommended for Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd face_recognition

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create directories
mkdir -p uploads known_faces logs

# 6. Configure (optional)
cp .env.example .env
# Edit .env with your preferences

# 7. Run the application
python main.py
```

### Method 2: Docker Installation (Recommended for Production)

```bash
# Using Docker Compose
docker-compose up -d

# Or using Docker directly
docker build -t face-recognition-api .
docker run -p 8000:8000 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/known_faces:/app/known_faces \
  -v $(pwd)/logs:/app/logs \
  --device=/dev/video0:/dev/video0 \
  face-recognition-api
```

**Note:** For camera access in Docker, you need to pass the video device with `--device=/dev/video0:/dev/video0`

### Verify Installation

```bash
# Check if API is running
curl http://localhost:8000/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "known_faces_count": 0
# }
```

---

## Quick Start

### Step 1: Start the Server

```bash
python main.py
```

The server will start at `http://localhost:8000`

### Step 2: Access the Interfaces

- **Testing Stand (Camera Interface)**: http://localhost:8000/testing-stand
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Step 3: Add Known Faces

You can add faces using:

1. **Web Interface (Swagger UI)**: http://localhost:8000/docs
   - Navigate to POST `/api/v1/faces/add`
   - Click "Try it out"
   - Upload an image and enter a name
   - Click "Execute"

2. **cURL**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/faces/add" \
     -F "file=@path/to/photo.jpg" \
     -F "name=John Doe"
   ```

3. **Python**:
   ```python
   import requests

   with open("photo.jpg", "rb") as f:
       response = requests.post(
           "http://localhost:8000/api/v1/faces/add",
           files={"file": f},
           data={"name": "John Doe"}
       )
   print(response.json())
   ```

### Step 4: Test Recognition

1. **Using Testing Stand**:
   - Go to http://localhost:8000/testing-stand
   - Click "▶ Start Camera"
   - The system will detect and recognize faces in real-time

2. **Using API**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/recognize" \
     -F "file=@test_image.jpg"
   ```

---

## Testing Stand (Real-Time Camera)

### Overview

The Testing Stand is a web-based interface for real-time face recognition using your webcam. It provides:

- Live video feed with face detection boxes
- Real-time face recognition
- Unique face tracking
- Session statistics
- Detection logs
- Export functionality

### Accessing the Testing Stand

1. Start the server:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000/testing-stand
   ```

### Using the Testing Stand

#### Controls

1. **▶ Start Camera**
   - Starts the webcam and begins face recognition
   - Connects to the server via WebSocket
   - Displays live video feed with detection boxes

2. **⏹ Stop Camera**
   - Stops the camera feed
   - Closes WebSocket connection
   - Prints session summary to server console

3. **🔄 New Session**
   - Starts a new recognition session
   - Resets unique face counter
   - Creates a new log file
   - Use this when starting a new demonstration

4. **📥 Export Log**
   - Downloads the current session log as JSON
   - Includes all detected faces and statistics
   - File format: `face_recognition_log_YYYY-MM-DDTHH-MM-SS.json`

#### Dashboard Elements

**Status Badge**
- 🟢 ACTIVE: Camera is running
- 🔴 INACTIVE: Camera is stopped

**Session Statistics**
- **Unique Faces**: Number of different people detected
- **Total Detections**: Total number of face detections

**Identified People**
- Lists all unique people detected
- Shows encounter count for each person
- Updates in real-time

**Detection Log**
- Real-time log of events
- Shows timestamps and detection confidence
- Auto-scrolls to latest entries

### Log Files

Session logs are automatically saved in the `logs/` directory:

```
logs/
├── session_20250118_143052.json
├── session_20250118_150123.json
└── session_20250118_153045.json
```

**Log File Format**:
```json
{
  "session_start": "2025-01-18T14:30:52.123456",
  "unique_faces": ["John Doe", "Jane Smith"],
  "encounters": {
    "John Doe": {
      "first_seen": "2025-01-18T14:31:05.123456",
      "last_seen": "2025-01-18T14:35:22.789012",
      "count": 45,
      "detections": [
        {
          "timestamp": "2025-01-18T14:31:05.123456",
          "confidence": 0.87,
          "location": {"top": 100, "right": 250, "bottom": 300, "left": 150}
        }
      ]
    }
  }
}
```

### Console Output

When a new face is detected, the server prints:

```
[NEW FACE DETECTED] John Doe at 2025-01-18T14:31:05.123456 (confidence: 0.87)
```

When the camera stops, a session summary is printed:

```
============================================================
SESSION SUMMARY
============================================================
Unique faces detected: 3
Faces: Alice Johnson, Bob Smith, John Doe

Encounter counts:
  - John Doe: 45 times
  - Alice Johnson: 23 times
  - Bob Smith: 12 times

Log file: logs/session_20250118_143052.json
============================================================
```

---

## API Reference

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "known_faces_count": 5
}
```

#### 2. Add Known Face

```http
POST /api/v1/faces/add
```

**Parameters:**
- `file` (form-data): Image file
- `name` (form-data): Person's name

**Response:**
```json
{
  "success": true,
  "message": "Successfully added face for John Doe",
  "name": "John Doe",
  "face_location": [100, 250, 300, 150]
}
```

**Error Cases:**
- No face detected
- Multiple faces detected
- Image processing error

#### 3. Recognize Faces

```http
POST /api/v1/recognize
```

**Parameters:**
- `file` (form-data): Image file
- `tolerance` (form-data, optional): Recognition tolerance (0.0-1.0)

**Response:**
```json
{
  "success": true,
  "message": "Detected 2 face(s)",
  "faces_found": 2,
  "faces": [
    {
      "name": "John Doe",
      "confidence": 0.87,
      "location": {
        "top": 100,
        "right": 250,
        "bottom": 300,
        "left": 150
      }
    },
    {
      "name": "Unknown",
      "confidence": 0.0,
      "location": {
        "top": 120,
        "right": 280,
        "bottom": 320,
        "left": 180
      }
    }
  ]
}
```

#### 4. List Known Faces

```http
GET /api/v1/faces
```

**Response:**
```json
{
  "success": true,
  "total_encodings": 5,
  "unique_people": 3,
  "people": ["John Doe", "Jane Smith", "Bob Johnson"],
  "counts": {
    "John Doe": 2,
    "Jane Smith": 2,
    "Bob Johnson": 1
  }
}
```

#### 5. Remove Known Face

```http
DELETE /api/v1/faces/{name}
```

**Response:**
```json
{
  "success": true,
  "message": "Removed 2 face(s) for John Doe"
}
```

#### 6. Detect Faces (Without Recognition)

```http
POST /api/v1/detect
```

**Parameters:**
- `file` (form-data): Image file

**Response:**
```json
{
  "success": true,
  "faces_found": 2,
  "locations": [
    {"top": 100, "right": 250, "bottom": 300, "left": 150},
    {"top": 120, "right": 280, "bottom": 320, "left": 180}
  ]
}
```

#### 7. Get Facial Landmarks

```http
POST /api/v1/landmarks
```

**Parameters:**
- `file` (form-data): Image file

**Response:**
```json
{
  "success": true,
  "faces_found": 1,
  "landmarks": [
    {
      "chin": [[x1, y1], [x2, y2], ...],
      "left_eyebrow": [[x1, y1], [x2, y2], ...],
      "right_eyebrow": [[x1, y1], [x2, y2], ...],
      "nose_bridge": [[x1, y1], [x2, y2], ...],
      "nose_tip": [[x1, y1], [x2, y2], ...],
      "left_eye": [[x1, y1], [x2, y2], ...],
      "right_eye": [[x1, y1], [x2, y2], ...],
      "top_lip": [[x1, y1], [x2, y2], ...],
      "bottom_lip": [[x1, y1], [x2, y2], ...]
    }
  ]
}
```

### Camera/Streaming Endpoints

#### 8. Start Camera

```http
POST /api/v1/camera/start
```

**Response:**
```json
{
  "success": true,
  "message": "Camera started successfully"
}
```

#### 9. Stop Camera

```http
POST /api/v1/camera/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Camera stopped"
}
```

#### 10. Get Camera Status

```http
GET /api/v1/camera/status
```

**Response:**
```json
{
  "is_running": true,
  "summary": {
    "unique_faces_count": 3,
    "unique_faces": ["John Doe", "Jane Smith", "Bob Johnson"],
    "encounters": {
      "John Doe": 45,
      "Jane Smith": 23,
      "Bob Johnson": 12
    },
    "log_file": "logs/session_20250118_143052.json"
  }
}
```

#### 11. New Session

```http
POST /api/v1/camera/new-session
```

**Response:**
```json
{
  "success": true,
  "message": "New session started",
  "summary": {
    "unique_faces_count": 0,
    "unique_faces": [],
    "encounters": {},
    "log_file": "logs/session_20250118_150000.json"
  }
}
```

#### 12. Get Session Summary

```http
GET /api/v1/camera/summary
```

**Response:**
```json
{
  "unique_faces_count": 3,
  "unique_faces": ["John Doe", "Jane Smith", "Bob Johnson"],
  "encounters": {
    "John Doe": 45,
    "Jane Smith": 23,
    "Bob Johnson": 12
  },
  "log_file": "logs/session_20250118_143052.json"
}
```

#### 13. WebSocket Camera Feed

```
WebSocket: ws://localhost:8000/api/v1/ws/camera
```

**Message Format (Received):**
```json
{
  "type": "frame",
  "frame": "base64_encoded_jpeg_image",
  "faces": [
    {
      "name": "John Doe",
      "confidence": 0.87,
      "location": {"top": 100, "right": 250, "bottom": 300, "left": 150}
    }
  ],
  "summary": {
    "unique_faces_count": 3,
    "unique_faces": ["John Doe", "Jane Smith", "Bob Johnson"],
    "encounters": {"John Doe": 45}
  }
}
```

---

## Python Client Usage

### Basic Client

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Add a known face
def add_face(image_path, name):
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/faces/add",
            files={"file": f},
            data={"name": name}
        )
    return response.json()

# Recognize faces
def recognize_faces(image_path):
    with open(image_path, "rb") as f:
        response = requests.post(
            f"{API_URL}/recognize",
            files={"file": f}
        )
    return response.json()

# List known faces
def list_faces():
    response = requests.get(f"{API_URL}/faces")
    return response.json()

# Usage
result = add_face("john_doe.jpg", "John Doe")
print(result)

result = recognize_faces("group_photo.jpg")
for face in result["faces"]:
    print(f"Found: {face['name']} ({face['confidence']:.2f})")
```

### Full Client Example

See `examples/client_example.py` for a complete Python client with all API methods.

---

## Advanced Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# API Settings
APP_NAME="Face Recognition API"
APP_VERSION="1.0.0"
API_PREFIX="/api/v1"
DEBUG=false

# Server Settings
HOST=0.0.0.0
PORT=8000

# File Upload Settings
UPLOAD_DIR=uploads
KNOWN_FACES_DIR=known_faces
MAX_UPLOAD_SIZE=10485760
ALLOWED_EXTENSIONS=".jpg,.jpeg,.png,.bmp"

# Face Recognition Settings
FACE_DETECTION_MODEL=hog
NUM_JITTERS=1
TOLERANCE=0.6
```

### Configuration Options

#### FACE_DETECTION_MODEL

- **hog** (default): Histogram of Oriented Gradients
  - Faster (CPU-friendly)
  - Good accuracy for frontal faces
  - Recommended for real-time applications

- **cnn**: Convolutional Neural Network
  - More accurate
  - Detects faces at various angles
  - Requires GPU for good performance
  - Slower on CPU

#### TOLERANCE

Controls how strict face matching is:

- **0.4 - 0.5**: Very strict (fewer false positives, may miss some matches)
- **0.6** (default): Balanced
- **0.7 - 0.8**: Lenient (more matches, more false positives)

#### NUM_JITTERS

Number of times to re-sample when calculating face encoding:

- **1** (default): Fast, good for real-time
- **5-10**: More accurate, slower
- **100**: Maximum accuracy, very slow

### Performance Tuning

#### For Real-Time Processing

```env
FACE_DETECTION_MODEL=hog
NUM_JITTERS=1
TOLERANCE=0.6
```

Edit `app/core/video_processor.py`:
```python
self.frame_skip = 3  # Process every 3rd frame (increase for better performance)
```

#### For Maximum Accuracy

```env
FACE_DETECTION_MODEL=cnn
NUM_JITTERS=10
TOLERANCE=0.5
```

#### For Low-End Hardware

```env
FACE_DETECTION_MODEL=hog
NUM_JITTERS=1
TOLERANCE=0.6
```

Edit `app/core/video_processor.py`:
```python
self.frame_skip = 5  # Process every 5th frame
```

---

## Troubleshooting

### Common Issues

#### 1. Camera Not Working

**Problem**: Camera doesn't start in Testing Stand

**Solutions**:
- Check camera permissions in your browser
- Verify camera index in `app/core/video_processor.py`:
  ```python
  video_processor = VideoStreamProcessor(camera_index=0)  # Try 0, 1, 2, etc.
  ```
- Test camera with:
  ```bash
  python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed')"
  ```

#### 2. Installation Errors

**Problem**: `dlib` installation fails

**Solutions**:
- Install CMake: `pip install cmake`
- On Ubuntu/Debian: `sudo apt-get install cmake build-essential`
- On macOS: `brew install cmake`
- On Windows: Install Visual Studio Build Tools

#### 3. Face Not Recognized

**Problem**: Known faces show as "Unknown"

**Solutions**:
- Increase tolerance: Set `TOLERANCE=0.7` in `.env`
- Add multiple photos of the person from different angles
- Ensure good lighting in both training and test images
- Use frontal face photos for training

#### 4. Performance Issues

**Problem**: Slow processing or high CPU usage

**Solutions**:
- Increase `frame_skip` in `video_processor.py`
- Use `FACE_DETECTION_MODEL=hog` instead of `cnn`
- Reduce video resolution
- Decrease `NUM_JITTERS`

#### 5. WebSocket Connection Fails

**Problem**: Testing Stand shows "WebSocket error"

**Solutions**:
- Check if server is running: `curl http://localhost:8000/api/v1/health`
- Verify WebSocket support: `pip install websockets`
- Check firewall settings
- Try different browser (Chrome/Firefox recommended)

### Debug Mode

Enable debug mode for detailed logs:

```env
DEBUG=true
```

Then run:
```bash
python main.py
```

You'll see detailed logs in the console.

---

## Best Practices

### 1. Training Data

- **Quality**: Use high-resolution, well-lit images
- **Variety**: Add multiple photos per person from different angles
- **Single Face**: Ensure training images contain only one face
- **Consistency**: Use similar lighting conditions for training and testing

### 2. Security

- **Production**: Set `DEBUG=false`
- **CORS**: Configure `allow_origins` in `main.py` for production
- **HTTPS**: Use HTTPS in production environments
- **Authentication**: Add authentication for production deployments
- **File Upload**: Validate and scan uploaded files
- **Rate Limiting**: Implement rate limiting for public APIs

### 3. Performance

- **Batch Processing**: Process multiple images in batches when possible
- **Cache**: Cache face encodings instead of recomputing
- **GPU**: Use CNN model with GPU for better accuracy and performance
- **Frame Skip**: Adjust frame_skip based on your hardware

### 4. Logging

- **Session Management**: Start new sessions for different events
- **Export Logs**: Regularly export and archive logs
- **Privacy**: Be mindful of privacy regulations when storing face data
- **Cleanup**: Implement log rotation to manage disk space

### 5. Face Database

- **Regular Updates**: Keep face encodings updated
- **Backup**: Regularly backup `known_faces/encodings.pkl`
- **Remove Duplicates**: Periodically check for duplicate entries
- **Version Control**: Track changes to your face database

---

## Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **GitHub Repository**: [Your Repository URL]
- **face_recognition Library**: https://github.com/ageitgey/face_recognition
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

---

## Support

For issues, questions, or feature requests:
1. Check this guide and the troubleshooting section
2. Review the API documentation at `/docs`
3. Open an issue on the GitHub repository

---

## License

This project is open-source and available under the MIT License.
