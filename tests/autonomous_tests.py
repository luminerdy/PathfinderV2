"""
Autonomous Test Suite
Self-validating tests using AprilTag visual feedback
"""

import os
import time
import cv2
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging

from .field_config import FieldConfig, get_field_config

logger = logging.getLogger(__name__)


class AutonomousTestSuite:
    """
    Autonomous testing framework with visual verification
    
    Tests can run without human intervention and validate
    success using AprilTag detection feedback.
    """
    
    def __init__(self, robot, field_config: FieldConfig, output_dir: str = "test_results"):
        """
        Initialize test suite
        
        Args:
            robot: PathfinderRobot instance
            field_config: FieldConfig describing test field
            output_dir: Directory for test results
        """
        self.robot = robot
        self.field = field_config
        self.output_dir = Path(output_dir)
        
        # Create timestamped run directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.output_dir / f"run_{timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.run_dir / "images"
        self.image_dir.mkdir(exist_ok=True)
        
        self.results = []
        self.test_start_time = None
        
        logger.info(f"Test suite initialized: {self.run_dir}")
    
    def run_all_tests(self) -> Dict:
        """
        Run complete test suite
        
        Returns:
            Summary of all test results
        """
        self.test_start_time = time.time()
        
        logger.info("="*60)
        logger.info(f"Starting autonomous test suite: {self.field.name}")
        logger.info("="*60)
        
        # Test 1: Tag detection survey
        self.test_tag_detection_survey()
        
        # Test 2: Navigate to each tag
        for tag_id in self.field.get_all_tags():
            self.test_navigate_to_tag(tag_id)
        
        # Test 3: Sequential waypoint tour
        self.test_waypoint_tour()
        
        # Test 4: Return to start
        self.test_return_to_home()
        
        # Generate report
        summary = self.generate_report()
        
        total_time = time.time() - self.test_start_time
        logger.info("="*60)
        logger.info(f"Test suite complete! Total time: {total_time:.1f}s")
        logger.info(f"Results: {self.run_dir}")
        logger.info("="*60)
        
        return summary
    
    def test_tag_detection_survey(self) -> Dict:
        """
        Test 1: Detect all tags by rotating 360°
        
        Validates:
        - AprilTag detection working
        - All field tags visible from center
        - Distance estimation
        
        Returns:
            Test result dict
        """
        test_name = "tag_detection_survey"
        logger.info(f"\n>>> Test: {test_name}")
        
        start_time = time.time()
        tags_seen = set()
        detections = []
        
        # Rotate and scan
        num_steps = 12  # 30° increments
        for step in range(num_steps):
            angle = step * 30
            
            # Capture image
            img = self.robot.camera.read()
            
            # Detect tags
            tags = self.robot.vision.detect_apriltags()
            
            # Log detections
            for tag in tags:
                tags_seen.add(tag.id)
                detections.append({
                    'angle': angle,
                    'tag_id': tag.id,
                    'distance_mm': tag.distance_estimate,
                    'center': tag.center
                })
                
                # Draw on image
                cv2.putText(img, f"Tag {tag.id}: {tag.distance_estimate:.0f}mm",
                           (10, 30 + tag.id * 30), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (0, 255, 0), 2)
            
            # Save image
            img_path = self.image_dir / f"{test_name}_angle_{angle:03d}.jpg"
            cv2.imwrite(str(img_path), img)
            
            # Rotate
            if step < num_steps - 1:  # Don't rotate after last step
                self.robot.chassis.set_velocity(0, 0, 0.3)
                time.sleep(0.5)
                self.robot.chassis.stop()
                time.sleep(0.2)
        
        # Stop
        self.robot.chassis.stop()
        
        # Evaluate
        expected_tags = set(self.field.get_all_tags())
        found_all = tags_seen >= expected_tags
        
        result = {
            'test': test_name,
            'success': found_all,
            'time': time.time() - start_time,
            'expected_tags': list(expected_tags),
            'tags_seen': list(tags_seen),
            'missing_tags': list(expected_tags - tags_seen),
            'detections': detections,
            'reason': 'All tags detected' if found_all else f'Missing tags: {expected_tags - tags_seen}'
        }
        
        self.results.append(result)
        logger.info(f"    Result: {'✅ PASS' if found_all else '❌ FAIL'}")
        logger.info(f"    Tags seen: {sorted(tags_seen)}")
        logger.info(f"    Time: {result['time']:.1f}s")
        
        return result
    
    def test_navigate_to_tag(self, tag_id: int, stop_distance: float = 300) -> Dict:
        """
        Test 2: Navigate to specific tag
        
        Validates:
        - Navigation capability
        - Visual servoing
        - Arrival detection
        
        Args:
            tag_id: Target tag ID
            stop_distance: Target distance in mm
        
        Returns:
            Test result dict
        """
        test_name = f"navigate_to_tag_{tag_id}"
        logger.info(f"\n>>> Test: {test_name}")
        
        # Capture before
        img_before = self.robot.camera.read()
        tags_before = self.robot.vision.detect_apriltags()
        initial_distance = None
        for tag in tags_before:
            if tag.id == tag_id:
                initial_distance = tag.distance_estimate
                break
        
        # Annotate and save before image
        for tag in tags_before:
            cv2.rectangle(img_before, 
                         (int(tag.corners[0][0]), int(tag.corners[0][1])),
                         (int(tag.corners[2][0]), int(tag.corners[2][1])),
                         (0, 255, 0) if tag.id == tag_id else (0, 0, 255), 2)
            cv2.putText(img_before, f"Tag {tag.id}", 
                       (int(tag.center[0]), int(tag.center[1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        img_before_path = self.image_dir / f"{test_name}_before.jpg"
        cv2.imwrite(str(img_before_path), img_before)
        
        # Navigate
        nav_result = self.robot.navigator.go_to_tag(tag_id, stop_distance)
        
        # Capture after
        time.sleep(0.5)  # Let robot settle
        img_after = self.robot.camera.read()
        tags_after = self.robot.vision.detect_apriltags()
        final_distance = nav_result.final_distance
        
        # Annotate and save after image
        for tag in tags_after:
            cv2.rectangle(img_after,
                         (int(tag.corners[0][0]), int(tag.corners[0][1])),
                         (int(tag.corners[2][0]), int(tag.corners[2][1])),
                         (0, 255, 0) if tag.id == tag_id else (0, 0, 255), 2)
            cv2.putText(img_after, f"Tag {tag.id}: {tag.distance_estimate:.0f}mm",
                       (int(tag.center[0]), int(tag.center[1]) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        img_after_path = self.image_dir / f"{test_name}_after.jpg"
        cv2.imwrite(str(img_after_path), img_after)
        
        # Evaluate
        success = nav_result.success and final_distance is not None and final_distance < (stop_distance * 1.2)
        
        result = {
            'test': test_name,
            'success': success,
            'tag_id': tag_id,
            'initial_distance': initial_distance,
            'final_distance': final_distance,
            'target_distance': stop_distance,
            'time': nav_result.time_taken,
            'reason': nav_result.reason,
            'images': {
                'before': str(img_before_path.relative_to(self.run_dir)),
                'after': str(img_after_path.relative_to(self.run_dir))
            }
        }
        
        self.results.append(result)
        logger.info(f"    Result: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"    Distance: {initial_distance:.0f}mm → {final_distance:.0f}mm (target: {stop_distance}mm)")
        logger.info(f"    Time: {nav_result.time_taken:.1f}s")
        
        return result
    
    def test_waypoint_tour(self) -> Dict:
        """
        Test 3: Navigate sequential path through all tags
        
        Validates:
        - Multi-waypoint navigation
        - Consistency
        - Total time
        
        Returns:
            Test result dict
        """
        test_name = "waypoint_tour"
        logger.info(f"\n>>> Test: {test_name}")
        
        tag_sequence = self.field.get_all_tags()
        logger.info(f"    Path: {' → '.join(map(str, tag_sequence))}")
        
        start_time = time.time()
        
        # Navigate path
        path_result = self.robot.navigator.navigate_path(tag_sequence, stop_distance=300)
        
        # Evaluate
        success = path_result['success']
        
        result = {
            'test': test_name,
            'success': success,
            'path': tag_sequence,
            'waypoints': path_result['waypoints'],
            'total_time': path_result['total_time'],
            'reason': 'Completed full tour' if success else 'Failed at waypoint'
        }
        
        self.results.append(result)
        logger.info(f"    Result: {'✅ PASS' if success else '❌ FAIL'}")
        logger.info(f"    Total time: {path_result['total_time']:.1f}s")
        logger.info(f"    Waypoints completed: {sum(1 for w in path_result['waypoints'] if w['success'])}/{len(tag_sequence)}")
        
        return result
    
    def test_return_to_home(self, home_tag: int = 0) -> Dict:
        """
        Test 4: Return to home/start position
        
        Args:
            home_tag: Tag ID for home position (default 0)
        
        Returns:
            Test result dict
        """
        test_name = "return_to_home"
        logger.info(f"\n>>> Test: {test_name}")
        
        nav_result = self.robot.navigator.go_to_tag(home_tag, stop_distance=200)
        
        result = {
            'test': test_name,
            'success': nav_result.success,
            'home_tag': home_tag,
            'final_distance': nav_result.final_distance,
            'time': nav_result.time_taken,
            'reason': nav_result.reason
        }
        
        self.results.append(result)
        logger.info(f"    Result: {'✅ PASS' if nav_result.success else '❌ FAIL'}")
        logger.info(f"    Time: {nav_result.time_taken:.1f}s")
        
        return result
    
    def generate_report(self) -> Dict:
        """
        Generate test report (markdown + JSON)
        
        Returns:
            Summary dict
        """
        # Calculate summary
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total_tests - passed
        total_time = time.time() - self.test_start_time
        
        summary = {
            'field': self.field.name,
            'timestamp': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed': passed,
            'failed': failed,
            'total_time': total_time,
            'results': self.results
        }
        
        # Save JSON
        json_path = self.run_dir / "results.json"
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Generate markdown report
        md_path = self.run_dir / "report.md"
        with open(md_path, 'w') as f:
            f.write(f"# Autonomous Test Report\n\n")
            f.write(f"**Field:** {self.field.name}\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Duration:** {total_time:.1f} seconds\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total tests:** {total_tests}\n")
            f.write(f"- **Passed:** {passed} ✅\n")
            f.write(f"- **Failed:** {failed} ❌\n")
            f.write(f"- **Success rate:** {100*passed/total_tests:.1f}%\n\n")
            
            f.write(f"## Test Results\n\n")
            for i, result in enumerate(self.results, 1):
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                f.write(f"### {i}. {result['test']} - {status}\n\n")
                f.write(f"- **Time:** {result['time']:.1f}s\n")
                f.write(f"- **Reason:** {result['reason']}\n")
                
                # Test-specific details
                if 'tags_seen' in result:
                    f.write(f"- **Tags detected:** {result['tags_seen']}\n")
                    if result['missing_tags']:
                        f.write(f"- **Missing tags:** {result['missing_tags']}\n")
                
                if 'initial_distance' in result and result['initial_distance']:
                    f.write(f"- **Initial distance:** {result['initial_distance']:.0f}mm\n")
                    f.write(f"- **Final distance:** {result['final_distance']:.0f}mm\n")
                    f.write(f"- **Target distance:** {result['target_distance']:.0f}mm\n")
                
                if 'images' in result:
                    f.write(f"\n**Images:**\n\n")
                    f.write(f"Before | After\n")
                    f.write(f"-------|-------\n")
                    f.write(f"![Before]({result['images']['before']}) | ![After]({result['images']['after']})\n")
                
                f.write(f"\n")
        
        logger.info(f"\nReport generated: {md_path}")
        logger.info(f"JSON results: {json_path}")
        
        return summary
