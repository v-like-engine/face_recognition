# Face Recognition API

A powerful and easy-to-use face recognition REST API built with Python, FastAPI, and the `face_recognition` library. This tool provides face detection, recognition, and management capabilities with a clean API interface.

## Features

- **Face Detection** - Detect and locate faces in images
- **Face Recognition** - Identify known faces in images
- **Face Management** - Add, remove, and list known faces
- **Facial Landmarks** - Extract detailed facial features (eyes, nose, mouth, etc.)
- **RESTful API** - Easy integration with any application
- **Interactive Documentation** - Auto-generated API docs with Swagger UI
- **Docker Support** - Easy deployment with Docker and Docker Compose
- **Configurable** - Adjustable tolerance, detection models, and more

## Technology Stack

- **Python 3.10+**
- **FastAPI** - Modern, fast web framework
- **face_recognition** - Face detection and recognition (built on dlib)
- **OpenCV** - Image processing
- **Pillow** - Image manipulation
- **Uvicorn** - ASGI server

## Installation

### Option 1: Local Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd face_recognition
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the application** (optional)
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or use uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Option 2: Docker

1. **Using Docker Compose** (recommended)
   ```bash
   docker-compose up -d
   ```

2. **Using Docker directly**
   ```bash
   docker build -t face-recognition-api .
   docker run -p 8000:8000 -v $(pwd)/uploads:/app/uploads -v $(pwd)/known_faces:/app/known_faces face-recognition-api
   ```

## API Documentation

Once the server is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```
GET /api/v1/health
```
Check API status and number of known faces loaded.

### Recognize Faces
```
POST /api/v1/recognize
```
Recognize faces in an uploaded image.

**Parameters:**
- `file` (form-data): Image file
- `tolerance` (optional): Face matching tolerance (0.0-1.0, default: 0.6)

**Response:**
```json
{
  "success": true,
  "message": "Detected 2 face(s)",
  "faces_found": 2,
  "faces": [
    {
      "name": "John Doe",
      "confidence": 0.85,
      "location": {
        "top": 100,
        "right": 250,
        "bottom": 300,
        "left": 150
      }
    }
  ]
}
```

### Add Known Face
```
POST /api/v1/faces/add
```
Add a known face to the database.

**Parameters:**
- `file` (form-data): Image file with a single face
- `name` (form-data): Name to associate with the face

**Response:**
```json
{
  "success": true,
  "message": "Successfully added face for John Doe",
  "name": "John Doe",
  "face_location": [100, 250, 300, 150]
}
```

### Remove Known Face
```
DELETE /api/v1/faces/{name}
```
Remove a known face from the database.

### List Known Faces
```
GET /api/v1/faces
```
List all known faces in the database.

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

### Detect Faces
```
POST /api/v1/detect
```
Detect faces in an image without recognition.

### Get Facial Landmarks
```
POST /api/v1/landmarks
```
Get detailed facial landmarks (eyes, nose, mouth, etc.).

## Usage Examples

### cURL

**Add a known face:**
```bash
curl -X POST "http://localhost:8000/api/v1/faces/add" \
  -F "file=@/path/to/photo.jpg" \
  -F "name=John Doe"
```

**Recognize faces:**
```bash
curl -X POST "http://localhost:8000/api/v1/recognize" \
  -F "file=@/path/to/group_photo.jpg"
```

**List known faces:**
```bash
curl -X GET "http://localhost:8000/api/v1/faces"
```

**Remove a known face:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/faces/John%20Doe"
```

### Python Client

See `examples/client_example.py` for a complete Python client example:

```python
import requests

API_URL = "http://localhost:8000/api/v1"

# Add a known face
with open("john_doe.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/faces/add",
        files={"file": f},
        data={"name": "John Doe"}
    )
    print(response.json())

# Recognize faces
with open("group_photo.jpg", "rb") as f:
    response = requests.post(
        f"{API_URL}/recognize",
        files={"file": f}
    )
    result = response.json()
    for face in result["faces"]:
        print(f"Found: {face['name']} (confidence: {face['confidence']:.2f})")
```

### JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const API_URL = 'http://localhost:8000/api/v1';

// Add a known face
async function addFace(imagePath, name) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));
  form.append('name', name);

  const response = await axios.post(`${API_URL}/faces/add`, form, {
    headers: form.getHeaders()
  });

  return response.data;
}

// Recognize faces
async function recognizeFaces(imagePath) {
  const form = new FormData();
  form.append('file', fs.createReadStream(imagePath));

  const response = await axios.post(`${API_URL}/recognize`, form, {
    headers: form.getHeaders()
  });

  return response.data;
}
```

## Configuration

Create a `.env` file based on `.env.example` to customize settings:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | "Face Recognition API" |
| `DEBUG` | Enable debug mode | false |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |
| `FACE_DETECTION_MODEL` | Detection model (hog/cnn) | hog |
| `TOLERANCE` | Face matching tolerance | 0.6 |
| `NUM_JITTERS` | Face encoding samples | 1 |
| `MAX_UPLOAD_SIZE` | Max file size in bytes | 10485760 |

### Face Detection Models

- **hog** (default): Faster, works on CPU, good for most cases
- **cnn**: More accurate, requires GPU, slower on CPU

### Tolerance Settings

- Lower values (0.4-0.5): More strict, fewer false positives
- Default (0.6): Balanced
- Higher values (0.7-0.8): More lenient, more false positives

## Project Structure

```
face_recognition/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── face_processor.py  # Core face recognition logic
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── utils/
│   │   ├── __init__.py
│   │   └── file_utils.py      # File handling utilities
│   └── __init__.py
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration settings
├── examples/
│   └── client_example.py      # Python client example
├── known_faces/               # Stored face encodings
├── uploads/                   # Temporary upload directory
├── .env.example               # Environment variables template
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── main.py                    # Application entry point
├── README.md
└── requirements.txt
```

## How It Works

1. **Face Detection**: Uses HOG (Histogram of Oriented Gradients) or CNN (Convolutional Neural Network) to locate faces in images
2. **Face Encoding**: Converts detected faces into 128-dimensional vectors
3. **Face Recognition**: Compares face encodings using Euclidean distance
4. **Storage**: Stores known face encodings in a pickle file for persistence

## Performance Tips

- Use `hog` model for faster processing on CPU
- Use `cnn` model for better accuracy (requires GPU)
- Lower `num_jitters` for faster encoding (less accurate)
- Higher `num_jitters` for better accuracy (slower)
- Adjust `tolerance` based on your use case

## Limitations

- Works best with frontal face images
- Requires good lighting conditions
- Performance depends on image quality
- May struggle with very similar-looking people

## Security Considerations

- Implement authentication for production use
- Validate and sanitize file uploads
- Set appropriate CORS policies
- Use HTTPS in production
- Limit file upload sizes
- Implement rate limiting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the MIT License.

## Acknowledgments

- Built with [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Uses [dlib](http://dlib.net/) for face detection and recognition

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.
