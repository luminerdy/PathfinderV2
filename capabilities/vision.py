"""
Vision System
AprilTag detection, YOLO object detection, and color tracking
"""

import cv2
import numpy as np
import logging
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

try:
    from dt_apriltags import Detector as AprilTagDetector
except ImportError:
    try:
        from pupil_apriltags import Detector as AprilTagDetector
    except ImportError:
        AprilTagDetector = None

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

logger = logging.getLogger(__name__)


@dataclass
class AprilTagDetection:
    """AprilTag detection result"""
    tag_id: int
    center: Tuple[float, float]
    corners: np.ndarray
    distance: Optional[float] = None
    angle: Optional[float] = None
    
    
@dataclass
class ObjectDetection:
    """YOLO object detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    center: Tuple[int, int]
    

class VisionSystem:
    """
    Unified vision system with AprilTag and YOLO detection
    """
    
    def __init__(self, camera, config: Dict):
        """
        Initialize vision system
        
        Args:
            camera: Camera instance
            config: Vision configuration dict
        """
        self.camera = camera
        self.config = config
        
        # AprilTag detector
        self._apriltag_detector = None
        if AprilTagDetector:
            try:
                at_config = config.get('apriltag', {})
                self._apriltag_detector = AprilTagDetector(
                    families=at_config.get('family', 'tag36h11'),
                    nthreads=2,
                    quad_decimate=at_config.get('quad_decimate', 2.0),
                    quad_sigma=at_config.get('quad_sigma', 0.0),
                    decode_sharpening=at_config.get('decode_sharpening', 0.25)
                )
                logger.info("AprilTag detector initialized")
            except Exception as e:
                logger.error(f"Failed to initialize AprilTag detector: {e}")
        else:
            logger.warning("AprilTag library not available")
            
        # YOLO detector
        self._yolo = None
        if YOLO is not None:
            try:
                yolo_config = config.get('yolo', {})
                model_path = yolo_config.get('model', 'yolo11n.pt')
                self._yolo = YOLO(model_path)
                self._yolo_conf = yolo_config.get('confidence', 0.5)
                self._yolo_iou = yolo_config.get('iou_threshold', 0.45)
                logger.info(f"YOLO detector initialized: {model_path}")
            except Exception as e:
                logger.error(f"Failed to initialize YOLO: {e}")
        else:
            logger.warning("YOLO not available (ultralytics not installed)")
            
        # Color tracking ranges (HSV)
        self._color_ranges = {
            'red': [(0, 100, 100), (10, 255, 255)],
            'red2': [(170, 100, 100), (180, 255, 255)],  # Red wraps around
            'blue': [(100, 100, 100), (130, 255, 255)],
            'green': [(40, 50, 50), (80, 255, 255)],
            'yellow': [(20, 100, 100), (30, 255, 255)],
        }
        
    # ===== AprilTag Detection =====
    
    def detect_apriltags(self, frame: np.ndarray, 
                        gray: bool = True) -> List[AprilTagDetection]:
        """
        Detect AprilTags in frame
        
        Args:
            frame: Input frame (BGR or grayscale)
            gray: Convert to grayscale if needed
            
        Returns:
            List of AprilTagDetection objects
        """
        if self._apriltag_detector is None:
            return []
            
        try:
            # Convert to grayscale if needed
            if gray and len(frame.shape) == 3:
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                gray_frame = frame
                
            # Detect tags
            detections = self._apriltag_detector.detect(gray_frame)
            
            # Convert to our format
            results = []
            for det in detections:
                center = tuple(det.center.astype(int))
                
                result = AprilTagDetection(
                    tag_id=det.tag_id,
                    center=center,
                    corners=det.corners
                )
                results.append(result)
                
            return results
            
        except Exception as e:
            logger.error(f"AprilTag detection error: {e}")
            return []
            
    def find_apriltag(self, frame: np.ndarray, tag_id: int) -> Optional[AprilTagDetection]:
        """
        Find specific AprilTag
        
        Args:
            frame: Input frame
            tag_id: Tag ID to find
            
        Returns:
            AprilTagDetection if found, None otherwise
        """
        detections = self.detect_apriltags(frame)
        for det in detections:
            if det.tag_id == tag_id:
                return det
        return None
        
    def draw_apriltags(self, frame: np.ndarray, 
                      detections: List[AprilTagDetection]) -> np.ndarray:
        """
        Draw AprilTag detections on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        for det in detections:
            # Draw corners
            corners = det.corners.astype(int)
            for i in range(4):
                pt1 = tuple(corners[i])
                pt2 = tuple(corners[(i + 1) % 4])
                cv2.line(output, pt1, pt2, (0, 255, 0), 2)
                
            # Draw center
            center = tuple(map(int, det.center))
            cv2.circle(output, center, 5, (0, 0, 255), -1)
            
            # Draw ID
            cv2.putText(output, f"ID: {det.tag_id}", 
                       (center[0] + 10, center[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                       
        return output
        
    # ===== YOLO Object Detection =====
    
    def detect_objects(self, frame: np.ndarray, 
                      classes: Optional[List[int]] = None) -> List[ObjectDetection]:
        """
        Detect objects using YOLO
        
        Args:
            frame: Input frame
            classes: Optional list of class IDs to detect
            
        Returns:
            List of ObjectDetection objects
        """
        if self._yolo is None:
            return []
            
        try:
            # Run inference
            results = self._yolo(frame, conf=self._yolo_conf, 
                               iou=self._yolo_iou, classes=classes, 
                               verbose=False)
                               
            detections = []
            
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract box data
                    x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    cls_name = result.names[cls_id]
                    
                    # Calculate center
                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2
                    
                    det = ObjectDetection(
                        class_id=cls_id,
                        class_name=cls_name,
                        confidence=conf,
                        bbox=(x1, y1, x2, y2),
                        center=(center_x, center_y)
                    )
                    detections.append(det)
                    
            return detections
            
        except Exception as e:
            logger.error(f"YOLO detection error: {e}")
            return []
            
    def find_object(self, frame: np.ndarray, class_name: str) -> Optional[ObjectDetection]:
        """
        Find specific object by class name
        
        Args:
            frame: Input frame
            class_name: Object class to find
            
        Returns:
            Closest ObjectDetection if found
        """
        detections = self.detect_objects(frame)
        
        # Filter by class name
        matches = [d for d in detections if d.class_name == class_name]
        
        if not matches:
            return None
            
        # Return closest to center
        frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
        
        def distance_to_center(det):
            dx = det.center[0] - frame_center[0]
            dy = det.center[1] - frame_center[1]
            return dx*dx + dy*dy
            
        return min(matches, key=distance_to_center)
        
    def draw_objects(self, frame: np.ndarray, 
                    detections: List[ObjectDetection]) -> np.ndarray:
        """
        Draw object detections on frame
        
        Args:
            frame: Input frame
            detections: List of detections
            
        Returns:
            Frame with drawn detections
        """
        output = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det.bbox
            
            # Draw bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            cv2.putText(output, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                       
            # Draw center
            cv2.circle(output, det.center, 3, (0, 0, 255), -1)
            
        return output
        
    # ===== Color Tracking =====
    
    def detect_color(self, frame: np.ndarray, color: str, 
                    min_area: int = 500) -> Optional[Tuple[int, int, int]]:
        """
        Detect color blob in frame
        
        Args:
            frame: Input frame (BGR)
            color: Color name ('red', 'blue', 'green', 'yellow')
            min_area: Minimum blob area
            
        Returns:
            (x, y, radius) of largest blob, or None
        """
        if color not in self._color_ranges:
            logger.warning(f"Unknown color: {color}")
            return None
            
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Create mask
            lower, upper = self._color_ranges[color]
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Handle red wrap-around
            if color == 'red' and 'red2' in self._color_ranges:
                lower2, upper2 = self._color_ranges['red2']
                mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
                mask = cv2.bitwise_or(mask, mask2)
                
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                          cv2.CHAIN_APPROX_SIMPLE)
                                          
            if not contours:
                return None
                
            # Find largest contour
            largest = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest) < min_area:
                return None
                
            # Get enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(largest)
            
            return (int(x), int(y), int(radius))
            
        except Exception as e:
            logger.error(f"Color detection error: {e}")
            return None
            
    # ===== Utility Methods =====
    
    def annotate_frame(self, frame: np.ndarray, 
                      show_apriltags: bool = True,
                      show_objects: bool = True) -> np.ndarray:
        """
        Annotate frame with all detections
        
        Args:
            frame: Input frame
            show_apriltags: Draw AprilTag detections
            show_objects: Draw object detections
            
        Returns:
            Annotated frame
        """
        output = frame.copy()
        
        if show_apriltags:
            tags = self.detect_apriltags(frame)
            output = self.draw_apriltags(output, tags)
            
        if show_objects:
            objects = self.detect_objects(frame)
            output = self.draw_objects(output, objects)
            
        return output
