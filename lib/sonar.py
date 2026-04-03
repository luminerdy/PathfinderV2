"""
Sonar — Unified Sonar Access

Single import point for the ultrasonic sensor.
Wraps I2CSonar with a simpler interface and distance-zone LED feedback.

Usage:
    from lib.sonar import Sonar
    sonar = Sonar()
    dist = sonar.get_distance()       # millimeters
    sonar.set_led_color(0, 255, 0)    # green
"""

from lib.i2c_sonar import I2CSonar


# Distance zones (mm) for LED feedback
ZONE_SAFE = 610       # > 24 inches = green
ZONE_CAUTION = 305    # 12-24 inches = yellow
ZONE_DANGER = 150     # < 6 inches = red
# Below ZONE_DANGER = critical (flashing red)


class Sonar:
    """
    Ultrasonic distance sensor with RGB LEDs.
    
    Wraps the I2C sonar module with a clean interface.
    Use this instead of importing from sdk.common, hardware, etc.
    """
    
    def __init__(self, i2c_bus=1, address=0x77):
        self._sonar = I2CSonar(i2c_bus=i2c_bus, address=address)
        self._sonar.set_rgb_mode(0)  # Static LED mode
    
    def get_distance(self):
        """
        Read distance in millimeters.
        
        Returns:
            Distance in mm (0-5000), or None on error.
        """
        return self._sonar.get_distance()
    
    def get_distance_cm(self):
        """
        Read distance in centimeters.
        
        Returns:
            Distance in cm (0-500), or None on error.
        """
        d = self._sonar.get_distance()
        return d / 10.0 if d is not None else None
    
    def set_led_color(self, r, g, b):
        """Set both sonar LEDs to the same color."""
        self._sonar.set_pixel_color(0, (r, g, b))
        self._sonar.set_pixel_color(1, (r, g, b))
    
    def set_led_by_distance(self, distance_mm):
        """
        Set LED color based on distance zone.
        
        Green = safe, Yellow = caution, Red = danger.
        
        Args:
            distance_mm: Distance in millimeters
        """
        if distance_mm is None:
            self.set_led_color(0, 0, 0)  # Off if no reading
        elif distance_mm >= ZONE_SAFE:
            self.set_led_color(0, 255, 0)      # Green
        elif distance_mm >= ZONE_CAUTION:
            self.set_led_color(255, 255, 0)    # Yellow
        elif distance_mm >= ZONE_DANGER:
            self.set_led_color(255, 0, 0)      # Red
        else:
            self.set_led_color(255, 0, 0)      # Red (critical)
    
    def update_leds(self):
        """Read distance and set LEDs automatically."""
        d = self.get_distance()
        self.set_led_by_distance(d)
        return d
    
    def off(self):
        """Turn off sonar LEDs."""
        self.set_led_color(0, 0, 0)
    
    def close(self):
        """Clean shutdown."""
        self.off()
