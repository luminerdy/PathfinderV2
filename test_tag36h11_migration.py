#!/usr/bin/env python3
"""
Test tag36h11 migration
Verifies new tag family detection after migration
"""

import sys
sys.path.append('/home/robot/code/pathfinder')

from capabilities.vision import VisionSystem
from hardware.camera import Camera
import cv2
import time
import yaml

def test_migration():
    """Test tag36h11 detection"""
    
    print("="*60)
    print("APRILTAG MIGRATION TEST - tag36h11")
    print("="*60)
    print()
    print("Expected tags: 583, 584, 585, 586")
    print("(PathfinderBot standard)")
    print()
    print("Point robot at tags on field...")
    print("Press ESC or Ctrl+C to exit")
    print()
    
    # Load config
    with open('/home/robot/code/pathfinder/config.yaml') as f:
        config = yaml.safe_load(f)
    
    camera = Camera()
    vision = VisionSystem(camera, config.get('vision', {}))
    camera.start_capture()
    
    time.sleep(1)  # Let camera initialize
    
    detected_tags = set()
    
    try:
        while True:
            frame = camera.get_frame()
            if frame is None:
                continue
            
            # Detect tags
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = vision.detect_apriltags(gray)
            
            # Draw detections
            for tag in tags:
                tag_id = tag['id']
                detected_tags.add(tag_id)
                
                # Draw bounding box
                corners = tag['corners']
                for i in range(4):
                    pt1 = tuple(corners[i].astype(int))
                    pt2 = tuple(corners[(i+1) % 4].astype(int))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
                
                # Label
                cx, cy = tag['center_x'], tag['center_y']
                
                # Tag name mapping
                tag_names = {
                    583: "Home/Start",
                    584: "Pickup_1",
                    585: "Pickup_2",
                    586: "Delivery"
                }
                
                name = tag_names.get(tag_id, "Unknown")
                label = f"ID {tag_id}: {name}"
                
                cv2.putText(frame, label, (int(cx)-50, int(cy)-20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Area
                area_text = f"Area: {tag['area']:.0f}px2"
                cv2.putText(frame, area_text, (int(cx)-50, int(cy)+20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                print(f"✅ Detected Tag {tag_id} ({name}): center=({cx:.0f}, {cy:.0f}), area={tag['area']:.0f}")
            
            # Show detection summary
            summary = f"Tags seen: {sorted(detected_tags)}"
            cv2.putText(frame, summary, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow("AprilTag Migration Test", frame)
            
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
                
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
    
    finally:
        camera.stop_capture()
        cv2.destroyAllWindows()
        
        # Summary
        print("\n" + "="*60)
        print("MIGRATION TEST SUMMARY")
        print("="*60)
        if detected_tags:
            print(f"✅ Detected tags: {sorted(detected_tags)}")
            
            expected = {583, 584, 585, 586}
            if detected_tags & expected:
                print(f"✅ Migration successful! tag36h11 working!")
            else:
                print(f"⚠️  Detected tags but not PathfinderBot IDs")
                print(f"   Expected: {sorted(expected)}")
        else:
            print("❌ No tags detected")
            print("   Make sure you're holding a tag36h11 tag (IDs 583-586)")

if __name__ == "__main__":
    test_migration()
