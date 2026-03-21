#!/usr/bin/env python3
"""
Autonomous AprilTag Search and Localization
Robot rotates to find AprilTags and determine position
"""

import cv2
import time
from lib.board_protocol import BoardController
from capabilities.vision import VisionSystem
import yaml

class AprilTagFinder:
    """Autonomous AprilTag search and localization"""
    
    def __init__(self):
        self.board = BoardController()
        
        # Load config
        with open('config.yaml') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize camera
        self.camera = cv2.VideoCapture(0)
        time.sleep(0.5)
        
        # Initialize vision
        self.vision = VisionSystem(self.camera, self.config['vision'])
        
        # Search parameters
        self.rotation_speed = 20  # Slow rotation for reliable detection
        self.check_interval = 0.3  # Check for tags every 300ms
        self.max_rotation_time = 30  # Give up after 30 seconds
        
    def position_camera_forward(self):
        """Position arm to camera-forward for tag searching"""
        print("Positioning camera forward...")
        
        camera_forward = [
            (1, 2500),  # Gripper open
            (6, 1500),  # Base forward
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]
        
        for servo_id, pwm in camera_forward:
            self.board.set_servo_position(500, [(servo_id, pwm)])
            time.sleep(0.3)
        
        time.sleep(0.5)
        print("  [OK] Camera positioned")
    
    def start_rotation(self, direction='right'):
        """Start slow rotation to search for tags"""
        # Rotate in place: left wheels opposite right wheels
        if direction == 'right':
            # Rotate clockwise
            self.board.set_motor_duty([
                (1, self.rotation_speed),   # FL forward
                (2, -self.rotation_speed),  # FR backward
                (3, self.rotation_speed),   # RL forward
                (4, -self.rotation_speed)   # RR backward
            ])
        else:
            # Rotate counter-clockwise
            self.board.set_motor_duty([
                (1, -self.rotation_speed),
                (2, self.rotation_speed),
                (3, -self.rotation_speed),
                (4, self.rotation_speed)
            ])
    
    def stop_rotation(self):
        """Stop rotating"""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    def search_for_tags(self, direction='right', save_image=True):
        """
        Rotate and search for AprilTags
        
        Returns:
            List of detected tags or None if timeout
        """
        print(f"\nSearching for AprilTags (rotating {direction})...")
        print(f"Will check every {self.check_interval}s for up to {self.max_rotation_time}s")
        
        # Start rotating
        self.start_rotation(direction)
        
        start_time = time.time()
        check_count = 0
        
        try:
            while (time.time() - start_time) < self.max_rotation_time:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret:
                    print("  [WARN] Camera read failed")
                    time.sleep(self.check_interval)
                    continue
                
                check_count += 1
                
                # Detect AprilTags
                tags = self.vision.detect_apriltags(frame)
                
                if tags:
                    # Found tag(s)!
                    self.stop_rotation()
                    elapsed = time.time() - start_time
                    
                    print(f"\n[SUCCESS] Found {len(tags)} tag(s) after {elapsed:.1f}s ({check_count} checks)")
                    
                    for tag in tags:
                        print(f"\n  Tag ID: {tag.tag_id}")
                        print(f"  Center: ({tag.center[0]:.0f}, {tag.center[1]:.0f}) pixels")
                        print(f"  Corners: {len(tag.corners)} detected")
                        
                        # Calculate angle offset from image center
                        image_center_x = frame.shape[1] / 2
                        offset_x = tag.center[0] - image_center_x
                        
                        # Rough angle estimate (assuming 60° FOV)
                        angle_per_pixel = 60.0 / frame.shape[1]
                        angle_offset = offset_x * angle_per_pixel
                        
                        print(f"  Offset from center: {offset_x:.0f} pixels")
                        print(f"  Estimated angle: {angle_offset:.1f}° from forward")
                        
                        if hasattr(tag, 'pose_t') and tag.pose_t is not None:
                            distance = tag.pose_t[2][0] * 1000  # Convert to mm
                            print(f"  Estimated distance: {distance:.0f}mm")
                    
                    # Save image with detected tags
                    if save_image:
                        # Draw tag outlines
                        annotated = frame.copy()
                        for tag in tags:
                            corners = tag.corners.astype(int)
                            cv2.polylines(annotated, [corners], True, (0, 255, 0), 2)
                            cv2.putText(annotated, f"ID:{tag.tag_id}", 
                                      (int(tag.center[0]), int(tag.center[1])),
                                      cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        
                        filename = f'apriltag_found_{int(time.time())}.jpg'
                        cv2.imwrite(filename, annotated)
                        print(f"\n  Image saved: {filename}")
                    
                    return tags
                
                # No tags yet, wait and continue
                time.sleep(self.check_interval)
            
            # Timeout - no tags found
            self.stop_rotation()
            print(f"\n[TIMEOUT] No tags found after {self.max_rotation_time}s")
            return None
            
        except KeyboardInterrupt:
            print("\n\nSearch interrupted by user")
            self.stop_rotation()
            return None
    
    def localize(self, tags):
        """
        Determine robot position based on detected tags
        
        This is a placeholder - full implementation would use:
        - Known tag positions on field
        - Tag pose estimation
        - Triangulation if multiple tags visible
        """
        if not tags:
            return None
        
        tag = tags[0]  # Use first tag
        
        # For now, just return basic info
        # Full implementation would map tag ID to field position
        localization = {
            'tag_id': tag.tag_id,
            'center': tag.center,
            'visible': True,
            'confidence': 'high' if len(tag.corners) == 4 else 'low'
        }
        
        return localization
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_rotation()
        self.camera.release()


def main():
    """Main function for standalone use"""
    print("=" * 60)
    print("APRILTAG AUTONOMOUS SEARCH")
    print("=" * 60)
    
    finder = AprilTagFinder()
    
    try:
        # Position camera
        finder.position_camera_forward()
        
        # Search for tags
        tags = finder.search_for_tags(direction='right')
        
        if tags:
            # Localize based on tags
            location = finder.localize(tags)
            
            print("\n" + "=" * 60)
            print("LOCALIZATION RESULT")
            print("=" * 60)
            print(f"Tag ID: {location['tag_id']}")
            print(f"Tag visible: {location['visible']}")
            print(f"Confidence: {location['confidence']}")
            print("\nRobot can now navigate relative to this tag!")
        else:
            print("\nNo AprilTags found on field")
            print("Recommendations:")
            print("  - Check that tags are printed and mounted")
            print("  - Verify camera is working")
            print("  - Ensure tags are within camera view when rotating")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        finder.cleanup()
        print("\n" + "=" * 60)
        print("Search complete")
        print("=" * 60)


if __name__ == '__main__':
    main()
