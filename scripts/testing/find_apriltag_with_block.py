#!/usr/bin/env python3
"""
AprilTag Search While Holding Block
Keeps gripper closed during search - won't drop the block!
"""

from find_apriltag import AprilTagFinder

def main():
    print("=" * 60)
    print("APRILTAG SEARCH - HOLDING BLOCK MODE")
    print("=" * 60)
    print("\n[!] Gripper will stay CLOSED during search")
    print("[!] Block will NOT be dropped\n")
    
    finder = AprilTagFinder()
    
    try:
        # Position camera (keep gripper closed!)
        finder.position_camera_forward(holding_block=True)
        
        # Search for tags (maintain grip)
        tags = finder.search_for_tags(direction='right', holding_block=True)
        
        if tags:
            location = finder.localize(tags)
            
            print("\n" + "=" * 60)
            print("LOCALIZATION COMPLETE - BLOCK STILL HELD")
            print("=" * 60)
            print(f"Tag ID: {location['tag_id']}")
            print(f"Confidence: {location['confidence']}")
            print("\nRobot knows position and is still holding the block!")
            print("Ready to navigate to delivery zone!")
        else:
            print("\nNo AprilTags found")
            print("Block is still held - gripper stayed closed")
    
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        finder.cleanup()
        print("\n[!] Gripper remains in current state")
        print("    Use delivery script to release block at target")


if __name__ == '__main__':
    main()
