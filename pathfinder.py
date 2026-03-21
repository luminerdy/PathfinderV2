#!/usr/bin/env python3
"""
Pathfinder Robot - Main Entry Point
A clean, modular framework for educational mobile robots
"""

import sys
import yaml
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from hardware import Board, Chassis, Arm, Camera, Sonar
from capabilities import MovementController, VisionSystem, ManipulationController, SensorMonitor
from capabilities.navigation import Navigator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Pathfinder:
    """
    Main robot controller class
    Integrates all hardware and capabilities
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize Pathfinder robot
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        logger.info(f"Initializing {self.config['robot']['name']} v{self.config['robot']['version']}")
        
        # Initialize hardware
        self.board = None
        self.chassis = None
        self.arm = None
        self.camera = None
        self.sonar = None
        
        # Initialize capabilities
        self.movement = None
        self.vision = None
        self.manipulation = None
        self.sensors = None
        self.navigator = None
        
        self._initialized = False
        
    def initialize(self, enable_camera: bool = True, enable_sonar: bool = True,
                  enable_monitoring: bool = True):
        """
        Initialize all robot systems
        
        Args:
            enable_camera: Initialize camera system
            enable_sonar: Initialize sonar sensor
            enable_monitoring: Start sensor monitoring
        """
        try:
            logger.info("Initializing hardware...")
            
            # Board (required)
            hw_config = self.config['hardware']
            self.board = Board(
                device=hw_config['board']['serial_port'],
                baudrate=hw_config['board']['baud_rate']
            )
            
            # Chassis (required)
            chassis_config = hw_config['chassis']
            self.chassis = Chassis(
                self.board,
                wheel_base=chassis_config['wheel_base'],
                track_width=chassis_config['track_width'],
                wheel_diameter=chassis_config['wheel_diameter']
            )
            self.chassis.max_speed = chassis_config['max_speed']
            
            # Arm (required)
            self.arm = Arm(self.board)
            
            # Camera (optional)
            if enable_camera:
                cam_config = hw_config['camera']
                self.camera = Camera(
                    device=cam_config['device'],
                    width=cam_config['width'],
                    height=cam_config['height'],
                    fps=cam_config['fps']
                )
                self.camera.open()
                
            # Sonar (optional)
            if enable_sonar:
                sonar_config = hw_config['sonar']
                self.sonar = Sonar(max_distance=sonar_config['max_distance'])
                
            logger.info("Hardware initialized")
            
            # Initialize capabilities
            logger.info("Initializing capabilities...")
            
            self.movement = MovementController(self.chassis, self.sonar)
            
            if self.camera:
                self.vision = VisionSystem(self.camera, self.config['vision'])
                self.manipulation = ManipulationController(self.arm, self.vision)
                self.navigator = Navigator(self)  # AprilTag navigation
            else:
                self.manipulation = ManipulationController(self.arm)
                
            if enable_monitoring:
                self.sensors = SensorMonitor(self.board, self.sonar)
                self.sensors.start()
                
            logger.info("Capabilities initialized")
            
            # Startup sequence
            self.board.beep(0.1)
            # TODO: Fix arm IK wrapper before enabling home
            # self.arm.home(duration=2.0)
            
            # Turn off sonar LEDs (power saving)
            if self.board:
                self.board.set_rgb(0, 0, 0)  # All LEDs off (black)
                logger.debug("Sonar LEDs off (power saving)")
            
            self._initialized = True
            logger.info("Pathfinder ready!")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.shutdown()
            raise
            
    def shutdown(self):
        """Safely shutdown all systems"""
        logger.info("Shutting down Pathfinder...")
        
        try:
            # Stop monitoring
            if self.sensors:
                self.sensors.stop()
                
            # Stop movement
            if self.chassis:
                self.chassis.stop()
                
            # Move arm to safe position
            # TODO: Fix arm IK wrapper before enabling
            # if self.arm:
            #     self.arm.rest()
                
            # Close camera
            if self.camera:
                self.camera.close()
                
            # Close sonar
            if self.sonar:
                self.sonar.close()
                
            # Close board
            if self.board:
                # Turn off all LEDs before shutdown
                self.board.set_rgb(0, 0, 0)
                self.board.beep(0.05)
                self.board.close()
                
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            
    # ===== Quick Access Properties =====
    
    @property
    def battery_voltage(self):
        """Current battery voltage"""
        return self.board.get_battery_voltage() if self.board else None
        
    @property
    def distance(self):
        """Current distance reading"""
        return self.sonar.get_distance() if self.sonar else None
        
    def status(self):
        """Print robot status"""
        print("\n" + "="*40)
        print(f"  {self.config['robot']['name']} Status")
        print("="*40)
        
        if self.sensors:
            diag = self.sensors.get_diagnostics()
            print(f"Battery: {diag['battery_voltage']:.2f}V" if diag['battery_voltage'] else "Battery: N/A")
            print(f"Distance: {diag['distance']:.1f}cm" if diag['distance'] else "Distance: N/A")
            print(f"Camera: {'Active' if self.camera and self.camera.is_opened() else 'Inactive'}")
            print(f"Monitoring: {'Running' if diag['running'] else 'Stopped'}")
        else:
            print(f"Battery: {self.battery_voltage:.2f}V" if self.battery_voltage else "Battery: N/A")
            print(f"Distance: {self.distance:.1f}cm" if self.distance else "Distance: N/A")
            
        print("="*40 + "\n")
        
    # ===== Context Manager =====
    
    def __enter__(self):
        if not self._initialized:
            self.initialize()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Pathfinder Robot Controller')
    parser.add_argument('--config', default='config.yaml', help='Config file path')
    parser.add_argument('--demo', help='Run demo script')
    parser.add_argument('--no-camera', action='store_true', help='Disable camera')
    parser.add_argument('--no-sonar', action='store_true', help='Disable sonar')
    parser.add_argument('--no-monitoring', action='store_true', help='Disable sensor monitoring')
    
    args = parser.parse_args()
    
    # Create robot instance
    robot = Pathfinder(args.config)
    
    try:
        # Initialize
        robot.initialize(
            enable_camera=not args.no_camera,
            enable_sonar=not args.no_sonar,
            enable_monitoring=not args.no_monitoring
        )
        
        # Show status
        robot.status()
        
        # Run demo if specified
        if args.demo:
            logger.info(f"Running demo: {args.demo}")
            demo_module = __import__(f'demos.{args.demo}', fromlist=['run'])
            demo_module.run(robot)
        else:
            # Interactive mode
            logger.info("Pathfinder ready. Press Ctrl+C to exit.")
            import time
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    finally:
        robot.shutdown()


if __name__ == '__main__':
    main()
