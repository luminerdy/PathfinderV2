"""
Vision-Guided Pickup Capability
AprilTag-assisted block pickup using inverse kinematics
"""

import time
import math
import logging
import cv2
import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BlockDetection:
    """Detected block information"""
    color: str
    center: Tuple[int, int]  # (x, y) in pixels
    width: int  # pixels
    height: int  # pixels
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float
    angle: float = 0.0  # Rotation angle in degrees (0 = aligned with robot)


@dataclass
class PickupResult:
    """Result of pickup attempt"""
    success: bool
    reason: str
    block_position: Optional[Tuple[float, float, float]]  # (x, y, z) in mm
    time_taken: float
    images: List[str]  # Paths to captured images


class VisualPickupController:
    """
    AprilTag-assisted block pickup using inverse kinematics
    
    Strategy:
    1. Detect block and nearby AprilTag
    2. Use tag as reference to calculate accurate 3D position
    3. Approach block using visual servoing
    4. Use IK to calculate arm pose
    5. Execute pickup sequence
    
    No hardcoded arm positions - all calculated from vision!
    """
    
    def __init__(self, robot):
        """
        Initialize pickup controller
        
        Args:
            robot: Pathfinder robot instance
        """
        self.robot = robot
        self.arm = robot.arm
        self.vision = robot.vision
        self.camera = robot.camera
        self.chassis = robot.chassis
        
        # Pickup parameters (tunable)
        self.block_size_mm = 25  # 1 inch = 25.4mm (use 25 for simplicity)
        self.approach_distance_mm = 150  # Stop when block this far from gripper
        self.pre_grasp_height_mm = 100  # Height above block for pre-grasp
        self.grasp_height_mm = 15  # Height of gripper center above ground
        self.lift_height_mm = 150  # Height to lift block after grasp
        
        # Orientation parameters
        self.align_to_block = True  # Rotate base to match block angle
        self.max_misalignment_degrees = 30  # Max angle difference to attempt pickup
        self.alignment_tolerance_degrees = 5  # "Close enough" for gripper
        
        # Mecanum fine positioning
        self.use_mecanum_positioning = True  # Use strafing for precise centering
        self.position_tolerance_pixels = 20  # Center within this many pixels
        
        # Speed limits (calibrate with tools/calibrate_motors.py)
        self.min_speed_forward = 20  # Below this, motors don't move
        self.min_speed_strafe = 20   # Adjust after calibration
        self.min_speed_rotate = 0.2
        self.max_speed_forward = 80  # Safe maximum
        self.max_speed_strafe = 80
        self.max_speed_rotate = 0.8
        
        # Camera parameters (these may need calibration)
        self.camera_offset_forward_mm = 100  # Camera is 10cm ahead of base
        self.camera_offset_up_mm = 100  # Camera is 10cm above ground
        self.camera_height_pixels = 480
        self.camera_width_pixels = 640
        
        # Color detection parameters (HSV ranges)
        self.color_ranges = {
            'red': [(0, 100, 100), (10, 255, 255)],  # Lower red
            'red2': [(170, 100, 100), (180, 255, 255)],  # Upper red
            'blue': [(100, 100, 100), (130, 255, 255)],
            'green': [(40, 100, 100), (80, 255, 255)],
            'yellow': [(20, 100, 100), (40, 255, 255)],
            'purple': [(130, 100, 100), (160, 255, 255)]  # Purple/violet
        }
    
    def pickup_block(self, color: str = 'red', use_tag: bool = True, 
                     tag_id: Optional[int] = None) -> PickupResult:
        """
        Detect and pick up a colored block
        
        Args:
            color: Block color to find ('red', 'blue', 'green', 'yellow')
            use_tag: Use AprilTag for positioning (more accurate)
            tag_id: Specific tag to use as reference (None = any visible tag)
        
        Returns:
            PickupResult with success status and details
        """
        start_time = time.time()
        images = []
        
        logger.info(f"Starting pickup sequence for {color} block")
        
        try:
            # 1. DETECT block and tag
            logger.info("Detecting block and reference tag...")
            img = self.camera.read()
            images.append(self._save_image(img, "01_initial_view"))
            
            block = self._detect_block_by_color(img, color)
            if not block:
                return PickupResult(
                    success=False,
                    reason=f"No {color} block detected",
                    block_position=None,
                    time_taken=time.time() - start_time,
                    images=images
                )
            
            tag = None
            if use_tag:
                tags = self.vision.detect_apriltags()
                if tag_id is not None:
                    tag = next((t for t in tags if t.id == tag_id), None)
                elif tags:
                    tag = tags[0]  # Use closest/first tag
                
                if not tag:
                    logger.warning("No reference tag found, using distance estimation")
                    use_tag = False
            
            # 2. ESTIMATE 3D position
            if use_tag and tag:
                block_pos = self._estimate_position_with_tag(block, tag)
                logger.info(f"Block position (tag-assisted): {block_pos}")
            else:
                block_pos = self._estimate_position_simple(block)
                logger.info(f"Block position (estimated): {block_pos}")
            
            # Draw detection on image
            img_annotated = self._annotate_detection(img, block, tag)
            images.append(self._save_image(img_annotated, "02_detection"))
            
            # 2.5. CHECK ALIGNMENT
            if self.align_to_block and abs(block.angle) > self.alignment_tolerance_degrees:
                if abs(block.angle) > self.max_misalignment_degrees:
                    logger.warning(f"Block angle ({block.angle:.1f}°) too extreme for gripper")
                    return PickupResult(
                        success=False,
                        reason=f"Block misaligned by {block.angle:.1f}° (max {self.max_misalignment_degrees}°)",
                        block_position=None,
                        time_taken=time.time() - start_time,
                        images=images
                    )
                
                logger.info(f"Aligning to block angle: {block.angle:.1f}°")
                align_success = self._align_to_block(block.angle)
                if not align_success:
                    logger.warning("Alignment failed, attempting pickup anyway")
                
                # Re-detect after alignment
                time.sleep(0.5)
                img = self.camera.read()
                block = self._detect_block_by_color(img, color)
                if not block:
                    return PickupResult(
                        success=False,
                        reason="Lost block after alignment",
                        block_position=block_pos,
                        time_taken=time.time() - start_time,
                        images=images
                    )
                
                images.append(self._save_image(img, "02b_after_alignment"))
            
            # 2.6. FINE POSITIONING using mecanum strafing
            if self.use_mecanum_positioning:
                logger.info("Fine-positioning with mecanum strafing...")
                position_success = self._fine_position_block(color)
                if position_success:
                    # Re-detect after fine positioning
                    time.sleep(0.3)
                    img = self.camera.read()
                    block = self._detect_block_by_color(img, color)
                    if block and use_tag and tag:
                        tags = self.vision.detect_apriltags()
                        tag = tags[0] if tags else None
                        if tag:
                            block_pos = self._estimate_position_with_tag(block, tag)
                        else:
                            block_pos = self._estimate_position_simple(block)
                    elif block:
                        block_pos = self._estimate_position_simple(block)
                    
                    images.append(self._save_image(img, "02c_after_fine_position"))
            
            # 3. APPROACH block if too far
            if block_pos[0] > self.approach_distance_mm:
                logger.info(f"Block {block_pos[0]:.0f}mm away, approaching...")
                approach_success = self._approach_block(color)
                if not approach_success:
                    return PickupResult(
                        success=False,
                        reason="Failed to approach block",
                        block_position=block_pos,
                        time_taken=time.time() - start_time,
                        images=images
                    )
                
                # Re-detect after approach
                time.sleep(0.5)
                img = self.camera.read()
                images.append(self._save_image(img, "03_after_approach"))
                
                block = self._detect_block_by_color(img, color)
                if not block:
                    return PickupResult(
                        success=False,
                        reason="Lost block after approach",
                        block_position=block_pos,
                        time_taken=time.time() - start_time,
                        images=images
                    )
                
                if use_tag and tag:
                    tags = self.vision.detect_apriltags()
                    tag = tags[0] if tags else None
                    if tag:
                        block_pos = self._estimate_position_with_tag(block, tag)
                    else:
                        block_pos = self._estimate_position_simple(block)
                else:
                    block_pos = self._estimate_position_simple(block)
            
            # 4. EXECUTE pickup using IK
            logger.info("Executing IK-based pickup sequence...")
            pickup_success = self._execute_pickup_ik(block_pos)
            
            # Capture final image
            time.sleep(0.5)
            img_final = self.camera.read()
            images.append(self._save_image(img_final, "04_after_pickup"))
            
            if pickup_success:
                return PickupResult(
                    success=True,
                    reason="Block picked up successfully",
                    block_position=block_pos,
                    time_taken=time.time() - start_time,
                    images=images
                )
            else:
                return PickupResult(
                    success=False,
                    reason="Pickup sequence failed",
                    block_position=block_pos,
                    time_taken=time.time() - start_time,
                    images=images
                )
        
        except Exception as e:
            logger.error(f"Pickup failed with exception: {e}")
            import traceback
            traceback.print_exc()
            
            return PickupResult(
                success=False,
                reason=f"Exception: {str(e)}",
                block_position=None,
                time_taken=time.time() - start_time,
                images=images
            )
    
    def _detect_block_by_color(self, img, color: str) -> Optional[BlockDetection]:
        """
        Detect block by color using HSV color space
        
        Args:
            img: BGR image from camera
            color: Color to detect
        
        Returns:
            BlockDetection or None (includes orientation angle)
        """
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Create mask for color
        if color not in self.color_ranges:
            logger.error(f"Unknown color: {color}")
            return None
        
        # Get color range
        lower, upper = self.color_ranges[color]
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        
        # Special handling for red (wraps around in HSV)
        if color == 'red' and 'red2' in self.color_ranges:
            lower2, upper2 = self.color_ranges['red2']
            mask2 = cv2.inRange(hsv, np.array(lower2), np.array(upper2))
            mask = cv2.bitwise_or(mask, mask2)
        
        # Morphological operations to clean up
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
        # Find largest contour
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        
        # Filter by minimum size
        if area < 100:  # Too small
            return None
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(largest)
        
        # Calculate center
        cx = x + w // 2
        cy = y + h // 2
        
        # Get orientation using minimum area rectangle
        # This gives us the angle of the block!
        rect = cv2.minAreaRect(largest)
        angle = rect[2]  # Angle in degrees
        
        # OpenCV gives angle in range [-90, 0]
        # Normalize to [-45, 45] where 0 = aligned with gripper
        # (Assumes square block, so 90° rotation = same orientation)
        if angle < -45:
            angle = 90 + angle
        
        # Confidence based on area (larger = more confident)
        confidence = min(1.0, area / 10000.0)
        
        return BlockDetection(
            color=color,
            center=(cx, cy),
            width=w,
            height=h,
            bbox=(x, y, x+w, y+h),
            confidence=confidence,
            angle=angle  # Block rotation angle
        )
    
    def _estimate_position_with_tag(self, block: BlockDetection, tag) -> Tuple[float, float, float]:
        """
        Estimate block 3D position using AprilTag reference
        
        This is the KEY advantage - tag provides accurate scale and position!
        
        Args:
            block: Block detection
            tag: AprilTag detection with pose
        
        Returns:
            (x, y, z) in robot base coordinates (mm)
        """
        # Tag provides known size and distance
        tag_size_mm = 150  # 6 inch tag
        
        # Calculate mm per pixel at tag distance using tag size
        tag_pixel_width = tag.corners[2][0] - tag.corners[0][0]  # Width in pixels
        mm_per_pixel = tag_size_mm / tag_pixel_width
        
        # Block offset from tag in pixels
        offset_x_pixels = block.center[0] - tag.center[0]
        offset_y_pixels = block.center[1] - tag.center[1]
        
        # Convert to mm
        offset_x_mm = offset_x_pixels * mm_per_pixel
        offset_y_mm = offset_y_pixels * mm_per_pixel
        
        # Tag gives us distance (z)
        tag_distance = tag.distance_estimate  # in mm
        
        # Block is roughly at same distance as tag (same plane)
        # Adjust for height difference (tag is at 10" = 254mm, block on ground)
        block_distance = tag_distance  # Approximate
        
        # Convert to robot base coordinates
        # x = forward (distance from robot)
        # y = left/right offset
        # z = up/down (height above ground)
        
        x = block_distance - self.camera_offset_forward_mm
        y = offset_x_mm  # Horizontal offset
        z = 0  # Block on ground
        
        return (x, y, z)
    
    def _estimate_position_simple(self, block: BlockDetection) -> Tuple[float, float, float]:
        """
        Estimate block position without tag (less accurate)
        
        Uses known block size to estimate distance
        
        Args:
            block: Block detection
        
        Returns:
            (x, y, z) in robot coordinates (mm)
        """
        # Estimate distance using block size
        # Known: 1" block = 25mm
        # Larger in image = closer
        
        # Rough focal length (needs calibration!)
        focal_length_pixels = 600  # Calibrate this for your camera
        
        # Estimate distance
        distance_mm = (self.block_size_mm * focal_length_pixels) / block.width
        
        # Offset from center
        center_x = self.camera_width_pixels / 2
        center_y = self.camera_height_pixels / 2
        
        offset_x_pixels = block.center[0] - center_x
        offset_y_pixels = block.center[1] - center_y
        
        # Convert to mm (rough)
        mm_per_pixel = distance_mm / focal_length_pixels
        offset_x_mm = offset_x_pixels * mm_per_pixel
        offset_y_mm = offset_y_pixels * mm_per_pixel
        
        # Robot coordinates
        x = distance_mm - self.camera_offset_forward_mm
        y = offset_x_mm
        z = 0  # Ground level
        
        return (x, y, z)
    
    def _align_to_block(self, target_angle: float, tolerance: float = 5.0) -> bool:
        """
        Rotate robot base to align gripper with block orientation
        
        Uses mecanum rotation capability for precise angle adjustment.
        
        Args:
            target_angle: Block angle to match (degrees)
            tolerance: Acceptable alignment error (degrees)
        
        Returns:
            True if successfully aligned
        """
        logger.info(f"Aligning base to block angle: {target_angle:.1f}°")
        
        # Convert angle to rotation
        # Positive angle = rotate counter-clockwise
        rotation_speed = 0.2 if target_angle > 0 else -0.2
        
        # Estimate rotation time (rough)
        rotation_time = abs(target_angle) / 45.0  # ~45°/second at speed 0.2
        
        # Rotate in place (mecanum can pivot without translation)
        self.chassis.set_velocity(0, 0, rotation_speed)
        time.sleep(rotation_time)
        self.chassis.stop()
        
        logger.info(f"Rotated ~{target_angle:.1f}° to align gripper")
        return True  # Assume success (no feedback for now)
    
    def _fine_position_block(self, color: str, max_iterations: int = 20) -> bool:
        """
        Use mecanum strafing to precisely center block
        
        Mecanum advantage: Can move laterally without rotating!
        - Strafe left/right to center horizontally
        - Move forward/backward for distance
        - Rotate for angle (already done in _align_to_block)
        
        Args:
            color: Block color to track
            max_iterations: Max positioning attempts
        
        Returns:
            True if block well-centered
        """
        logger.info("Fine-positioning using mecanum strafing...")
        
        for i in range(max_iterations):
            # Detect block
            img = self.camera.read()
            block = self._detect_block_by_color(img, color)
            
            if not block:
                logger.warning("Lost block during fine positioning")
                return False
            
            # Check if well-centered
            center_x = self.camera_width_pixels / 2
            center_y = self.camera_height_pixels / 2
            
            offset_x = block.center[0] - center_x
            offset_y = block.center[1] - center_y
            
            # Good enough?
            if abs(offset_x) < 20 and abs(offset_y) < 20:
                logger.info("Block well-centered!")
                self.chassis.stop()
                return True
            
            # Calculate mecanum movements
            # Offset in pixels → velocity in each direction
            
            # Lateral correction (strafe left/right)
            strafe_speed = 0
            if abs(offset_x) > 20:
                strafe_speed = -offset_x / 15.0  # Proportional
                # Enforce min/max
                if abs(strafe_speed) < self.min_speed_strafe:
                    strafe_speed = self.min_speed_strafe if strafe_speed > 0 else -self.min_speed_strafe
                strafe_speed = max(-self.max_speed_strafe, min(self.max_speed_strafe, strafe_speed))
            
            # Forward/backward correction
            forward_speed = 0
            if abs(offset_y) > 20:
                # Positive offset_y = block in lower part of frame = too far
                forward_speed = offset_y / 20.0
                # Enforce min/max
                if abs(forward_speed) < self.min_speed_forward:
                    forward_speed = self.min_speed_forward if forward_speed > 0 else -self.min_speed_forward
                forward_speed = max(-self.max_speed_forward, min(self.max_speed_forward, forward_speed))
            
            # Move (mecanum can do both simultaneously!)
            self.chassis.set_velocity(forward_speed, strafe_speed, 0)
            time.sleep(0.3)
            self.chassis.stop()
            time.sleep(0.1)
        
        logger.warning("Fine positioning max iterations reached")
        self.chassis.stop()
        return False
    
    def _approach_block(self, color: str, max_attempts: int = 30) -> bool:
        """
        Drive toward block using visual servoing
        
        Similar to AprilTag navigation but tracking block color
        
        Args:
            color: Block color to track
            max_attempts: Max control loop iterations
        
        Returns:
            True if successfully approached
        """
        logger.info("Visual servoing approach to block...")
        
        for attempt in range(max_attempts):
            # Detect block
            img = self.camera.read()
            block = self._detect_block_by_color(img, color)
            
            if not block:
                logger.warning("Lost block during approach")
                return False
            
            # Check if close enough
            if block.width > 150:  # Large in view = close
                logger.info("Arrived at block!")
                self.chassis.stop()
                return True
            
            # Center block horizontally
            center_x = self.camera_width_pixels / 2
            offset_x = block.center[0] - center_x
            
            if abs(offset_x) > 30:  # Need to turn
                turn_speed = -offset_x / 500.0
                turn_speed = max(-self.max_speed_rotate, min(self.max_speed_rotate, turn_speed))
                # Enforce minimum
                if abs(turn_speed) < self.min_speed_rotate:
                    turn_speed = self.min_speed_rotate if turn_speed > 0 else -self.min_speed_rotate
                self.chassis.set_velocity(0, 0, turn_speed)
                time.sleep(0.2)
            else:
                # Block centered, drive forward
                # Slow down when close, but respect minimum speed
                if block.width > 80:  # Very close
                    speed = max(self.min_speed_forward, 20)
                else:
                    speed = max(self.min_speed_forward, 30)
                speed = min(speed, self.max_speed_forward)
                self.chassis.set_velocity(speed, 0, 0)
                time.sleep(0.3)
            
            self.chassis.stop()
            time.sleep(0.1)
        
        logger.warning("Max approach attempts reached")
        self.chassis.stop()
        return False
    
    def _execute_pickup_ik(self, block_pos: Tuple[float, float, float]) -> bool:
        """
        Execute pickup using inverse kinematics
        
        NO HARDCODED POSITIONS - all calculated from block position!
        
        Args:
            block_pos: (x, y, z) block position in mm
        
        Returns:
            True if pickup successful
        """
        x, y, z = block_pos
        
        try:
            # Step 1: Move to pre-grasp position (above block)
            logger.info("Moving to pre-grasp position...")
            pre_x = x
            pre_y = y
            pre_z = z + self.pre_grasp_height_mm
            
            self.arm.set_position(pre_x, pre_y, pre_z, duration=2.0)
            time.sleep(2.5)
            
            # Step 2: Open gripper
            logger.info("Opening gripper...")
            self.arm.gripper_open()
            time.sleep(1.0)
            
            # Step 3: Lower to grasp position
            logger.info("Lowering to grasp position...")
            grasp_x = x
            grasp_y = y
            grasp_z = z + self.grasp_height_mm
            
            self.arm.set_position(grasp_x, grasp_y, grasp_z, duration=2.0)
            time.sleep(2.5)
            
            # Step 4: Close gripper
            logger.info("Closing gripper...")
            self.arm.gripper_close()
            time.sleep(1.5)
            
            # Step 5: Lift block
            logger.info("Lifting block...")
            lift_x = x
            lift_y = y
            lift_z = self.lift_height_mm
            
            self.arm.set_position(lift_x, lift_y, lift_z, duration=2.0)
            time.sleep(2.5)
            
            logger.info("Pickup sequence complete!")
            return True
            
        except Exception as e:
            logger.error(f"Pickup execution failed: {e}")
            return False
    
    def _annotate_detection(self, img, block: Optional[BlockDetection], tag=None):
        """Draw detection boxes and info on image"""
        img_copy = img.copy()
        
        # Draw block
        if block:
            x1, y1, x2, y2 = block.bbox
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(img_copy, block.center, 5, (0, 255, 0), -1)
            
            # Draw orientation arrow
            arrow_length = 30
            angle_rad = math.radians(block.angle)
            end_x = int(block.center[0] + arrow_length * math.cos(angle_rad))
            end_y = int(block.center[1] + arrow_length * math.sin(angle_rad))
            cv2.arrowedLine(img_copy, block.center, (end_x, end_y), (255, 0, 0), 2)
            
            # Label with color and angle
            cv2.putText(img_copy, f"{block.color} {block.angle:.1f}deg", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw tag
        if tag:
            corners = tag.corners.astype(int)
            cv2.polylines(img_copy, [corners], True, (0, 0, 255), 2)
            cv2.putText(img_copy, f"Tag {tag.id}", 
                       (int(tag.center[0]), int(tag.center[1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return img_copy
    
    def _save_image(self, img, name: str) -> str:
        """Save image for debugging"""
        from pathlib import Path
        output_dir = Path("pickup_images")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.jpg"
        path = output_dir / filename
        
        cv2.imwrite(str(path), img)
        return str(path)
