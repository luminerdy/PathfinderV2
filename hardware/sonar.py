"""
Ultrasonic Sonar Sensor
Distance measurement using HC-SR04 or similar ultrasonic sensor
"""

import sys
import time
import logging
from typing import Optional, Tuple

from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from sdk.common.sonar import Sonar as BaseSonar

logger = logging.getLogger(__name__)


class Sonar:
    """
    Ultrasonic distance sensor with RGB indicator LEDs
    """
    
    def __init__(self, max_distance: float = 400):
        """
        Initialize sonar sensor
        
        Args:
            max_distance: Maximum measurable distance in cm
        """
        self._sonar = BaseSonar()
        self.max_distance = max_distance
        self._last_distance = None
        
        # Turn off RGB LEDs initially
        self._sonar.setRGBMode(0)
        self._sonar.setPixelColor(0, (0, 0, 0))
        self._sonar.setPixelColor(1, (0, 0, 0))
        self._sonar.show()
        
        logger.info("Sonar initialized")
        
    # ===== Distance Measurement =====
    
    def get_distance(self) -> Optional[float]:
        """
        Get distance measurement
        
        Returns:
            Distance in cm, or None if measurement failed
        """
        try:
            distance = self._sonar.getDistance()
            
            # Filter invalid readings
            if distance is None or distance < 2 or distance > self.max_distance:
                return None
                
            self._last_distance = distance
            return distance
            
        except Exception as e:
            logger.error(f"Error reading sonar: {e}")
            return None
            
    def get_filtered_distance(self, samples: int = 5) -> Optional[float]:
        """
        Get filtered distance (median of multiple samples)
        
        Args:
            samples: Number of samples to take
            
        Returns:
            Median distance in cm
        """
        measurements = []
        
        for _ in range(samples):
            dist = self.get_distance()
            if dist is not None:
                measurements.append(dist)
            time.sleep(0.02)  # Small delay between samples
            
        if not measurements:
            return None
            
        # Return median
        measurements.sort()
        return measurements[len(measurements) // 2]
        
    @property
    def distance(self) -> Optional[float]:
        """Last measured distance"""
        return self._last_distance
        
    # ===== Detection Methods =====
    
    def is_obstacle_detected(self, threshold: float = 20) -> bool:
        """
        Check if obstacle is within threshold distance
        
        Args:
            threshold: Detection threshold in cm
            
        Returns:
            True if obstacle detected
        """
        dist = self.get_distance()
        return dist is not None and dist < threshold
        
    def wait_for_clear(self, threshold: float = 30, timeout: float = 10) -> bool:
        """
        Wait until path is clear
        
        Args:
            threshold: Clearance threshold in cm
            timeout: Maximum wait time in seconds
            
        Returns:
            True if clear, False if timeout
        """
        start = time.time()
        
        while time.time() - start < timeout:
            dist = self.get_distance()
            if dist is None or dist > threshold:
                return True
            time.sleep(0.1)
            
        return False
        
    def detect_motion(self, threshold: float = 5, duration: float = 2) -> bool:
        """
        Detect motion by monitoring distance changes
        
        Args:
            threshold: Motion detection threshold in cm
            duration: Monitoring duration in seconds
            
        Returns:
            True if motion detected
        """
        initial = self.get_filtered_distance()
        if initial is None:
            return False
            
        time.sleep(duration)
        
        final = self.get_filtered_distance()
        if final is None:
            return False
            
        return abs(final - initial) > threshold
        
    # ===== RGB LED Control =====
    
    def set_rgb(self, led: int, color: Tuple[int, int, int]):
        """
        Set RGB LED color
        
        Args:
            led: LED index (0 or 1)
            color: (R, G, B) tuple (0-255)
        """
        self._sonar.setPixelColor(led, color)
        self._sonar.show()
        
    def set_both_rgb(self, color: Tuple[int, int, int]):
        """Set both RGB LEDs to same color"""
        self._sonar.setPixelColor(0, color)
        self._sonar.setPixelColor(1, color)
        self._sonar.show()
        
    def rgb_off(self):
        """Turn off RGB LEDs"""
        self.set_both_rgb((0, 0, 0))
        
    def set_distance_indicator(self):
        """
        Set RGB color based on distance (traffic light style)
        Green = far, Yellow = medium, Red = close
        """
        dist = self.get_distance()
        
        if dist is None:
            color = (0, 0, 0)  # Off if no reading
        elif dist > 50:
            color = (0, 255, 0)  # Green - clear
        elif dist > 20:
            color = (255, 255, 0)  # Yellow - caution
        else:
            color = (255, 0, 0)  # Red - obstacle
            
        self.set_both_rgb(color)
        
    # ===== Cleanup =====
    
    def close(self):
        """Clean up sonar resources"""
        self.rgb_off()
        logger.info("Sonar closed")
