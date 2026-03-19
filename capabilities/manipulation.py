"""
Manipulation Controller
High-level arm and gripper control for pick-and-place operations
"""

import time
import logging
from typing import Optional, Tuple, Callable

logger = logging.getLogger(__name__)


class ManipulationController:
    """
    High-level manipulation control with vision integration
    """
    
    def __init__(self, arm, vision=None):
        """
        Initialize manipulation controller
        
        Args:
            arm: Arm instance
            vision: Optional VisionSystem instance
        """
        self.arm = arm
        self.vision = vision
        
        # Calibration offsets (camera to gripper)
        self.camera_offset_x = 0  # mm
        self.camera_offset_y = 50  # mm (camera ahead of gripper)
        
        logger.info("Manipulation controller initialized")
        
    # ===== Pick and Place =====
    
    def pick_object(self, x: float, y: float, z: float = 20,
                   approach_height: float = 50) -> bool:
        """
        Pick object at position
        
        Args:
            x, y, z: Object position (mm)
            approach_height: Height to approach from
            
        Returns:
            True if successful
        """
        logger.info(f"Picking object at ({x}, {y}, {z})")
        return self.arm.pick_sequence(x, y, z, approach_height)
        
    def place_object(self, x: float, y: float, z: float = 20,
                    approach_height: float = 50) -> bool:
        """
        Place object at position
        
        Args:
            x, y, z: Target position (mm)
            approach_height: Height to approach from
            
        Returns:
            True if successful
        """
        logger.info(f"Placing object at ({x}, {y}, {z})")
        return self.arm.place_sequence(x, y, z, approach_height)
        
    def transfer_object(self, from_pos: Tuple[float, float, float],
                       to_pos: Tuple[float, float, float]) -> bool:
        """
        Transfer object from one position to another
        
        Args:
            from_pos: (x, y, z) pickup position
            to_pos: (x, y, z) place position
            
        Returns:
            True if successful
        """
        x1, y1, z1 = from_pos
        x2, y2, z2 = to_pos
        
        # Pick
        if not self.pick_object(x1, y1, z1):
            return False
            
        time.sleep(0.3)
        
        # Move to carry position
        self.arm.move_to_named('carry', duration=1.0)
        time.sleep(0.5)
        
        # Place
        if not self.place_object(x2, y2, z2):
            return False
            
        return True
        
    # ===== Visual Manipulation =====
    
    def pick_by_color(self, color: str, camera_frame=None) -> bool:
        """
        Pick object by color detection
        
        Args:
            color: Color name ('red', 'blue', 'green', 'yellow')
            camera_frame: Optional pre-captured frame
            
        Returns:
            True if successful
        """
        if self.vision is None:
            logger.error("Vision system not available")
            return False
            
        # Get frame
        if camera_frame is None:
            camera_frame = self.vision.camera.read()
            if camera_frame is None:
                logger.error("Failed to read camera frame")
                return False
                
        # Detect color blob
        detection = self.vision.detect_color(camera_frame, color, min_area=500)
        
        if detection is None:
            logger.warning(f"No {color} object detected")
            return False
            
        x_px, y_px, radius = detection
        logger.info(f"Detected {color} object at pixel ({x_px}, {y_px})")
        
        # Convert pixel coordinates to world coordinates
        x, y = self._pixel_to_world(x_px, y_px, camera_frame.shape)
        
        # Pick object
        return self.pick_object(x, y, z=20)
        
    def pick_by_apriltag(self, tag_id: int, camera_frame=None,
                        offset_x: float = 0, offset_y: float = 0) -> bool:
        """
        Pick object at AprilTag location
        
        Args:
            tag_id: AprilTag ID
            camera_frame: Optional pre-captured frame
            offset_x, offset_y: Offset from tag center (mm)
            
        Returns:
            True if successful
        """
        if self.vision is None:
            logger.error("Vision system not available")
            return False
            
        # Get frame
        if camera_frame is None:
            camera_frame = self.vision.camera.read()
            if camera_frame is None:
                logger.error("Failed to read camera frame")
                return False
                
        # Detect AprilTag
        detection = self.vision.find_apriltag(camera_frame, tag_id)
        
        if detection is None:
            logger.warning(f"AprilTag {tag_id} not detected")
            return False
            
        x_px, y_px = detection.center
        logger.info(f"Detected AprilTag {tag_id} at pixel ({x_px}, {y_px})")
        
        # Convert to world coordinates
        x, y = self._pixel_to_world(x_px, y_px, camera_frame.shape)
        
        # Apply offset
        x += offset_x
        y += offset_y
        
        # Pick object
        return self.pick_object(x, y, z=20)
        
    def pick_by_yolo(self, class_name: str, camera_frame=None) -> bool:
        """
        Pick object detected by YOLO
        
        Args:
            class_name: Object class name
            camera_frame: Optional pre-captured frame
            
        Returns:
            True if successful
        """
        if self.vision is None:
            logger.error("Vision system not available")
            return False
            
        # Get frame
        if camera_frame is None:
            camera_frame = self.vision.camera.read()
            if camera_frame is None:
                logger.error("Failed to read camera frame")
                return False
                
        # Detect object
        detection = self.vision.find_object(camera_frame, class_name)
        
        if detection is None:
            logger.warning(f"No {class_name} object detected")
            return False
            
        x_px, y_px = detection.center
        logger.info(f"Detected {class_name} at pixel ({x_px}, {y_px})")
        
        # Convert to world coordinates
        x, y = self._pixel_to_world(x_px, y_px, camera_frame.shape)
        
        # Pick object
        return self.pick_object(x, y, z=20)
        
    # ===== Sorting Operations =====
    
    def sort_by_color(self, colors: list, positions: dict,
                     duration: float = 60.0) -> dict:
        """
        Sort objects by color to designated positions
        
        Args:
            colors: List of colors to sort
            positions: Dict mapping color -> (x, y, z) position
            duration: Maximum sorting duration
            
        Returns:
            Dict with counts per color
        """
        if self.vision is None:
            logger.error("Vision system not available")
            return {}
            
        counts = {color: 0 for color in colors}
        start = time.time()
        
        while time.time() - start < duration:
            # Scan for objects
            frame = self.vision.camera.read()
            if frame is None:
                continue
                
            # Try each color
            for color in colors:
                if color not in positions:
                    continue
                    
                detection = self.vision.detect_color(frame, color, min_area=500)
                
                if detection is None:
                    continue
                    
                # Found object, pick and place
                x_px, y_px, _ = detection
                x_pick, y_pick = self._pixel_to_world(x_px, y_px, frame.shape)
                
                if self.pick_object(x_pick, y_pick, z=20):
                    time.sleep(0.5)
                    x_place, y_place, z_place = positions[color]
                    if self.place_object(x_place, y_place, z_place):
                        counts[color] += 1
                        logger.info(f"Sorted {color} object ({counts[color]} total)")
                    time.sleep(0.5)
                    
            time.sleep(0.5)
            
        # Return to home
        self.arm.home()
        
        return counts
        
    # ===== Calibration =====
    
    def calibrate_camera_offset(self, known_x: float, known_y: float,
                               camera_frame=None):
        """
        Calibrate camera-to-gripper offset using known position
        
        Args:
            known_x, known_y: Known object position (mm)
            camera_frame: Optional frame with object visible
        """
        if camera_frame is None or self.vision is None:
            logger.error("Camera frame and vision required for calibration")
            return
            
        # User should place arm at known position and capture frame
        # This is a simplified calibration
        logger.info(f"Calibrating with known position: ({known_x}, {known_y})")
        
        # Detect object in frame (assuming AprilTag or color)
        # Calculate offset and store
        # This is a placeholder - real calibration more complex
        
    def _pixel_to_world(self, px: float, py: float, 
                       frame_shape: tuple) -> Tuple[float, float]:
        """
        Convert pixel coordinates to world coordinates
        
        Args:
            px, py: Pixel coordinates
            frame_shape: (height, width, channels)
            
        Returns:
            (x, y) in mm
        """
        height, width = frame_shape[:2]
        
        # Simple linear mapping (should be calibrated)
        # Assuming camera sees ~400mm x 300mm at typical height
        x = (px - width / 2) * (400 / width)
        y = (height / 2 - py) * (300 / height) + self.camera_offset_y
        
        return x, y
        
    # ===== Gestures and Sequences =====
    
    def wave(self):
        """Friendly wave gesture"""
        self.arm.move_to(50, 150, 150, duration=1.0)
        time.sleep(0.3)
        
        for _ in range(3):
            self.arm.move_to(80, 150, 150, duration=0.3)
            time.sleep(0.1)
            self.arm.move_to(50, 150, 150, duration=0.3)
            time.sleep(0.1)
            
        self.arm.home()
        
    def dance(self):
        """Fun dance sequence"""
        positions = [
            (0, 150, 100),
            (40, 150, 120),
            (-40, 150, 120),
            (0, 180, 80),
            (0, 120, 140),
        ]
        
        for _ in range(2):
            for pos in positions:
                self.arm.move_to(*pos, duration=0.5)
                time.sleep(0.2)
                
        self.arm.home()
