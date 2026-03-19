"""
Board Hardware Interface
Provides servo, LED, buzzer, and sensor control via serial protocol
"""

import sys
import time
import logging
from pathlib import Path
from typing import List, Tuple, Optional

# Import from local SDK
sys.path.insert(0, str(Path(__file__).parent.parent))
from sdk.common.ros_robot_controller_sdk import Board as ControllerBoard

logger = logging.getLogger(__name__)


class Board:
    """
    Hardware board interface
    Provides access to servos, motors, LEDs, buzzer, and sensors
    """
    
    def __init__(self, device="/dev/ttyAMA0", baudrate=1000000):
        """Initialize board connection"""
        self._board = ControllerBoard(device=device, baudrate=baudrate)
        self._board.enable_reception()
        logger.info(f"Board initialized on {device}")
        
    # ===== Servo Control =====
    
    def set_servo_position(self, servo_id: int, position: int, duration: float = 0.5):
        """
        Set a single servo position
        
        Args:
            servo_id: Servo ID (1-6)
            position: Pulse width (500-2500)
            duration: Movement duration in seconds
        """
        self._board.pwm_servo_set_position(duration, [[servo_id, position]])
        
    def set_servos_position(self, servos: List[Tuple[int, int]], duration: float = 0.5):
        """
        Set multiple servo positions simultaneously
        
        Args:
            servos: List of (servo_id, position) tuples
            duration: Movement duration in seconds
        """
        self._board.pwm_servo_set_position(duration, servos)
        
    def read_servo_position(self, servo_id: int) -> Optional[int]:
        """Read current servo position"""
        return self._board.pwm_servo_read_position(servo_id)
    
    # ===== Motor Control =====
    
    def set_motor_duty(self, motor_id: int, duty: int):
        """
        Set motor duty cycle
        
        Args:
            motor_id: Motor ID (1-4)
            duty: Duty cycle (-100 to 100)
        """
        self._board.set_motor_duty([[motor_id, duty]])
        
    def set_motors_duty(self, motors: List[Tuple[int, int]]):
        """
        Set multiple motor duty cycles
        
        Args:
            motors: List of (motor_id, duty) tuples
        """
        self._board.set_motor_duty(motors)
        
    def stop_motors(self):
        """Stop all motors"""
        self._board.set_motor_duty([[1, 0], [2, 0], [3, 0], [4, 0]])
        
    # ===== Buzzer Control =====
    
    def buzzer(self, frequency: int, on_time: float, off_time: float = 0.0, repeat: int = 1):
        """
        Control buzzer
        
        Args:
            frequency: Frequency in Hz (100-10000)
            on_time: On duration in seconds
            off_time: Off duration between repeats
            repeat: Number of times to repeat
        """
        self._board.set_buzzer(frequency, on_time, off_time, repeat)
        
    def beep(self, duration: float = 0.1):
        """Quick beep"""
        self.buzzer(2000, duration)
        
    # ===== LED Control =====
    
    def set_led(self, led_id: int, state: bool):
        """
        Control onboard LED
        
        Args:
            led_id: LED ID
            state: True=on, False=off
        """
        self._board.set_led(led_id, 1 if state else 0)
        
    # ===== RGB Control =====
    
    def set_rgb(self, r: int, g: int, b: int):
        """
        Set RGB LED color
        
        Args:
            r, g, b: Color values (0-255)
        """
        # SDK expects: [(index, r, g, b), ...]
        # Assuming 2 RGB LEDs at indices 1 and 2
        self._board.set_rgb([(1, r, g, b), (2, r, g, b)])
        
    def rgb_off(self):
        """Turn off RGB LEDs"""
        self.set_rgb(0, 0, 0)
        
    # ===== Sensors =====
    
    def get_battery_voltage(self) -> Optional[float]:
        """Get battery voltage in volts"""
        try:
            mv = self._board.get_battery()
            return mv / 1000.0 if mv else None
        except Exception as e:
            logger.error(f"Error reading battery: {e}")
            return None
            
    def get_imu_data(self) -> Optional[dict]:
        """Get IMU data (accelerometer, gyroscope)"""
        try:
            return self._board.get_imu()
        except Exception as e:
            logger.error(f"Error reading IMU: {e}")
            return None
            
    # ===== Gamepad =====
    
    def get_gamepad_state(self) -> Optional[dict]:
        """Get gamepad state"""
        try:
            return self._board.get_gamepad()
        except Exception as e:
            logger.error(f"Error reading gamepad: {e}")
            return None
            
    # ===== Cleanup =====
    
    def close(self):
        """Close board connection"""
        self.stop_motors()
        self.rgb_off()
        logger.info("Board closed")
