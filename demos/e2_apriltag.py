"""
E2 - AprilTag Navigation
Advanced: AprilTag detection and navigation
"""

import cv2
import time
import logging

logger = logging.getLogger(__name__)


def run(robot):
    """
    E2 Demo: AprilTag detection and navigation
    
    Teaches:
    - AprilTag detection
    - Visual feedback
    - Tag-based navigation
    - Pick and place using tags
    """
    logger.info("=== E2: AprilTag Demo ===")
    
    if robot.camera is None or robot.vision is None:
        print("Error: Camera/Vision system not available")
        return
        
    try:
        # 1. Detect AprilTags
        print("\n1. Scanning for AprilTags...")
        print("   Press 'q' to continue to next demo")
        
        while True:
            frame = robot.camera.read()
            if frame is None:
                continue
                
            # Detect tags
            detections = robot.vision.detect_apriltags(frame)
            
            # Draw detections
            display = robot.vision.draw_apriltags(frame, detections)
            
            # Show count
            cv2.putText(display, f"Tags detected: {len(detections)}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                       
            # List detected IDs
            if detections:
                y = 60
                for det in detections:
                    cv2.putText(display, f"ID {det.tag_id}", 
                               (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y += 30
                    
            cv2.imshow('AprilTag Detection', display)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cv2.destroyAllWindows()
        time.sleep(0.5)
        
        # 2. Track specific tag
        print("\n2. Tracking tag ID 0 (if available)...")
        print("   Robot will center tag in frame")
        print("   Press 'q' to stop")
        
        tag_id = 0
        duration = 20.0
        start = time.time()
        
        while time.time() - start < duration:
            frame = robot.camera.read()
            if frame is None:
                continue
                
            # Find specific tag
            detection = robot.vision.find_apriltag(frame, tag_id)
            
            if detection:
                # Draw detection
                display = robot.vision.draw_apriltags(frame, [detection])
                
                # Calculate centering error
                frame_center_x = frame.shape[1] // 2
                error_x = detection.center[0] - frame_center_x
                
                cv2.putText(display, f"Tag {tag_id} found - Error: {error_x}px", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                           
                # Simple proportional control to center tag
                if abs(error_x) > 50:
                    rotation = -error_x / frame_center_x * 0.3
                    robot.chassis.set_velocity(0, 0, rotation)
                else:
                    robot.chassis.stop()
                    cv2.putText(display, "CENTERED", 
                               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                display = frame.copy()
                cv2.putText(display, f"Searching for tag {tag_id}...", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                robot.chassis.stop()
                
            cv2.imshow('Tag Tracking', display)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        robot.chassis.stop()
        cv2.destroyAllWindows()
        time.sleep(0.5)
        
        # 3. Pick object at AprilTag
        print("\n3. Pick object at AprilTag location...")
        print("   Place tag ID 1 with object on it")
        input("   Press Enter when ready...")
        
        frame = robot.camera.read()
        if frame is not None:
            detection = robot.vision.find_apriltag(frame, tag_id=1)
            
            if detection:
                print(f"   Found tag 1 at pixel {detection.center}")
                
                # Show annotated frame
                display = robot.vision.draw_apriltags(frame, [detection])
                cv2.imshow('Target', display)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
                
                # Attempt pick
                print("   Attempting pick...")
                success = robot.manipulation.pick_by_apriltag(1, frame, offset_y=0)
                
                if success:
                    print("   Pick successful!")
                    time.sleep(1)
                    
                    # Place at different location
                    print("   Placing object...")
                    robot.manipulation.place_object(80, 180, 30)
                    
                    print("   Transfer complete!")
                else:
                    print("   Pick failed")
            else:
                print("   Tag 1 not found")
                
        # 4. Navigate to AprilTag
        print("\n4. Navigate to AprilTag 2...")
        print("   Robot will approach tag 2")
        print("   Press 'q' to stop")
        
        approach_distance = 30  # cm
        duration = 30.0
        start = time.time()
        
        while time.time() - start < duration:
            frame = robot.camera.read()
            if frame is None:
                continue
                
            detection = robot.vision.find_apriltag(frame, tag_id=2)
            
            if detection:
                display = robot.vision.draw_apriltags(frame, [detection])
                
                # Estimate distance (very rough - needs calibration)
                tag_size_px = max(
                    abs(detection.corners[0][0] - detection.corners[2][0]),
                    abs(detection.corners[0][1] - detection.corners[2][1])
                )
                
                # Simple proportional navigation
                frame_center_x = frame.shape[1] // 2
                error_x = detection.center[0] - frame_center_x
                
                if tag_size_px < 200:  # Far away
                    # Move forward while centering
                    rotation = -error_x / frame_center_x * 0.3
                    robot.chassis.set_velocity(40, 0, rotation)
                    cv2.putText(display, "APPROACHING", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else:  # Close enough
                    robot.chassis.stop()
                    cv2.putText(display, "ARRIVED", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow('Navigation', display)
                    cv2.waitKey(2000)
                    break
                    
            else:
                display = frame.copy()
                cv2.putText(display, "Searching for tag 2...", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                # Slowly rotate to search
                robot.chassis.set_velocity(0, 0, 0.2)
                
            cv2.imshow('Navigation', display)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        robot.chassis.stop()
        cv2.destroyAllWindows()
        
        print("\nE2 Demo complete!")
        
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        robot.chassis.stop()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    print("Run via: python pathfinder.py --demo e2_apriltag")
