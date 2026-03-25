#!/usr/bin/env python3
"""
Quick snapshot test of new AprilTags
Takes one photo and analyzes it (camera-friendly - no live view)
"""

import sys
sys.path.append('/home/robot/code/pathfinder')

import subprocess
import cv2
from pupil_apriltags import Detector
import time

def test_tags_snapshot():
    """Take snapshot and analyze tags"""
    
    print("="*70)
    print("NEW APRILTAG SNAPSHOT TEST")
    print("="*70)
    print()
    print("This test will:")
    print("1. Stop web servers (to release camera)")
    print("2. Capture one image")
    print("3. Detect AprilTags")
    print("4. Restart web servers")
    print()
    
    # Stop web servers
    print("Stopping web servers...")
    subprocess.run(["sudo", "systemctl", "stop", "pathfinder-drive"], check=False)
    subprocess.run(["sudo", "systemctl", "stop", "pathfinder-servo"], check=False)
    time.sleep(2)
    
    # Capture image using fswebcam (simple, reliable)
    print("Capturing image...")
    filename = f"/home/robot/code/pathfinder/tag_test_{int(time.time())}.jpg"
    
    result = subprocess.run([
        "fswebcam",
        "-r", "640x480",
        "--no-banner",
        "-S", "10",  # Skip 10 frames to let camera adjust
        filename
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"ERROR capturing image: {result.stderr}")
        # Restart services
        subprocess.run(["sudo", "systemctl", "start", "pathfinder-drive"], check=False)
        subprocess.run(["sudo", "systemctl", "start", "pathfinder-servo"], check=False)
        return
    
    print(f"Image captured: {filename}")
    print()
    
    # Load and analyze
    print("Loading image...")
    frame = cv2.imread(filename)
    
    if frame is None:
        print("ERROR: Could not load image!")
        subprocess.run(["sudo", "systemctl", "start", "pathfinder-drive"], check=False)
        subprocess.run(["sudo", "systemctl", "start", "pathfinder-servo"], check=False)
        return
    
    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")
    print()
    
    # Detect tags
    print("Detecting AprilTags (tag36h11)...")
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    detector = Detector(families='tag36h11')
    tags = detector.detect(gray)
    
    print(f"Found {len(tags)} tag(s)")
    print()
    
    if tags:
        print("="*70)
        print("DETECTIONS:")
        print("="*70)
        
        for i, tag in enumerate(tags, 1):
            tag_id = tag.tag_id
            name = get_tag_name(tag_id)
            
            # Calculate area
            corners = tag.corners
            width = max(corners[:, 0]) - min(corners[:, 0])
            height = max(corners[:, 1]) - min(corners[:, 1])
            area = width * height
            
            # Center
            cx, cy = int(tag.center[0]), int(tag.center[1])
            
            # Distance estimate
            distance = estimate_distance(area)
            
            print(f"\nTag {i}:")
            print(f"  ID: {tag_id}")
            print(f"  Name: {name}")
            print(f"  Center: ({cx}, {cy}) pixels")
            print(f"  Size: {width:.0f} x {height:.0f} pixels")
            print(f"  Area: {area:.0f} px²")
            print(f"  Est. distance: ~{distance:.1f}m")
            
            # Draw on image
            for j in range(4):
                pt1 = tuple(corners[j].astype(int))
                pt2 = tuple(corners[(j+1) % 4].astype(int))
                cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
            
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
            label = f"ID {tag_id}: {name}"
            cv2.putText(frame, label, (cx - 80, cy - 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            area_text = f"{area:.0f}px² (~{distance:.1f}m)"
            cv2.putText(frame, area_text, (cx - 70, cy + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # Save annotated image
        annotated_file = filename.replace('.jpg', '_annotated.jpg')
        cv2.imwrite(annotated_file, frame)
        print()
        print(f"Annotated image saved: {annotated_file}")
        
        # Summary
        print()
        print("="*70)
        print("SUMMARY:")
        print("="*70)
        
        detected_ids = {tag.tag_id for tag in tags}
        expected = {583, 584, 585, 586}
        
        print(f"\nDetected tags: {sorted(detected_ids)}")
        print(f"Expected tags: {sorted(expected)}")
        
        if expected.issubset(detected_ids):
            print("\n✅ ALL EXPECTED TAGS DETECTED!")
        else:
            missing = expected - detected_ids
            extra = detected_ids - expected
            if missing:
                print(f"\n⚠️  Missing: {sorted(missing)}")
            if extra:
                print(f"⚠️  Extra/unexpected: {sorted(extra)}")
        
        # Quality assessment
        areas = [max(tag.corners[:, 0]) - min(tag.corners[:, 0]) *
                 (max(tag.corners[:, 1]) - min(tag.corners[:, 1]))
                 for tag in tags]
        avg_area = sum(areas) / len(areas)
        max_area = max(areas)
        
        print(f"\nDetection quality:")
        print(f"  Average area: {avg_area:.0f} px²")
        print(f"  Largest area: {max_area:.0f} px²")
        
        if max_area > 50000:
            print("  ✅ Excellent (very close or large tags)")
        elif max_area > 20000:
            print("  ✅ Good")
        elif max_area > 5000:
            print("  ⚠️  Fair")
        else:
            print("  ❌ Poor (tags too far or too small)")
        
        print()
        print("COMPARISON TO OLD 6\" TAGS:")
        print("  Old tags: typical max ~31,000 px² at close range")
        print(f"  New tags: max {max_area:.0f} px²")
        
        if max_area > 31000:
            improvement = ((max_area - 31000) / 31000) * 100
            print(f"  ✅ {improvement:.0f}% larger detection area!")
        
    else:
        print("❌ No tags detected!")
        print()
        print("Troubleshooting:")
        print("  - Check that tags are visible to camera")
        print("  - Verify tags are tag36h11 family (IDs 583-586)")
        print("  - Check lighting (good, even lighting works best)")
        print("  - Verify tags are flat and not wrinkled")
        print(f"\nRaw image saved: {filename}")
        print("You can inspect it to see what camera sees")
    
    # Restart web servers
    print()
    print("Restarting web servers...")
    subprocess.run(["sudo", "systemctl", "start", "pathfinder-drive"], check=False)
    subprocess.run(["sudo", "systemctl", "start", "pathfinder-servo"], check=False)
    
    print("\nTest complete!")
    print(f"Images at: /home/robot/code/pathfinder/")

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
    if area_px > 100000:
        return 0.3
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
        return 4.0

if __name__ == "__main__":
    test_tags_snapshot()
