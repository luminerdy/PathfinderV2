#!/usr/bin/env python3
"""
Autonomous Navigation to AprilTags
Drive to each detected tag on the field
"""

import cv2
import time
import yaml
from lib.board_protocol import BoardController
from capabilities.vision import VisionSystem
import math

class TagNavigator:
    """Navigate autonomously to AprilTags"""
    
    def __init__(self):
        self.board = BoardController()
        time.sleep(0.5)
        
        # Load config
        with open('config.yaml') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize camera and vision
        self.camera = cv2.VideoCapture(0)
        time.sleep(1)
        self.vision = VisionSystem(self.camera, self.config['vision'])
        
        # Navigation parameters
        self.rotation_speed = 25
        self.rotation_increment = 0.5  # seconds
        self.settle_time = 0.3
        self.drive_speed = 30
        self.approach_distance_pixels = 40000  # Target area in pixels²
        
        # Image center for angle calculation
        self.image_center_x = 320  # 640/2
        self.image_center_y = 240  # 480/2
        
    def position_camera_forward(self):
        """Position arm to camera-forward"""
        print("Positioning camera forward...")
        positions = [
            (1, 2500),  # Gripper open
            (6, 1500),  # Base forward
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]
        for servo_id, pulse in positions:
            self.board.set_servo_position(500, [(servo_id, pulse)])
            time.sleep(0.3)
        print("  [OK] Camera positioned")
    
    def stop_motors(self):
        """Stop all motors"""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    def rotate_right(self, duration):
        """Rotate clockwise for duration seconds"""
        self.board.set_motor_duty([
            (1, self.rotation_speed),
            (2, -self.rotation_speed),
            (3, self.rotation_speed),
            (4, -self.rotation_speed)
        ])
        time.sleep(duration)
        self.stop_motors()
    
    def drive_forward(self, duration, speed=None):
        """Drive forward for duration seconds"""
        if speed is None:
            speed = self.drive_speed
        self.board.set_motor_duty([
            (1, speed), (2, speed), (3, speed), (4, speed)
        ])
        time.sleep(duration)
        self.stop_motors()
    
    def search_for_tag(self, max_attempts=20):
        """
        Search for AprilTag using move-stop-look pattern
        
        Returns:
            tag object or None
        """
        print("\nSearching for AprilTag...")
        
        for attempt in range(max_attempts):
            print(f"  Attempt {attempt + 1}/{max_attempts}", end="")
            
            # Rotate
            self.rotate_right(self.rotation_increment)
            
            # Settle
            time.sleep(self.settle_time)
            
            # Look
            ret, frame = self.camera.read()
            if not ret:
                print(" - camera failed")
                continue
            
            tags = self.vision.detect_apriltags(frame)
            if tags:
                tag = tags[0]
                print(f" - FOUND tag {tag.tag_id}!")
                
                # Save image
                cv2.imwrite(f'tag_found_{tag.tag_id}_{int(time.time())}.jpg', frame)
                
                return tag
            else:
                print(" - no tag")
        
        print("No tag found after full rotation")
        return None
    
    def center_on_tag(self, max_iterations=10):
        """
        Rotate to center tag in camera view
        
        Returns:
            True if centered, False if lost
        """
        print("\nCentering on tag...")
        
        for iteration in range(max_iterations):
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                print("  Camera failed")
                return False
            
            # Detect tag
            tags = self.vision.detect_apriltags(frame)
            if not tags:
                print("  Tag lost!")
                return False
            
            tag = tags[0]
            center_x = tag.center[0]
            offset_x = center_x - self.image_center_x
            
            print(f"  Iteration {iteration + 1}: offset = {offset_x:.0f} pixels")
            
            # Check if centered
            if abs(offset_x) < 30:  # Within 30 pixels = centered
                print("  [OK] Tag centered!")
                return True
            
            # Calculate rotation needed
            # Negative offset = tag on left = rotate left (negative speed)
            # Positive offset = tag on right = rotate right (positive speed)
            rotation_time = abs(offset_x) / 200.0  # Rough calibration
            rotation_time = max(0.1, min(1.0, rotation_time))
            
            if offset_x > 0:
                # Tag on right, rotate right
                print(f"  Rotating right {rotation_time:.2f}s")
                self.rotate_right(rotation_time)
            else:
                # Tag on left, rotate left
                print(f"  Rotating left {rotation_time:.2f}s")
                self.board.set_motor_duty([
                    (1, -self.rotation_speed),
                    (2, self.rotation_speed),
                    (3, -self.rotation_speed),
                    (4, self.rotation_speed)
                ])
                time.sleep(rotation_time)
                self.stop_motors()
            
            time.sleep(0.3)  # Settle
        
        print("  Could not center after max iterations")
        return False
    
    def approach_tag(self, max_iterations=15):
        """
        Drive toward tag until close enough
        
        Returns:
            True if reached, False if lost
        """
        print("\nApproaching tag...")
        
        for iteration in range(max_iterations):
            # Capture frame
            ret, frame = self.camera.read()
            if not ret:
                print("  Camera failed")
                return False
            
            # Detect tag
            tags = self.vision.detect_apriltags(frame)
            if not tags:
                print("  Tag lost!")
                return False
            
            tag = tags[0]
            
            # Calculate tag area (rough distance estimate)
            corners = tag.corners
            x_coords = corners[:, 0]
            y_coords = corners[:, 1]
            width = max(x_coords) - min(x_coords)
            height = max(y_coords) - min(y_coords)
            area = width * height
            
            print(f"  Iteration {iteration + 1}: area = {area:.0f} pixels²")
            
            # Check if close enough
            if area > self.approach_distance_pixels:
                print("  [OK] Close enough!")
                return True
            
            # Drive forward a bit
            drive_time = 0.5  # Small increments
            print(f"  Driving forward {drive_time}s")
            self.drive_forward(drive_time)
            
            time.sleep(0.3)  # Settle
        
        print("  Max iterations reached")
        return False
    
    def navigate_to_tag(self):
        """
        Complete navigation sequence to one tag
        
        Returns:
            tag_id if successful, None if failed
        """
        print("\n" + "=" * 60)
        print("NAVIGATING TO APRILTAG")
        print("=" * 60)
        
        # Step 1: Search for tag
        tag = self.search_for_tag()
        if not tag:
            return None
        
        tag_id = tag.tag_id
        print(f"\nTarget: Tag {tag_id}")
        
        # Step 2: Center on tag
        if not self.center_on_tag():
            print("Failed to center on tag")
            return None
        
        # Step 3: Approach tag
        if not self.approach_tag():
            print("Failed to approach tag")
            return None
        
        print("\n" + "=" * 60)
        print(f"SUCCESS! Reached Tag {tag_id}")
        print("=" * 60)
        
        return tag_id
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_motors()
        self.camera.release()


def main():
    print("=" * 60)
    print("AUTONOMOUS APRILTAG NAVIGATION TEST")
    print("=" * 60)
    
    nav = TagNavigator()
    
    try:
        # Position camera
        nav.position_camera_forward()
        time.sleep(1)
        
        # Navigate to tags
        visited_tags = []
        max_tags = 4  # Try to visit all 4 tags
        
        for attempt in range(max_tags):
            print(f"\n\nATTEMPT {attempt + 1}/{max_tags}")
            
            tag_id = nav.navigate_to_tag()
            
            if tag_id is not None:
                visited_tags.append(tag_id)
                print(f"\nVisited tags so far: {visited_tags}")
                
                # Back up to see more tags
                print("\nBacking up to find next tag...")
                nav.board.set_motor_duty([
                    (1, -30), (2, -30), (3, -30), (4, -30)
                ])
                time.sleep(1.5)
                nav.stop_motors()
                time.sleep(0.5)
                
                # Rotate to look for different tag
                print("Rotating to find different tag...")
                nav.rotate_right(2.0)
                time.sleep(0.5)
            else:
                print("\nNo tag found on this attempt")
                # Rotate more to search
                nav.rotate_right(3.0)
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print(f"Successfully visited {len(visited_tags)} tag(s): {visited_tags}")
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        nav.cleanup()


if __name__ == '__main__':
    main()
