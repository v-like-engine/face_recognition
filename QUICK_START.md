# Quick Start Guide - Face Recognition API

Get up and running in 5 minutes!

## 🚀 Super Quick Start

### Linux/macOS

```bash
# 1. Run the start script
./start.sh

# That's it! The script will:
# - Create virtual environment
# - Install dependencies
# - Create necessary directories
# - Start the server
```

### Windows

```cmd
REM 1. Run the start script
start.bat

REM That's it! The script will do everything for you.
```

### What's Running?

Once started, you'll see:

```
Starting Face Recognition API...

Access points:
  • Testing Stand: http://localhost:8000/testing-stand
  • API Docs:      http://localhost:8000/docs
  • Health Check:  http://localhost:8000/api/v1/health
```

## 📹 Using the Testing Stand (Camera Interface)

### Step 1: Access the Interface

Open your browser and go to:
```
http://localhost:8000/testing-stand
```

### Step 2: Add Known Faces

Before starting the camera, add some faces to recognize:

**Option A: Using Web Interface**
1. Go to http://localhost:8000/docs
2. Find `POST /api/v1/faces/add`
3. Click "Try it out"
4. Upload a photo and enter a name
5. Click "Execute"

**Option B: Using Command Line**
```bash
python scripts/add_face.py path/to/photo.jpg "Person Name"
```

**Option C: Using cURL**
```bash
curl -X POST "http://localhost:8000/api/v1/faces/add" \
  -F "file=@photo.jpg" \
  -F "name=John Doe"
```

### Step 3: Start Camera Recognition

1. On the Testing Stand page, click **"▶ Start Camera"**
2. Allow camera access when prompted by your browser
3. Watch as faces are detected and recognized in real-time!

### Step 4: View Results

The interface shows:

- **Live Video Feed**: With detection boxes around faces
- **Unique Faces**: Count of different people detected
- **Total Detections**: Total number of face detections
- **Identified People**: List of people and encounter counts
- **Detection Log**: Real-time log of detections

### Step 5: Export Your Results

Click **"📥 Export Log"** to download a JSON file with:
- All unique faces detected
- Timestamps of first and last detection
- Confidence scores
- Face locations

## 📊 Example Workflow

### Scenario: Attendance System

```bash
# 1. Start the server
./start.sh

# 2. Add employees to database
python scripts/add_face.py employees/john_doe.jpg "John Doe"
python scripts/add_face.py employees/jane_smith.jpg "Jane Smith"
python scripts/add_face.py employees/bob_jones.jpg "Bob Jones"

# 3. List registered employees
python scripts/list_faces.py

# Output:
# Known Faces Database
# ====================
# Total encodings: 3
# Unique people:   3
#
# People in database:
#   • Bob Jones (1 encoding)
#   • Jane Smith (1 encoding)
#   • John Doe (1 encoding)

# 4. Open Testing Stand
# Go to http://localhost:8000/testing-stand

# 5. Click "Start Camera" and "New Session"

# 6. As employees arrive, they're automatically logged

# 7. At end of day, click "Export Log"
# You get a JSON file with:
# - Who was present
# - When they first appeared
# - How many times they were detected
```

## 🛠️ Utility Scripts

### Add a Face

```bash
python scripts/add_face.py <image_path> <name>

# Example:
python scripts/add_face.py photos/john.jpg "John Doe"
```

### List All Faces

```bash
python scripts/list_faces.py
```

### Recognize Faces in Image

```bash
python scripts/recognize.py <image_path> [tolerance]

# Examples:
python scripts/recognize.py group_photo.jpg
python scripts/recognize.py photo.jpg 0.5  # Strict matching
python scripts/recognize.py photo.jpg 0.7  # Lenient matching
```

## 🎯 Common Tasks

### Test Recognition Before Camera

```bash
# Add a face
python scripts/add_face.py my_photo.jpg "My Name"

# Test with another photo
python scripts/recognize.py test_photo.jpg
```

### Start a New Recognition Session

While on the Testing Stand:
1. Click **"🔄 New Session"**
2. This resets counters and creates a new log file
3. Use this when starting a new event or demo

### Stop and Resume

- **Stop Camera**: Click **"⏹ Stop Camera"**
  - Prints session summary to console
  - Saves log file
  - Stops video feed

- **Resume**: Click **"▶ Start Camera"** again
  - Continues current session
  - Keeps existing face counts

## 📱 API Quick Reference

### Check Server Status

```bash
curl http://localhost:8000/api/v1/health
```

### Add Face

```bash
curl -X POST "http://localhost:8000/api/v1/faces/add" \
  -F "file=@photo.jpg" \
  -F "name=John Doe"
```

### Recognize Faces

```bash
curl -X POST "http://localhost:8000/api/v1/recognize" \
  -F "file=@photo.jpg"
```

### List Known Faces

```bash
curl http://localhost:8000/api/v1/faces
```

### Remove a Face

```bash
curl -X DELETE "http://localhost:8000/api/v1/faces/John%20Doe"
```

## 🎨 Configuration Tips

### Adjust Recognition Sensitivity

Edit `.env` file:

```env
# Strict matching (fewer false positives)
TOLERANCE=0.5

# Balanced (default)
TOLERANCE=0.6

# Lenient (more matches)
TOLERANCE=0.7
```

### Improve Performance

Edit `.env` file:

```env
# Use HOG model (faster, CPU-friendly)
FACE_DETECTION_MODEL=hog

# Reduce encoding quality for speed
NUM_JITTERS=1
```

Edit `app/core/video_processor.py` line 15:

```python
self.frame_skip = 5  # Process every 5th frame (increase for better performance)
```

### Improve Accuracy

Edit `.env` file:

```env
# Use CNN model (requires GPU)
FACE_DETECTION_MODEL=cnn

# Increase encoding quality
NUM_JITTERS=10

# Stricter matching
TOLERANCE=0.5
```

## 🔧 Troubleshooting

### Camera Not Working?

```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'FAILED')"

# Try different camera index
# Edit app/core/video_processor.py line 107:
# video_processor = VideoStreamProcessor(camera_index=1)  # Try 0, 1, 2
```

### Face Not Recognized?

1. Add multiple photos of the person
2. Ensure good lighting
3. Use frontal face photos
4. Increase tolerance to 0.7
5. Check if face is in database: `python scripts/list_faces.py`

### Performance Issues?

1. Increase `frame_skip` to 5 or higher
2. Use `FACE_DETECTION_MODEL=hog`
3. Set `NUM_JITTERS=1`
4. Reduce video resolution in browser

## 📚 Next Steps

- **Full Documentation**: See [USER_GUIDE.md](USER_GUIDE.md)
- **API Reference**: http://localhost:8000/docs
- **Python Client**: See `examples/client_example.py`

## 🎉 That's It!

You're now ready to use the Face Recognition API!

### Need Help?

1. Check [USER_GUIDE.md](USER_GUIDE.md) for detailed documentation
2. Review [README.md](README.md) for technical details
3. Open an issue on GitHub

Enjoy! 🚀
