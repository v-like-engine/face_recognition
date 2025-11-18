"""
Real-time video streaming and WebSocket endpoints
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
import cv2
import asyncio
import json
import base64
import numpy as np
from typing import List

from app.core.video_processor import video_processor

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@router.websocket("/ws/camera")
async def websocket_camera_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time camera feed with face recognition

    Sends video frames and face recognition results to connected clients
    """
    await manager.connect(websocket)

    try:
        # Start camera if not already running
        if not video_processor.is_running:
            if not video_processor.start_camera():
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to start camera"
                })
                return

        while True:
            # Read frame from camera
            frame = video_processor.read_frame()

            if frame is None:
                await websocket.send_json({
                    "type": "error",
                    "message": "Failed to read frame"
                })
                break

            # Process frame for face recognition
            processed_frame, faces_data = video_processor.process_frame(frame)

            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = base64.b64encode(buffer).decode('utf-8')

            # Get session summary
            summary = video_processor.get_session_summary()

            # Send data to client
            await websocket.send_json({
                "type": "frame",
                "frame": frame_bytes,
                "faces": faces_data,
                "summary": summary
            })

            # Small delay to control frame rate (~30 FPS)
            await asyncio.sleep(0.033)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.post("/camera/start")
async def start_camera():
    """Start the camera for streaming"""
    if video_processor.is_running:
        return {
            "success": True,
            "message": "Camera is already running"
        }

    if video_processor.start_camera():
        return {
            "success": True,
            "message": "Camera started successfully"
        }
    else:
        raise HTTPException(status_code=500, detail="Failed to start camera")


@router.post("/camera/stop")
async def stop_camera():
    """Stop the camera"""
    video_processor.stop_camera()
    return {
        "success": True,
        "message": "Camera stopped"
    }


@router.get("/camera/status")
async def camera_status():
    """Get camera status"""
    return {
        "is_running": video_processor.is_running,
        "summary": video_processor.get_session_summary() if video_processor.is_running else None
    }


@router.post("/camera/new-session")
async def new_session():
    """Start a new recognition session"""
    video_processor.logger.start_new_session()
    return {
        "success": True,
        "message": "New session started",
        "summary": video_processor.get_session_summary()
    }


@router.get("/camera/summary")
async def get_summary():
    """Get current session summary"""
    return video_processor.get_session_summary()


@router.post("/camera/process-image")
async def process_single_image(image_data: str):
    """
    Process a single base64-encoded image for face recognition

    Args:
        image_data: Base64-encoded image string

    Returns:
        Face recognition results
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1] if ',' in image_data else image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        # Process frame
        processed_frame, faces_data = video_processor.process_frame(frame, perform_recognition=True)

        # Encode processed frame
        _, buffer = cv2.imencode('.jpg', processed_frame)
        processed_frame_b64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "success": True,
            "faces": faces_data,
            "processed_image": f"data:image/jpeg;base64,{processed_frame_b64}",
            "summary": video_processor.get_session_summary()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
