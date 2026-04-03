"""
Robot — Single Robot Instance

The ONE object that owns all hardware. Pass it to skills.

Usage:
    from robot import Robot
    
    robot = Robot()
    robot.drive(30, 30, 30, 30)   # Forward
    robot.stop()                   # Stop
    robot.arm.camera_forward()     # Arm pose
    frame = robot.camera.get_frame()  # Camera
    dist = robot.sonar.get_distance() # Sonar
    print(robot.battery)           # Voltage
    robot.shutdown()               # Clean exit

Context manager:
    with Robot() as robot:
        robot.arm.camera_forward()
        robot.drive(30, 30, 30, 30)
        time.sleep(1)
    # auto-shutdown on exit

Skills pattern:
    from robot import Robot
    from skills.bump_grab import bump_grab
    
    robot = Robot()
    try:
        bump_grab(robot, color='red')
        robot.arm.backward_drop()
    finally:
        robot.shutdown()
"""

import time
from lib.board import get_board, PLATFORM


class Robot:
    """
    Single robot instance owning all hardware.
    
    Create once, pass to skills. Skills should never create
    their own board, camera, or sonar.
    """
    
    def __init__(self, enable_camera=True, enable_sonar=True,
                 calibration_path=None):
        """
        Initialize robot hardware.
        
        Args:
            enable_camera: Open camera on init
            enable_sonar: Initialize sonar on init
            calibration_path: Path to camera calibration .npz file
        """
        self.platform = PLATFORM
        self.board = get_board()
        
        # Wait for board to stabilize
        time.sleep(0.5)
        
        # Arm controller (always available)
        from lib.arm_positions import Arm
        self.arm = Arm(self.board)
        
        # Camera (optional)
        self._camera = None
        self._camera_enabled = enable_camera
        self._calibration_path = calibration_path
        if enable_camera:
            self._init_camera()
        
        # Sonar (optional)
        self._sonar = None
        self._sonar_enabled = enable_sonar
        if enable_sonar:
            self._init_sonar()
        
        # Battery thresholds
        self.battery_min = 7.0 if PLATFORM == 'pi4' else 8.1
        
        # Startup beep
        self._beep(0.1)
    
    def _init_camera(self):
        """Initialize camera."""
        try:
            from lib.camera import Camera
            self._camera = Camera(calibration_path=self._calibration_path)
            self._camera.open()
        except Exception as e:
            print("Camera init failed: %s" % e)
            self._camera = None
    
    def _init_sonar(self):
        """Initialize sonar."""
        try:
            from lib.sonar import Sonar
            self._sonar = Sonar()
        except Exception as e:
            print("Sonar init failed: %s" % e)
            self._sonar = None
    
    def _beep(self, duration=0.1):
        """Short beep."""
        try:
            self.board.set_buzzer(1)
            time.sleep(duration)
            self.board.set_buzzer(0)
        except Exception:
            pass
    
    # === PROPERTIES ===
    
    @property
    def camera(self):
        """Camera instance (lazy init if needed)."""
        if self._camera is None and self._camera_enabled:
            self._init_camera()
        return self._camera
    
    @property
    def sonar(self):
        """Sonar instance."""
        return self._sonar
    
    @property
    def battery(self):
        """Battery voltage (float) or None."""
        mv = self.board.get_battery()
        if mv and 5000 < mv < 20000:
            return mv / 1000.0
        return None
    
    @property
    def battery_ok(self):
        """True if battery is above minimum threshold."""
        v = self.battery
        return v is not None and v >= self.battery_min
    
    # === DRIVE ===
    
    def drive(self, fl, fr, rl, rr):
        """
        Set motor speeds directly.
        
        Args:
            fl: Front-left motor duty (-100 to 100)
            fr: Front-right motor duty
            rl: Rear-left motor duty
            rr: Rear-right motor duty
        """
        self.board.set_motor_duty([(1, fl), (2, fr), (3, rl), (4, rr)])
    
    def stop(self):
        """Stop all motors immediately."""
        self.board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
    
    def forward(self, power=35):
        """Drive forward."""
        self.drive(power, power, power, power)
    
    def backward(self, power=35):
        """Drive backward."""
        self.drive(-power, -power, -power, -power)
    
    def rotate_left(self, power=35):
        """Rotate left in place."""
        self.drive(-power, power, -power, power)
    
    def rotate_right(self, power=35):
        """Rotate right in place."""
        self.drive(power, -power, power, -power)
    
    def strafe_left(self, power=35):
        """Strafe left (mecanum)."""
        self.drive(-power, power, power, -power)
    
    def strafe_right(self, power=35):
        """Strafe right (mecanum)."""
        self.drive(power, -power, -power, power)
    
    # === STATUS ===
    
    def status(self):
        """Print robot status."""
        print("=" * 40)
        print("  Robot Status (%s)" % self.platform)
        print("=" * 40)
        
        v = self.battery
        if v:
            status = "OK" if v >= self.battery_min else "LOW"
            print("  Battery: %.2fV (%s)" % (v, status))
        else:
            print("  Battery: unknown")
        
        if self._camera:
            print("  Camera: %s" % ("open" if self._camera.is_open() else "closed"))
            if self._camera.calibrated:
                print("  Camera cal: fx=%.0f fy=%.0f" % (self._camera.fx, self._camera.fy))
            else:
                print("  Camera cal: estimated (fx=500)")
        else:
            print("  Camera: disabled")
        
        if self._sonar:
            d = self._sonar.get_distance()
            if d:
                print("  Sonar: %dmm (%.1fcm)" % (d, d/10.0))
            else:
                print("  Sonar: no reading")
        else:
            print("  Sonar: disabled")
        
        print("=" * 40)
    
    # === LIFECYCLE ===
    
    def shutdown(self):
        """Clean shutdown — stop motors, release camera, LEDs off."""
        self.stop()
        
        if self._camera:
            self._camera.release()
            self._camera = None
        
        if self._sonar:
            self._sonar.off()
        
        self._beep(0.05)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
    
    def __del__(self):
        try:
            self.stop()
        except Exception:
            pass
