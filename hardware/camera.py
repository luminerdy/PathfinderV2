"""
Camera Interface
Provides video capture and streaming capabilities
"""

import cv2
import time
import logging
import threading
import numpy as np
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class Camera:
    """
    Camera capture and streaming interface
    """
    
    def __init__(self, device: int = 0, width: int = 640, height: int = 480, 
                 fps: int = 30):
        """
        Initialize camera
        
        Args:
            device: Camera device index
            width: Frame width
            height: Frame height
            fps: Target frames per second
        """
        self.device = device
        self.width = width
        self.height = height
        self.fps = fps
        
        self._cap = None
        self._frame = None
        self._running = False
        self._lock = threading.Lock()
        self._thread = None
        
        logger.info(f"Camera configured: {width}x{height}@{fps}fps")
        
    def open(self) -> bool:
        """
        Open camera and start capture
        
        Returns:
            True if successful
        """
        try:
            self._cap = cv2.VideoCapture(self.device)
            
            if not self._cap.isOpened():
                logger.error("Failed to open camera")
                return False
                
            # Configure camera
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self._cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Start capture thread
            self._running = True
            self._thread = threading.Thread(target=self._capture_loop, daemon=True)
            self._thread.start()
            
            logger.info("Camera opened")
            return True
            
        except Exception as e:
            logger.error(f"Error opening camera: {e}")
            return False
            
    def _capture_loop(self):
        """Background capture thread"""
        while self._running:
            ret, frame = self._cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
            else:
                logger.warning("Failed to read frame")
                time.sleep(0.1)
                
    def read(self) -> Optional[np.ndarray]:
        """
        Read current frame
        
        Returns:
            Frame as numpy array, or None if unavailable
        """
        with self._lock:
            if self._frame is not None:
                return self._frame.copy()
        return None
        
    def read_with_timestamp(self) -> Tuple[Optional[np.ndarray], float]:
        """
        Read frame with timestamp
        
        Returns:
            (frame, timestamp) tuple
        """
        frame = self.read()
        timestamp = time.time()
        return frame, timestamp
        
    def close(self):
        """Close camera and stop capture"""
        self._running = False
        
        if self._thread:
            self._thread.join(timeout=2.0)
            
        if self._cap:
            self._cap.release()
            
        logger.info("Camera closed")
        
    # ===== Utilities =====
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current resolution"""
        return (self.width, self.height)
        
    def is_opened(self) -> bool:
        """Check if camera is open"""
        return self._cap is not None and self._cap.isOpened()
        
    def set_brightness(self, value: float):
        """Set brightness (0-1)"""
        if self._cap:
            self._cap.set(cv2.CAP_PROP_BRIGHTNESS, value)
            
    def set_contrast(self, value: float):
        """Set contrast (0-1)"""
        if self._cap:
            self._cap.set(cv2.CAP_PROP_CONTRAST, value)
            
    def set_saturation(self, value: float):
        """Set saturation (0-1)"""
        if self._cap:
            self._cap.set(cv2.CAP_PROP_SATURATION, value)
            
    def set_exposure(self, value: float):
        """Set exposure (-1 for auto, 0-1 for manual)"""
        if self._cap:
            if value < 0:
                self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.75)  # Auto
            else:
                self._cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Manual
                self._cap.set(cv2.CAP_PROP_EXPOSURE, value)
                
    # ===== Context Manager =====
    
    def __enter__(self):
        self.open()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
