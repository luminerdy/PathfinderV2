"""
Camera — Unified Camera Access

Wraps cv2.VideoCapture with optional calibration and frame flushing.

Usage:
    from lib.camera import Camera
    cam = Camera()
    frame = cam.get_frame()       # Clean, flushed frame
    cam.release()
"""

import cv2
import time
import numpy as np
from pathlib import Path


# Default calibration (estimated). Replace with real values from calibration.
DEFAULT_FX = 500
DEFAULT_FY = 500
DEFAULT_CX = 320
DEFAULT_CY = 240


class Camera:
    """
    Camera wrapper with optional calibration and convenience methods.
    
    Handles:
    - Frame buffer flushing (stale frame prevention)
    - Optional lens calibration/undistortion
    - Resolution management
    - Graceful release
    """
    
    def __init__(self, device=0, width=640, height=480, calibration_path=None):
        """
        Initialize camera.
        
        Args:
            device: Video device index (0 = /dev/video0)
            width: Frame width
            height: Frame height
            calibration_path: Path to .npz calibration file (optional)
        """
        self.device = device
        self.width = width
        self.height = height
        self.cap = None
        
        # Calibration data
        self.fx = DEFAULT_FX
        self.fy = DEFAULT_FY
        self.cx = DEFAULT_CX
        self.cy = DEFAULT_CY
        self.mtx = None
        self.dist = None
        self.mapx = None
        self.mapy = None
        self.calibrated = False
        
        # Load calibration if provided
        if calibration_path:
            self._load_calibration(calibration_path)
    
    def _load_calibration(self, path):
        """Load camera calibration from .npz file."""
        try:
            data = np.load(path)
            self.mtx = data['mtx_array']
            self.dist = data['dist_array']
            
            # Extract intrinsics
            self.fx = self.mtx[0, 0]
            self.fy = self.mtx[1, 1]
            self.cx = self.mtx[0, 2]
            self.cy = self.mtx[1, 2]
            
            # Precompute undistortion maps
            newmtx, roi = cv2.getOptimalNewCameraMatrix(
                self.mtx, self.dist, (self.width, self.height), 0,
                (self.width, self.height)
            )
            self.mapx, self.mapy = cv2.initUndistortRectifyMap(
                self.mtx, self.dist, None, newmtx,
                (self.width, self.height), 5
            )
            self.calibrated = True
        except Exception as e:
            print("Camera calibration load failed: %s" % e)
            print("Using default estimated values.")
    
    @property
    def camera_params(self):
        """Return (fx, fy, cx, cy) tuple for AprilTag pose estimation."""
        return (self.fx, self.fy, self.cx, self.cy)
    
    def open(self):
        """Open the camera."""
        if self.cap is not None:
            return
        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        time.sleep(1.5)  # Let auto-exposure settle
    
    def is_open(self):
        """Check if camera is open."""
        return self.cap is not None and self.cap.isOpened()
    
    def get_frame(self, flush=3):
        """
        Get a clean frame (flushes buffer first).
        
        Args:
            flush: Number of frames to discard (prevents stale frames)
        
        Returns:
            BGR frame (numpy array) or None
        """
        if not self.is_open():
            self.open()
        
        # Flush stale frames from buffer
        for _ in range(flush):
            self.cap.read()
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        # Apply undistortion if calibrated
        if self.calibrated and self.mapx is not None:
            frame = cv2.remap(frame, self.mapx, self.mapy, cv2.INTER_LINEAR)
        
        return frame
    
    def get_raw_frame(self):
        """Get a frame without flushing (faster but might be stale)."""
        if not self.is_open():
            self.open()
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def release(self):
        """Release the camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def __del__(self):
        self.release()
