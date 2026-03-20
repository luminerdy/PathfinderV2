"""
Board Communication Protocol
Clean-room implementation of serial protocol for robot control boards.

Protocol Documentation:
- Serial: 1000000 baud, 8N1
- Packet format: [0xAA, 0x55, function, length, data..., checksum]
- Checksum: CRC-8 of [function, length, data...]

Created from protocol analysis and testing, no vendor code used.
"""

import struct
import serial
import threading
import queue
from enum import IntEnum
from typing import List, Tuple, Optional


class Function(IntEnum):
    """Command function codes"""
    SYS = 0             # System reports (battery, etc.)
    LED = 1             # LED control
    BUZZER = 2          # Buzzer control
    MOTOR = 3           # Motor speed/duty control
    SERVO = 4           # PWM servo position
    BUS_SERVO = 5       # Bus servo
    KEY = 6             # Key/button
    IMU = 7             # IMU data
    GAMEPAD = 8         # Gamepad
    SBUS = 9            # SBUS
    OLED = 10           # OLED
    RGB = 11            # RGB (custom - check actual value)
    

CRC8_TABLE = [
    0, 94, 188, 226, 97, 63, 221, 131, 194, 156, 126, 32, 163, 253, 31, 65,
    157, 195, 33, 127, 252, 162, 64, 30, 95, 1, 227, 189, 62, 96, 130, 220,
    35, 125, 159, 193, 66, 28, 254, 160, 225, 191, 93, 3, 128, 222, 60, 98,
    190, 224, 2, 92, 223, 129, 99, 61, 124, 34, 192, 158, 29, 67, 161, 255,
    70, 24, 250, 164, 39, 121, 155, 197, 132, 218, 56, 102, 229, 187, 89, 7,
    219, 133, 103, 57, 186, 228, 6, 88, 25, 71, 165, 251, 120, 38, 196, 154,
    101, 59, 217, 135, 4, 90, 184, 230, 167, 249, 27, 69, 198, 152, 122, 36,
    248, 166, 68, 26, 153, 199, 37, 123, 58, 100, 134, 216, 91, 5, 231, 185,
    140, 210, 48, 110, 237, 179, 81, 15, 78, 16, 242, 172, 47, 113, 147, 205,
    17, 79, 173, 243, 112, 46, 204, 146, 211, 141, 111, 49, 178, 236, 14, 80,
    175, 241, 19, 77, 206, 144, 114, 44, 109, 51, 209, 143, 12, 82, 176, 238,
    50, 108, 142, 208, 83, 13, 239, 177, 240, 174, 76, 18, 145, 207, 45, 115,
    202, 148, 118, 40, 171, 245, 23, 73, 8, 86, 180, 234, 105, 55, 213, 139,
    87, 9, 235, 181, 54, 104, 138, 212, 149, 203, 41, 119, 244, 170, 72, 22,
    233, 183, 85, 11, 136, 214, 52, 106, 43, 117, 151, 201, 74, 20, 246, 168,
    116, 42, 200, 150, 21, 75, 169, 247, 182, 232, 10, 84, 215, 137, 107, 53
]


def crc8(data: bytes) -> int:
    """
    Calculate CRC-8 checksum using lookup table
    (Standard CRC-8/MAXIM polynomial)
    """
    check = 0
    for byte in data:
        check = CRC8_TABLE[check ^ byte]
    return check & 0xFF


class BoardProtocol:
    """
    Low-level serial protocol for robot control board
    """
    
    HEADER = bytes([0xAA, 0x55])
    
    def __init__(self, port: str = "/dev/ttyAMA0", baudrate: int = 1000000):
        """
        Initialize serial connection
        
        Args:
            port: Serial device path
            baudrate: Communication speed
        """
        self.port = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.1
        )
        
        self._read_thread = None
        self._running = False
        self._rx_queue = queue.Queue(maxsize=100)
        
    def start_reception(self):
        """Start background thread for receiving responses"""
        if not self._running:
            self._running = True
            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            
    def stop_reception(self):
        """Stop reception thread"""
        self._running = False
        if self._read_thread:
            self._read_thread.join(timeout=1.0)
            
    def _read_loop(self):
        """Background thread for reading responses"""
        while self._running:
            try:
                if self.port.in_waiting > 0:
                    # Read header
                    header = self.port.read(2)
                    if header != self.HEADER:
                        continue
                        
                    # Read function and length
                    func = self.port.read(1)[0]
                    length = self.port.read(1)[0]
                    
                    # Read data and checksum
                    data = self.port.read(length)
                    checksum = self.port.read(1)[0]
                    
                    # Verify checksum
                    payload = bytes([func, length]) + data
                    if crc8(payload) == checksum:
                        self._rx_queue.put((func, data))
            except Exception:
                pass  # Continue on errors
                
    def send_command(self, function: int, data: bytes):
        """
        Send command packet
        
        Args:
            function: Command function code
            data: Command data bytes
        """
        # Build packet
        packet = self.HEADER
        packet += bytes([function, len(data)])
        packet += data
        
        # Add checksum
        payload = bytes([function, len(data)]) + data
        packet += bytes([crc8(payload)])
        
        # Send
        self.port.write(packet)
        self.port.flush()
        
    def read_response(self, timeout: float = 0.1) -> Optional[Tuple[int, bytes]]:
        """
        Read response packet
        
        Args:
            timeout: Maximum wait time
            
        Returns:
            (function, data) tuple or None
        """
        try:
            return self._rx_queue.get(timeout=timeout)
        except queue.Empty:
            return None
            
    def close(self):
        """Close serial connection"""
        self.stop_reception()
        if self.port.is_open:
            self.port.close()


class BoardController:
    """
    High-level control interface for robot board
    """
    
    def __init__(self, port: str = "/dev/ttyAMA0", baudrate: int = 1000000):
        """Initialize board controller"""
        self.protocol = BoardProtocol(port, baudrate)
        self.protocol.start_reception()
        
    # ===== Motor Control =====
    
    def set_motor_duty(self, motors: List[Tuple[int, float]]):
        """
        Set motor duty cycles
        
        Args:
            motors: List of (motor_id, duty) tuples
                   motor_id: 1-4
                   duty: -100 to 100 (negative = reverse)
        """
        data = bytes([0x05, len(motors)])  # Sub-command 0x05 = duty cycle
        for motor_id, duty in motors:
            # Pack motor index (0-based) and duty as float
            data += struct.pack("<Bf", motor_id - 1, float(duty))
        self.protocol.send_command(Function.MOTOR, data)
        
    def set_motor_speed(self, motors: List[Tuple[int, float]]):
        """
        Set motor speeds (alternative command)
        
        Args:
            motors: List of (motor_id, speed) tuples
        """
        data = bytes([0x01, len(motors)])  # Sub-command 0x01 = speed
        for motor_id, speed in motors:
            data += struct.pack("<Bf", motor_id - 1, float(speed))
        self.protocol.send_command(Function.MOTOR, data)
        
    # ===== Servo Control =====
    
    def set_servo_position(self, duration_ms: int, servos: List[Tuple[int, int]]):
        """
        Set servo positions
        
        Args:
            duration_ms: Movement duration in milliseconds
            servos: List of (servo_id, pulse_width) tuples
                   servo_id: 1-6 (typically)
                   pulse_width: 500-2500 (1500 = center)
        """
        data = bytes([0x01])  # Sub-command 0x01 = set position
        data += struct.pack("<H", duration_ms)  # Duration (16-bit little-endian)
        data += bytes([len(servos)])
        
        for servo_id, pulse in servos:
            data += struct.pack("<BH", servo_id, pulse)
            
        self.protocol.send_command(Function.SERVO, data)
        
    # ===== RGB LED Control =====
    
    def set_rgb(self, leds: List[Tuple[int, int, int, int]]):
        """
        Set RGB LED colors
        
        Args:
            leds: List of (led_id, r, g, b) tuples
                 led_id: 1-2 (typically)
                 r, g, b: 0-255
        """
        data = bytes([0x01, len(leds)])  # Sub-command 0x01 = set color
        for led_id, r, g, b in leds:
            data += struct.pack("<BBBB", led_id - 1, int(r), int(g), int(b))
        self.protocol.send_command(Function.RGB, data)
        
    # ===== Buzzer Control =====
    
    def set_buzzer(self, freq_hz: int, on_ms: float, off_ms: float, repeat: int = 1):
        """
        Control buzzer
        
        Args:
            freq_hz: Frequency in Hz
            on_ms: On duration in seconds (converted to ms internally)
            off_ms: Off duration in seconds (converted to ms internally)
            repeat: Number of times to repeat
        """
        on_time = int(on_ms * 1000)
        off_time = int(off_ms * 1000)
        data = struct.pack("<HHHH", freq_hz, on_time, off_time, repeat)
        self.protocol.send_command(Function.BUZZER, data)
        
    # ===== Sensors =====
    
    def get_battery(self) -> Optional[int]:
        """
        Get battery voltage
        
        Board sends battery data periodically in SYS packets.
        Sub-command 0x04 contains battery voltage.
        
        Returns:
            Voltage in millivolts or None
        """
        # Read recent SYS packets
        for _ in range(10):  # Check recent packets
            response = self.protocol.read_response(timeout=0.1)
            if response and response[0] == Function.SYS:
                data = response[1]
                if len(data) >= 3 and data[0] == 0x04:  # Sub-command 0x04 = battery
                    # Battery voltage as 16-bit little-endian
                    voltage = struct.unpack("<H", data[1:3])[0]
                    return voltage
        return None
        
    # ===== Cleanup =====
    
    def close(self):
        """Close connection"""
        # Stop all motors
        self.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        self.protocol.close()


# Compatibility alias (for drop-in replacement)
Board = BoardController
