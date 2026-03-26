"""
Board Controller for Pi 4 — I2C Protocol

The Pi 4 MasterPi board communicates via I2C (bus 1, address 0x7A).
This is a clean rewrite of the vendor Board.py module.

Protocol (reverse-engineered from vendor code):
  I2C bus: 1
  Address: 0x7A

  Battery:  Write [0x00], Read 2 bytes (uint16 LE, millivolts)
  Motor:    Write [31 + index, speed_signed_byte]  (index 0-3, speed -100..100)
  Servo:    Write [40, count, time_lo, time_hi, id1, pulse_lo1, pulse_hi1, ...]
  Buzzer:   GPIO pin 31 (HIGH=on, LOW=off)
  RGB LEDs: WS281x on GPIO pin 12 (requires root for DMA)

Motor indexing: 1-based (motor 1-4)
  Motors 1,3 are inverted (left side mounted backwards)

Servo indexing: 1-based (servo 1-6)
  Servo 2 does not physically exist on this platform
  Supports deviation correction from Deviation.yaml

Created: March 26, 2026
Reverse-engineered from /home/pi/MasterPi/HiwonderSDK/Board.py
"""

import time
import struct
from smbus2 import SMBus, i2c_msg
from typing import List, Tuple, Optional

try:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    _GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    _GPIO_AVAILABLE = False

# I2C configuration
I2C_BUS = 1
I2C_ADDR = 0x7A

# Register addresses
REG_BATTERY = 0x00
REG_MOTOR_BASE = 31      # Motor 0 = reg 31, motor 1 = reg 32, etc.
REG_SERVO_CMD = 40        # Servo command register

# GPIO
BUZZER_PIN = 31

# Deviation file (servo calibration offsets)
DEVIATION_FILE = '/home/robot/code/pathfinder/Deviation.yaml'


def _load_deviations():
    """Load servo deviation values from YAML file"""
    try:
        import yaml
        with open(DEVIATION_FILE) as f:
            data = yaml.safe_load(f)
            if data:
                return {int(k): int(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


class BoardController:
    """
    I2C board controller for Pi 4 MasterPi platform.
    
    Same API as lib/board_protocol.py (Pi 5) so all skills
    work unchanged on either platform.
    """
    
    def __init__(self):
        self._deviations = _load_deviations()
        self._buzzer_initialized = False
    
    def _i2c_write(self, data):
        """Write bytes to board via I2C"""
        with SMBus(I2C_BUS) as bus:
            try:
                msg = i2c_msg.write(I2C_ADDR, data)
                bus.i2c_rdwr(msg)
            except Exception:
                # Retry once on failure (vendor code does this)
                try:
                    msg = i2c_msg.write(I2C_ADDR, data)
                    bus.i2c_rdwr(msg)
                except Exception:
                    pass
    
    def _i2c_read(self, register, length):
        """Write register address then read bytes"""
        with SMBus(I2C_BUS) as bus:
            try:
                msg_write = i2c_msg.write(I2C_ADDR, [register])
                bus.i2c_rdwr(msg_write)
                msg_read = i2c_msg.read(I2C_ADDR, length)
                bus.i2c_rdwr(msg_read)
                return list(msg_read)
            except Exception:
                try:
                    msg_write = i2c_msg.write(I2C_ADDR, [register])
                    bus.i2c_rdwr(msg_write)
                    msg_read = i2c_msg.read(I2C_ADDR, length)
                    bus.i2c_rdwr(msg_read)
                    return list(msg_read)
                except Exception:
                    return None
    
    # ===== Motor Control =====
    
    def set_motor_duty(self, motors: List[Tuple[int, float]]):
        """
        Set motor duty cycles.
        
        Args:
            motors: List of (motor_id, duty) tuples
                   motor_id: 1-4
                   duty: -100 to 100 (negative = reverse)
        """
        for motor_id, duty in motors:
            if motor_id < 1 or motor_id > 4:
                continue
            
            # Invert motors 1 and 3 (left side, mounted backwards)
            if motor_id == 1 or motor_id == 3:
                duty = -duty
            
            # Clamp
            duty = max(-100, min(100, int(duty)))
            
            # Register: 31 + (motor_id - 1)
            reg = REG_MOTOR_BASE + (motor_id - 1)
            
            # Speed as signed byte
            speed_byte = duty.to_bytes(1, 'little', signed=True)[0]
            self._i2c_write([reg, speed_byte])
    
    # ===== Servo Control =====
    
    def set_servo_position(self, duration_ms: int, servos: List[Tuple[int, int]]):
        """
        Set servo positions (all move simultaneously).
        
        Args:
            duration_ms: Movement duration in milliseconds
            servos: List of (servo_id, pulse_width) tuples
                   servo_id: 1-6
                   pulse_width: 500-2500 (1500 = center)
        """
        duration_ms = max(0, min(30000, duration_ms))
        count = len(servos)
        
        # Build command: [40, count, time_lo, time_hi, id1, pulse_lo1, pulse_hi1, ...]
        buf = [REG_SERVO_CMD, count]
        buf += list(duration_ms.to_bytes(2, 'little'))
        
        for servo_id, pulse in servos:
            if servo_id < 1 or servo_id > 6:
                continue
            
            # Apply deviation correction
            deviation = self._deviations.get(servo_id, 0)
            pulse += deviation
            
            # Clamp
            pulse = max(500, min(2500, pulse))
            
            buf.append(servo_id)
            buf += list(pulse.to_bytes(2, 'little'))
        
        self._i2c_write(buf)
    
    # ===== Battery =====
    
    def get_battery(self) -> Optional[int]:
        """
        Get battery voltage.
        
        Returns:
            Voltage in millivolts, or None on error
        """
        data = self._i2c_read(REG_BATTERY, 2)
        if data and len(data) == 2:
            voltage = int.from_bytes(bytes(data), 'little')
            return voltage
        return None
    
    # ===== Buzzer =====
    
    def set_buzzer(self, freq_hz: int, on_s: float, off_s: float, repeat: int = 1):
        """
        Control buzzer.
        
        Note: Pi 4 buzzer is simple GPIO on/off (no frequency control).
        freq_hz parameter is accepted for API compatibility but ignored.
        
        Args:
            freq_hz: Ignored (GPIO buzzer has fixed frequency)
            on_s: On duration in seconds
            off_s: Off duration in seconds
            repeat: Number of beeps
        """
        if not _GPIO_AVAILABLE:
            return
        
        if not self._buzzer_initialized:
            GPIO.setup(BUZZER_PIN, GPIO.OUT)
            self._buzzer_initialized = True
        
        for _ in range(repeat):
            GPIO.output(BUZZER_PIN, True)
            time.sleep(on_s)
            GPIO.output(BUZZER_PIN, False)
            time.sleep(off_s)
    
    # ===== RGB LEDs =====
    
    def set_rgb(self, leds: List[Tuple[int, int, int, int]]):
        """
        Set RGB LED colors.
        
        Note: Pi 4 uses WS281x (NeoPixel) on GPIO 12.
        Requires root access for DMA.
        
        Args:
            leds: List of (led_id, r, g, b) tuples
                 led_id: 0-1
                 r, g, b: 0-255
        """
        try:
            from rpi_ws281x import PixelStrip, Color
            
            strip = PixelStrip(2, 12, 800000, 10, False, 120, 0)
            strip.begin()
            
            for led_id, r, g, b in leds:
                if 0 <= led_id <= 1:
                    strip.setPixelColor(led_id, Color(r, g, b))
            strip.show()
        except Exception:
            pass  # LEDs not critical, fail silently
    
    # ===== Cleanup =====
    
    def close(self):
        """Stop motors and clean up"""
        self.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        if _GPIO_AVAILABLE:
            try:
                GPIO.output(BUZZER_PIN, False)
            except Exception:
                pass


# Compatibility
Board = BoardController
