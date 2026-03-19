"""
Sensor Monitor
Centralized sensor monitoring and safety system
"""

import time
import logging
import threading
from typing import Optional, Callable, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RobotState:
    """Current robot state from sensors"""
    battery_voltage: Optional[float] = None
    distance: Optional[float] = None
    imu_data: Optional[dict] = None
    gamepad_state: Optional[dict] = None
    timestamp: float = 0.0
    

class SensorMonitor:
    """
    Centralized sensor monitoring with safety callbacks
    """
    
    def __init__(self, board, sonar=None, update_rate: float = 10.0):
        """
        Initialize sensor monitor
        
        Args:
            board: Board instance
            sonar: Optional Sonar instance
            update_rate: Update frequency in Hz
        """
        self.board = board
        self.sonar = sonar
        self.update_rate = update_rate
        
        self._running = False
        self._thread = None
        self._state = RobotState()
        
        # Safety thresholds
        self.voltage_critical = 6.8
        self.voltage_warning = 7.0
        self.distance_critical = 10  # cm
        
        # Callbacks
        self._callbacks = {
            'low_battery': [],
            'critical_battery': [],
            'obstacle_detected': [],
            'state_update': []
        }
        
        logger.info("Sensor monitor initialized")
        
    # ===== Monitoring Control =====
    
    def start(self):
        """Start sensor monitoring"""
        if self._running:
            logger.warning("Sensor monitor already running")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        logger.info("Sensor monitor started")
        
    def stop(self):
        """Stop sensor monitoring"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("Sensor monitor stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        interval = 1.0 / self.update_rate
        
        while self._running:
            start = time.time()
            
            # Update all sensors
            self._update_sensors()
            
            # Check safety conditions
            self._check_safety()
            
            # Trigger state update callbacks
            self._trigger_callbacks('state_update', self._state)
            
            # Maintain update rate
            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)
                
    def _update_sensors(self):
        """Update all sensor readings"""
        self._state.timestamp = time.time()
        
        # Battery voltage
        voltage = self.board.get_battery_voltage()
        if voltage is not None:
            self._state.battery_voltage = voltage
            
        # Distance sensor
        if self.sonar:
            distance = self.sonar.get_distance()
            if distance is not None:
                self._state.distance = distance
                
        # IMU data
        imu = self.board.get_imu_data()
        if imu is not None:
            self._state.imu_data = imu
            
        # Gamepad state
        gamepad = self.board.get_gamepad_state()
        if gamepad is not None:
            self._state.gamepad_state = gamepad
            
    def _check_safety(self):
        """Check safety conditions and trigger alerts"""
        # Battery voltage check
        if self._state.battery_voltage is not None:
            if self._state.battery_voltage < self.voltage_critical:
                self._trigger_callbacks('critical_battery', self._state.battery_voltage)
            elif self._state.battery_voltage < self.voltage_warning:
                self._trigger_callbacks('low_battery', self._state.battery_voltage)
                
        # Obstacle detection
        if self._state.distance is not None:
            if self._state.distance < self.distance_critical:
                self._trigger_callbacks('obstacle_detected', self._state.distance)
                
    # ===== Callback Management =====
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register event callback
        
        Args:
            event: Event name ('low_battery', 'critical_battery', 
                   'obstacle_detected', 'state_update')
            callback: Callback function
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)
            logger.info(f"Registered callback for {event}")
        else:
            logger.warning(f"Unknown event: {event}")
            
    def unregister_callback(self, event: str, callback: Callable):
        """Unregister event callback"""
        if event in self._callbacks and callback in self._callbacks[event]:
            self._callbacks[event].remove(callback)
            
    def _trigger_callbacks(self, event: str, data):
        """Trigger all callbacks for event"""
        for callback in self._callbacks[event]:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in {event} callback: {e}")
                
    # ===== State Access =====
    
    def get_state(self) -> RobotState:
        """Get current robot state"""
        return self._state
        
    def get_battery_voltage(self) -> Optional[float]:
        """Get current battery voltage"""
        return self._state.battery_voltage
        
    def get_distance(self) -> Optional[float]:
        """Get current distance reading"""
        return self._state.distance
        
    def is_battery_low(self) -> bool:
        """Check if battery is low"""
        if self._state.battery_voltage is None:
            return False
        return self._state.battery_voltage < self.voltage_warning
        
    def is_battery_critical(self) -> bool:
        """Check if battery is critical"""
        if self._state.battery_voltage is None:
            return False
        return self._state.battery_voltage < self.voltage_critical
        
    def is_obstacle_detected(self) -> bool:
        """Check if obstacle is detected"""
        if self._state.distance is None:
            return False
        return self._state.distance < self.distance_critical
        
    # ===== Diagnostics =====
    
    def print_status(self):
        """Print current sensor status"""
        print("\n=== Robot Sensor Status ===")
        print(f"Battery: {self._state.battery_voltage:.2f}V" 
              if self._state.battery_voltage else "Battery: N/A")
        print(f"Distance: {self._state.distance:.1f}cm" 
              if self._state.distance else "Distance: N/A")
        print(f"IMU: {'Available' if self._state.imu_data else 'N/A'}")
        print(f"Gamepad: {'Connected' if self._state.gamepad_state else 'N/A'}")
        print(f"Updated: {time.time() - self._state.timestamp:.1f}s ago")
        print("=" * 27 + "\n")
        
    def get_diagnostics(self) -> Dict:
        """
        Get diagnostic information
        
        Returns:
            Dict with sensor status
        """
        return {
            'battery_voltage': self._state.battery_voltage,
            'battery_low': self.is_battery_low(),
            'battery_critical': self.is_battery_critical(),
            'distance': self._state.distance,
            'obstacle_detected': self.is_obstacle_detected(),
            'imu_available': self._state.imu_data is not None,
            'gamepad_connected': self._state.gamepad_state is not None,
            'update_age': time.time() - self._state.timestamp,
            'running': self._running
        }
        
    # ===== Context Manager =====
    
    def __enter__(self):
        self.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
