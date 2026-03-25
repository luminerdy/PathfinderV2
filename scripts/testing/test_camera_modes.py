#!/usr/bin/env python3
"""
Test camera modes and switching strategy
Determines optimal angles for navigation vs block detection
"""

import sys
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hardware.arm import Arm
from hardware.camera import Camera
from capabilities.vision import Vision
import cv2
import time

def test_camera_mode(arm, camera, vision, mode_name, servo_positions, test_type):
    """Test a specific camera angle configuration"""
    
    print(f"\n{'='*60}")
    print(f"Testing: {mode_name}")
    print(f"{'='*60}")
    
    # Move to position
    print(f"Moving camera to {mode_name} position...")
    arm.set_servos(servo_positions)
    time.sleep(2)
    
    print(f"Servo positions: {servo_positions}")
    
    # Capture test image
    frame = camera.get_frame()
    if frame is None:
        print("❌ No frame captured")
        return None
    
    # Save reference image
    filename = f"/home/robot/code/pathfinder/camera_{mode_name.lower().replace(' ', '_')}.jpg"
    cv2.imwrite(filename, frame)
    print(f"📸 Image saved: {filename}")
    
    # Test detection based on type
    results = {}
    
    if test_type == 'apriltag' or test_type == 'both':
        print("\n🏷️  Testing AprilTag detection...")
        tags = vision.detect_apriltags(frame)
        if tags:
            print(f"   ✅ Detected {len(tags)} tag(s)")
            for tag in tags:
                print(f"      ID {tag['id']}: center=({tag['center_x']}, {tag['center_y']}), area={tag['area']:.0f}px²")
            results['apriltag_count'] = len(tags)
            results['apriltag_visible'] = True
        else:
            print(f"   ❌ No AprilTags detected")
            results['apriltag_count'] = 0
            results['apriltag_visible'] = False
    
    if test_type == 'block' or test_type == 'both':
        print("\n🟥 Testing block detection...")
        blocks = vision.detect_blocks(frame)
        if blocks:
            print(f"   ✅ Detected {len(blocks)} block(s)")
            for block in blocks:
                print(f"      {block['color']}: center=({block['center_x']}, {block['center_y']}), area={block['area']:.0f}px²")
            results['block_count'] = len(blocks)
            results['block_visible'] = True
        else:
            print(f"   ❌ No blocks detected")
            results['block_count'] = 0
            results['block_visible'] = False
    
    # User feedback
    print(f"\nPlease review the camera view:")
    if test_type == 'apriltag':
        see_tags = input("  Can you see AprilTags clearly? (y/n): ").lower() == 'y'
        results['user_confirms'] = see_tags
    elif test_type == 'block':
        see_blocks = input("  Can you see blocks on floor clearly? (y/n): ").lower() == 'y'
        results['user_confirms'] = see_blocks
    else:
        see_both = input("  Can you see both tags AND floor blocks? (y/n): ").lower() == 'y'
        results['user_confirms'] = see_both
    
    fov = input("  Field of view rating (1-5, 5=excellent): ")
    results['fov_rating'] = int(fov) if fov.isdigit() else 3
    
    return results

def calibrate_camera_angles():
    """Find optimal camera angles for different tasks"""
    
    print("="*60)
    print("CAMERA MODE CALIBRATION")
    print("="*60)
    print("\nThis will test different camera angles to find optimal")
    print("positions for navigation and block detection.\n")
    
    # Setup
    print("Setup instructions:")
    print("  1. Place robot on field")
    print("  2. Place AprilTag ~1m in front")
    print("  3. Place colored block on floor ~30cm in front")
    input("\nPress Enter when ready...")
    
    arm = Arm()
    camera = Camera()
    vision = Vision()
    camera.start_capture()
    
    # Test configurations
    # Format: (name, servo_dict, test_type)
    test_configs = [
        # Current camera-forward (navigation)
        ("Navigation Forward", {
            6: 1500,  # Base center
            5: 700,   # Shoulder
            4: 2450,  # Elbow
            3: 590,   # Wrist
            1: 2500   # Gripper open
        }, 'apriltag'),
        
        # Angled down slightly (compromise)
        ("Compromise Angle", {
            6: 1500,
            5: 900,   # Shoulder lower
            4: 2200,  # Elbow less extended
            3: 800,   # Wrist more down
            1: 2500
        }, 'both'),
        
        # Looking down at floor (block detection)
        ("Block Detection Down", {
            6: 1500,
            5: 1200,  # Shoulder way down
            4: 1800,  # Elbow pulled back
            3: 1200,  # Wrist straight down
            1: 2500
        }, 'block'),
        
        # Extreme down (close blocks)
        ("Close Pickup View", {
            6: 1500,
            5: 1400,  # Very low
            4: 1600,  # Retracted
            3: 1500,  # Pointing down
            1: 2500
        }, 'block'),
    ]
    
    results = {}
    
    for config_name, servos, test_type in test_configs:
        result = test_camera_mode(arm, camera, vision, config_name, servos, test_type)
        results[config_name] = {
            'servos': servos,
            'test_type': test_type,
            'results': result
        }
        
        time.sleep(1)
    
    # Analysis
    print("\n" + "="*60)
    print("CALIBRATION SUMMARY")
    print("="*60)
    
    for config_name, data in results.items():
        print(f"\n{config_name}:")
        print(f"  Purpose: {data['test_type']}")
        if data['results']:
            print(f"  User rating: {data['results'].get('fov_rating', 'N/A')}/5")
            print(f"  User confirms: {data['results'].get('user_confirms', False)}")
            if 'apriltag_count' in data['results']:
                print(f"  AprilTags: {data['results']['apriltag_count']}")
            if 'block_count' in data['results']:
                print(f"  Blocks: {data['results']['block_count']}")
    
    # Recommendations
    print("\n" + "="*60)
    print("RECOMMENDED CAMERA STRATEGY")
    print("="*60)
    
    # Find best modes
    nav_modes = {k: v for k, v in results.items() if v['test_type'] in ['apriltag', 'both']}
    block_modes = {k: v for k, v in results.items() if v['test_type'] in ['block', 'both']}
    
    if nav_modes:
        best_nav = max(nav_modes.items(), 
                      key=lambda x: x[1]['results'].get('fov_rating', 0) if x[1]['results'] else 0)
        print(f"\n📍 NAVIGATION MODE: {best_nav[0]}")
        print(f"   Servos: {best_nav[1]['servos']}")
        print(f"   Use for: AprilTag detection, long-distance navigation")
    
    if block_modes:
        best_block = max(block_modes.items(),
                        key=lambda x: x[1]['results'].get('fov_rating', 0) if x[1]['results'] else 0)
        print(f"\n🟥 BLOCK DETECTION MODE: {best_block[0]}")
        print(f"   Servos: {best_block[1]['servos']}")
        print(f"   Use for: Floor block detection, close-range positioning")
    
    print("\n🔄 SWITCHING STRATEGY:")
    print("   1. Start in NAVIGATION mode")
    print("   2. Navigate to approximate block location using AprilTag")
    print("   3. SWITCH to BLOCK DETECTION mode")
    print("   4. Fine-tune position using block vision")
    print("   5. Execute pickup")
    print("   6. SWITCH back to NAVIGATION mode")
    print("   7. Navigate to delivery location")
    
    # Save configuration
    import json
    config_file = '/home/robot/code/pathfinder/camera_modes.json'
    with open(config_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Configuration saved to: {config_file}")
    
    camera.stop_capture()
    arm.cleanup()

if __name__ == "__main__":
    try:
        calibrate_camera_angles()
    except KeyboardInterrupt:
        print("\n\nCalibration cancelled")
        sys.exit(1)
