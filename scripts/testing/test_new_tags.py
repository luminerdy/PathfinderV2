#!/usr/bin/env python3
"""
Quick test of new 10" tag36h11 AprilTags
Tests detection quality and range with larger tags
"""

import sys
sys.path.append('/home/robot/code/pathfinder')

from hardware.camera import Camera
from pupil_apriltags import Detector
import cv2
import time

def test_new_tags():
    """Test new 10-inch tag36h11 tags"""
    
    print("="*70)
    print("NEW APRILTAG TEST - 10\" tag36h11 (PathfinderBot Standard)")
    print("="*70)
    print()
    print("Expected tags on field:")
    print("  Tag 583: Home/Start (North wall)")
    print("  Tag 584: Pickup Zone 1 (East wall)")
    print("  Tag 585: Pickup Zone 2 (South wall)")
    print("  Tag 586: Delivery Zone (West wall)")
    print()
    print("Camera opening...")
    
    # Initialize camera
    camera = Camera(device=0, width=640, height=480)
    if not camera.open():
        print("ERROR: Could not open camera!")
        return
    
    print("Camera ready!")
    print()
    print("Initializing AprilTag detector (tag36h11)...")
    
    # Initialize detector
    detector = Detector(families='tag36h11')
    
    print("Detector ready!")
    print()
    print("Point robot at field tags...")
    print("Press ESC to exit, 's' to save image")
    print()
    
    time.sleep(1)  # Let camera warm up
    
    detected_tags = {}  # Track all detected tags
    frame_count = 0
    last_print = time.time()
    
    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue
            
            frame_count += 1
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect tags
            tags = detector.detect(gray)
            
            # Process detections
            for tag in tags:
                tag_id = tag.tag_id
                
                # Track this tag
                if tag_id not in detected_tags:
                    detected_tags[tag_id] = {
                        'first_seen': frame_count,
                        'count': 0,
                        'max_area': 0,
                        'min_area': 999999,
                        'name': get_tag_name(tag_id)
                    }
                
                detected_tags[tag_id]['count'] += 1
                
                # Calculate area
                corners = tag.corners
                width = max(corners[:, 0]) - min(corners[:, 0])
                height = max(corners[:, 1]) - min(corners[:, 1])
                area = width * height
                
                detected_tags[tag_id]['max_area'] = max(detected_tags[tag_id]['max_area'], area)
                detected_tags[tag_id]['min_area'] = min(detected_tags[tag_id]['min_area'], area)
                
                # Draw detection
                # Draw corners
                for i in range(4):
                    pt1 = tuple(corners[i].astype(int))
                    pt2 = tuple(corners[(i+1) % 4].astype(int))
                    cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
                
                # Draw center
                cx, cy = int(tag.center[0]), int(tag.center[1])
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                # Label
                name = get_tag_name(tag_id)
                label = f"ID {tag_id}: {name}"
                cv2.putText(frame, label, (cx - 80, cy - 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Area
                area_text = f"Area: {area:.0f}px"
                cv2.putText(frame, area_text, (cx - 60, cy + 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Distance estimate (10" tag)
                # Rough formula: distance ~= (tag_width_pixels / actual_width_mm) * focal_length
                # For 10" (254mm) tag at various distances
                distance_estimate = estimate_distance(area)
                dist_text = f"~{distance_estimate:.1f}m"
                cv2.putText(frame, dist_text, (cx - 40, cy + 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            
            # Status overlay
            status_y = 30
            cv2.putText(frame, f"Detected {len(tags)} tag(s)", (10, status_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            if detected_tags:
                status_y += 30
                tag_list = ', '.join([f"{tid}" for tid in sorted(detected_tags.keys())])
                cv2.putText(frame, f"Seen: {tag_list}", (10, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow("New AprilTag Test - 10\" tag36h11", frame)
            
            # Print periodic summary
            if time.time() - last_print > 2.0 and tags:
                print(f"[Frame {frame_count}] Detected {len(tags)} tag(s):")
                for tag in tags:
                    name = get_tag_name(tag.tag_id)
                    corners = tag.corners
                    width = max(corners[:, 0]) - min(corners[:, 0])
                    height = max(corners[:, 1]) - min(corners[:, 1])
                    area = width * height
                    dist = estimate_distance(area)
                    print(f"  Tag {tag.tag_id} ({name}): area={area:.0f}px², ~{dist:.1f}m")
                last_print = time.time()
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('s'):  # Save
                filename = f"new_tags_test_{int(time.time())}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Image saved: {filename}")
                
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    finally:
        camera.close()
        cv2.destroyAllWindows()
        
        # Print summary
        print("\n" + "="*70)
        print("DETECTION SUMMARY")
        print("="*70)
        
        if detected_tags:
            print(f"\nTotal frames: {frame_count}")
            print(f"Unique tags detected: {len(detected_tags)}")
            print()
            
            for tag_id in sorted(detected_tags.keys()):
                info = detected_tags[tag_id]
                detection_rate = (info['count'] / frame_count) * 100
                
                print(f"Tag {tag_id} ({info['name']}):")
                print(f"  First seen: frame {info['first_seen']}")
                print(f"  Detections: {info['count']}/{frame_count} ({detection_rate:.1f}%)")
                print(f"  Area range: {info['min_area']:.0f} - {info['max_area']:.0f} px²")
                
                # Distance estimates
                max_dist = estimate_distance(info['min_area'])
                min_dist = estimate_distance(info['max_area'])
                print(f"  Distance range: {min_dist:.1f}m - {max_dist:.1f}m")
                print()
            
            # Overall assessment
            print("="*70)
            print("ASSESSMENT:")
            
            expected = {583, 584, 585, 586}
            detected_ids = set(detected_tags.keys())
            
            if expected.issubset(detected_ids):
                print("✅ All expected tags detected!")
            else:
                missing = expected - detected_ids
                print(f"⚠️  Missing tags: {missing}")
            
            # Detection quality
            avg_max_area = sum(t['max_area'] for t in detected_tags.values()) / len(detected_tags)
            if avg_max_area > 50000:
                print("✅ Excellent detection quality (large tag areas)")
            elif avg_max_area > 20000:
                print("✅ Good detection quality")
            elif avg_max_area > 5000:
                print("⚠️  Fair detection quality")
            else:
                print("❌ Poor detection quality (tags may be too far)")
            
            print()
            print("COMPARISON TO OLD 6\" TAGS:")
            print("  Old tags (6\"): typical area 170-31,000 px², range ~1-2m")
            print(f"  New tags (10\"): max area {avg_max_area:.0f} px², range ~{min_dist:.1f}-{max_dist:.1f}m")
            
            if avg_max_area > 20000:
                improvement = (avg_max_area / 15000) * 100
                print(f"  ✅ ~{improvement:.0f}% better detection!")
            
        else:
            print("❌ No tags detected")
            print("   - Check tag IDs (should be 583-586)")
            print("   - Check tag family (should be tag36h11)")
            print("   - Check lighting")
            print("   - Check camera position/orientation")

def get_tag_name(tag_id):
    """Get tag name from ID"""
    names = {
        583: "Home/Start",
        584: "Pickup_1",
        585: "Pickup_2",
        586: "Delivery"
    }
    return names.get(tag_id, "Unknown")

def estimate_distance(area_px):
    """Rough distance estimate for 10\" (254mm) tag"""
    # Very rough approximation
    # Larger area = closer distance
    if area_px > 100000:
        return 0.3  # Very close
    elif area_px > 50000:
        return 0.8
    elif area_px > 20000:
        return 1.5
    elif area_px > 10000:
        return 2.0
    elif area_px > 5000:
        return 2.5
    elif area_px > 2000:
        return 3.0
    elif area_px > 1000:
        return 3.5
    else:
        return 4.0  # Far

if __name__ == "__main__":
    test_new_tags()
