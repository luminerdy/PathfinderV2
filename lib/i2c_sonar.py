"""
I2C Ultrasonic Sensor
Clean-room implementation for I2C ultrasonic distance sensors with RGB LEDs.

Common I2C address: 0x77
Register layout discovered through testing and protocol analysis.
"""

from smbus2 import SMBus, i2c_msg
from typing import Tuple, Optional


class I2CSonar:
    """
    I2C ultrasonic distance sensor with RGB LEDs
    
    Features:
    - Distance measurement (millimeters)
    - Dual RGB LEDs
    - Breathing effect modes
    """
    
    # I2C Registers (discovered through testing)
    REG_DISTANCE_LSB = 0x00
    REG_DISTANCE_MSB = 0x01
    REG_RGB_MODE = 0x02
    REG_RGB1_R = 0x03
    REG_RGB1_G = 0x04
    REG_RGB1_B = 0x05
    REG_RGB2_R = 0x06
    REG_RGB2_G = 0x07
    REG_RGB2_B = 0x08
    REG_RGB1_R_BREATH = 0x09
    REG_RGB1_G_BREATH = 0x0A
    REG_RGB1_B_BREATH = 0x0B
    REG_RGB2_R_BREATH = 0x0C
    REG_RGB2_G_BREATH = 0x0D
    REG_RGB2_B_BREATH = 0x0E
    
    # RGB Modes
    MODE_STATIC = 0     # Static colors
    MODE_BREATHING = 1  # Breathing effect
    
    def __init__(self, i2c_bus: int = 1, address: int = 0x77):
        """
        Initialize I2C sonar sensor
        
        Args:
            i2c_bus: I2C bus number (1 for /dev/i2c-1)
            address: I2C device address (default 0x77)
        """
        self.i2c_bus = i2c_bus
        self.address = address
        self.pixels = [(0, 0, 0), (0, 0, 0)]  # RGB state for 2 LEDs
        
    def get_distance(self) -> Optional[int]:
        """
        Read ultrasonic distance measurement
        
        Returns:
            Distance in millimeters (0-5000) or None on error
        """
        try:
            with SMBus(self.i2c_bus) as bus:
                # Write register address
                msg_write = i2c_msg.write(self.address, [self.REG_DISTANCE_LSB])
                bus.i2c_rdwr(msg_write)
                
                # Read 2 bytes (16-bit little-endian distance)
                msg_read = i2c_msg.read(self.address, 2)
                bus.i2c_rdwr(msg_read)
                
                # Convert to distance
                data = list(msg_read)
                distance = int.from_bytes(bytes(data), byteorder='little', signed=False)
                
                # Clamp to valid range
                if distance > 5000:
                    distance = 5000
                    
                return distance
        except Exception as e:
            return None
            
    def set_rgb_mode(self, mode: int):
        """
        Set RGB LED mode
        
        Args:
            mode: 0=static, 1=breathing
        """
        try:
            with SMBus(self.i2c_bus) as bus:
                bus.write_byte_data(self.address, self.REG_RGB_MODE, mode)
        except Exception:
            pass
            
    def set_pixel_color(self, led_id: int, color: Tuple[int, int, int]):
        """
        Set RGB LED color
        
        Args:
            led_id: LED number (0 or 1)
            color: (R, G, B) tuple (0-255 each)
        """
        if led_id not in (0, 1):
            return
            
        r, g, b = color
        self.pixels[led_id] = (r, g, b)
        
        # Calculate register base (LED 0 = 0x03, LED 1 = 0x06)
        reg_base = self.REG_RGB1_R if led_id == 0 else self.REG_RGB2_R
        
        try:
            with SMBus(self.i2c_bus) as bus:
                bus.write_byte_data(self.address, reg_base, r & 0xFF)
                bus.write_byte_data(self.address, reg_base + 1, g & 0xFF)
                bus.write_byte_data(self.address, reg_base + 2, b & 0xFF)
        except Exception:
            pass
            
    def get_pixel_color(self, led_id: int) -> Tuple[int, int, int]:
        """
        Get current LED color from cache
        
        Args:
            led_id: LED number (0 or 1)
            
        Returns:
            (R, G, B) tuple
        """
        if led_id not in (0, 1):
            return (0, 0, 0)
        return self.pixels[led_id]
        
    def set_breath_cycle(self, led_id: int, channel: int, period_ms: int):
        """
        Set breathing effect period for a color channel
        
        Args:
            led_id: LED number (0 or 1)
            channel: Color channel (0=R, 1=G, 2=B)
            period_ms: Breathing period in milliseconds
        """
        if led_id not in (0, 1) or channel not in (0, 1, 2):
            return
            
        # Convert period to register value (units of 100ms)
        period_units = int(period_ms / 100)
        
        # Calculate register address
        if led_id == 0:
            reg_addr = self.REG_RGB1_R_BREATH + channel
        else:
            reg_addr = self.REG_RGB2_R_BREATH + channel
            
        try:
            with SMBus(self.i2c_bus) as bus:
                bus.write_byte_data(self.address, reg_addr, period_units & 0xFF)
        except Exception:
            pass
            
    def start_symphony(self):
        """
        Start a pre-configured breathing light show
        Different periods for each color channel create interesting effects
        """
        self.set_rgb_mode(self.MODE_BREATHING)
        
        # LED 1: Slow R, medium G, fast B
        self.set_breath_cycle(0, 0, 2000)  # R: 2 seconds
        self.set_breath_cycle(0, 1, 3300)  # G: 3.3 seconds
        self.set_breath_cycle(0, 2, 4700)  # B: 4.7 seconds
        
        # LED 2: Different pattern
        self.set_breath_cycle(1, 0, 4600)  # R: 4.6 seconds
        self.set_breath_cycle(1, 1, 2000)  # G: 2 seconds
        self.set_breath_cycle(1, 2, 3400)  # B: 3.4 seconds
        
    def show(self):
        """Compatibility method (no-op for I2C - changes are immediate)"""
        pass
        
    def num_pixels(self) -> int:
        """Return number of RGB LEDs"""
        return 2


# Compatibility alias
Sonar = I2CSonar
