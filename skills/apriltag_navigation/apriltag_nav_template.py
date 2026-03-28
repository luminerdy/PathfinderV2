#!/usr/bin/env python3
"""
AprilTag Navigation Template (Level 3: Fill in the Blanks)

This template provides the structure for AprilTag navigation.
Your job: Fill in the TODO sections to complete the implementation.

Learning goals:
- Understand the navigation pipeline
- Implement proportional control
- Handle edge cases (no tag, timeout, obstacles)

Hints are provided for each TODO section.
"""

import cv2
import time
import yaml
from pupil_apriltags import Detector
from lib.board import get_board

class AprilTagNavigator:
    """Navigate to AprilTags using proportional control and mecanum drive."""
    
    def __init__(self, config_path='config.yaml'):
        """
        Initialize navigator with configuration.
        
        Args:
            config_path: Path to YAML config file
        """
        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Hardware
        self.board = get_board()
        self.camera = None
        
        # TODO 1: Create AprilTag detector
        # Hint: Use Detector(families='tag36h11')
        self.detector = ???  # YOUR CODE HERE
        
        # Extract config values for easy access
        self.target_distance = self.config['target_distance']
        self.kx = self.config['gains']['lateral']
        self.kz = self.config['gains']['forward']
        self.center_tol = self.config['tolerances']['center']
        self.dist_tol = self.config['tolerances']['distance']
    
    def open_camera(self):
        """Open camera if not already open."""
        if self.camera is None or not self.camera.isOpened():
            # TODO 2: Open camera and set resolution
            # Hint: cv2.VideoCapture(0), then set CAP_PROP_FRAME_WIDTH/HEIGHT
            self.camera = ???  # YOUR CODE HERE
            time.sleep(1.0)  # Camera warm-up time
    
    def close_camera(self):
        """Release camera."""
        if self.camera and self.camera.isOpened():
            self.camera.release()
            self.camera = None
    
    def stop_motors(self):
        """Stop all motors."""
        # TODO 3: Stop all 4 motors
        # Hint: set_motor_duty([(motor_id, duty), ...])
        # Motor IDs: 1=FL, 2=FR, 3=RL, 4=RR
        ???  # YOUR CODE HERE
    
    def drive_mecanum(self, strafe, forward):
        """
        Drive with mecanum wheels (simultaneous strafe + forward).
        
        Args:
            strafe: Lateral speed (positive = right, negative = left)
            forward: Forward speed (positive = forward, negative = backward)
        
        Mecanum equations:
            FL = forward + strafe
            FR = forward - strafe
            RL = forward - strafe
            RR = forward + strafe
        """
        # TODO 4: Calculate wheel speeds using mecanum equations
        # Hint: See equations in docstring above
        fl = ???  # YOUR CODE HERE
        fr = ???  # YOUR CODE HERE
        rl = ???  # YOUR CODE HERE
        rr = ???  # YOUR CODE HERE
        
        # Clamp speeds to valid range (-100 to 100)
        fl = max(-100, min(100, fl))
        fr = max(-100, min(100, fr))
        rl = max(-100, min(100, rl))
        rr = max(-100, min(100, rr))
        
        # Send to motors
        self.board.set_motor_duty([
            (1, int(fl)),
            (2, int(fr)),
            (3, int(rl)),
            (4, int(rr))
        ])
    
    def detect_tag(self, tag_id):
        """
        Detect specified AprilTag in current camera frame.
        
        Args:
            tag_id: Which tag to look for
        
        Returns:
            Detected tag object or None if not found
        """
        # TODO 5: Capture frame and detect tag
        # Steps:
        #   1. Read frame from camera
        #   2. Convert to grayscale
        #   3. Run detector
        #   4. Find tag with matching ID
        
        # Hint: camera.read() returns (success, frame)
        ret, frame = ???  # YOUR CODE HERE
        
        if not ret:
            return None
        
        # Hint: cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = ???  # YOUR CODE HERE
        
        # Get camera parameters from config
        cam = self.config['camera']
        camera_params = [cam['fx'], cam['fy'], cam['cx'], cam['cy']]
        tag_size = self.config['tag']['size']
        
        # Hint: detector.detect(gray, estimate_tag_pose=True, ...)
        detections = ???  # YOUR CODE HERE
        
        # Find tag with matching ID
        for detection in detections:
            if detection.tag_id == tag_id:
                return detection
        
        return None  # Tag not found
    
    def calculate_control(self, tag):
        """
        Calculate control signals from tag pose.
        
        Args:
            tag: Detected tag object with pose information
        
        Returns:
            (strafe_speed, forward_speed) tuple
        """
        # TODO 6: Extract pose from tag
        # Hint: tag.pose_t is translation vector [[x], [y], [z]]
        x = ???  # YOUR CODE HERE - lateral offset
        z = ???  # YOUR CODE HERE - distance forward
        
        # TODO 7: Calculate errors
        # Hint: lateral_error = x (want to minimize x, so error = x - 0)
        #       distance_error = z - target_distance
        lateral_error = ???  # YOUR CODE HERE
        distance_error = ???  # YOUR CODE HERE
        
        # TODO 8: Proportional control
        # Hint: speed = gain * error
        strafe_speed = ???  # YOUR CODE HERE (use self.kx)
        forward_speed = ???  # YOUR CODE HERE (use self.kz)
        
        # TODO 9: Apply deadbands (don't correct tiny errors)
        # Hint: if abs(error) < tolerance: speed = 0
        if abs(lateral_error) < self.center_tol:
            strafe_speed = 0
        
        if abs(distance_error) < self.dist_tol:
            forward_speed = 0  # Arrived!
        
        # Clamp speeds
        max_speed = self.config['speeds']['max']
        strafe_speed = max(-max_speed, min(max_speed, strafe_speed))
        forward_speed = max(-max_speed, min(max_speed, forward_speed))
        
        return strafe_speed, forward_speed
    
    def navigate_to_tag(self, tag_id, timeout=30.0):
        """
        Navigate to specified AprilTag.
        
        Args:
            tag_id: Which tag to approach
            timeout: Maximum time (seconds) before giving up
        
        Returns:
            True if reached tag, False if timeout
        """
        self.open_camera()
        start_time = time.time()
        
        print(f"Navigating to tag {tag_id}...")
        
        try:
            while True:
                # TODO 10: Check timeout
                # Hint: if time.time() - start_time > timeout: ...
                if ???:  # YOUR CODE HERE
                    print("Timeout!")
                    return False
                
                # Detect tag
                tag = self.detect_tag(tag_id)
                
                if tag is None:
                    # No tag found - stop and keep looking
                    self.stop_motors()
                    print("Searching for tag...")
                    time.sleep(0.1)
                    continue
                
                # Calculate control
                strafe, forward = self.calculate_control(tag)
                
                # TODO 11: Check if arrived
                # Hint: If both speeds are 0, we've arrived (within tolerances)
                if ???:  # YOUR CODE HERE
                    print("Arrived!")
                    self.stop_motors()
                    return True
                
                # Drive toward tag
                self.drive_mecanum(strafe, forward)
                
                # Print status
                x = tag.pose_t[0][0]
                z = tag.pose_t[2][0]
                print(f"Tag detected: x={x:+.3f}m, z={z:.3f}m, "
                      f"strafe={strafe:+.1f}, forward={forward:+.1f}")
                
                time.sleep(0.01)  # Control loop delay
        
        finally:
            self.stop_motors()
            self.close_camera()


def main():
    """Run the navigation example."""
    print("=" * 60)
    print("APRILTAG NAVIGATION (Template)")
    print("=" * 60)
    print()
    print("TODO: Complete the template code above!")
    print()
    print("Once complete, this will navigate to tag 581.")
    print("Press Ctrl+C to stop.")
    print("-" * 60)
    
    # Load config to get target tag
    with open('config.yaml') as f:
        config = yaml.safe_load(f)
    
    target_id = config['target_tag_id']
    
    # Create navigator
    nav = AprilTagNavigator()
    
    try:
        # Navigate!
        success = nav.navigate_to_tag(target_id, timeout=30.0)
        
        if success:
            print("\nSUCCESS!")
            nav.board.set_buzzer(1000, 0.1, 0.1, 2)
        else:
            print("\nFailed to reach tag.")
    
    except KeyboardInterrupt:
        print("\nStopped by user.")
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
