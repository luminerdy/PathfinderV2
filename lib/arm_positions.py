"""
Arm Positions — Single Source of Truth

All servo positions and arm sequences in one place.
Vendor-tested positions from PathfinderBot V1 + our own calibrations.

Servo IDs:
    1 = Gripper      (1475=closed, 2500=open)
    3 = Shoulder      (500-2500)
    4 = Elbow         (500-2500)
    5 = Wrist         (500-2500)
    6 = Base rotation  (500=right, 1500=center, 2500=left)

Usage:
    from lib.arm_positions import Arm
    arm = Arm(board)
    arm.camera_forward()
    arm.pickup_front()
    arm.backward_drop()
"""

import time


# === STATIC POSITIONS ===
# Format: [(servo_id, pulse_width), ...]

# Camera / navigation poses
POS_CAMERA_FORWARD = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
POS_CAMERA_DOWN    = [(1, 2500), (3, 590), (4, 2450), (5, 1214), (6, 1500)]

# Carry (block in gripper, arm up)
POS_CARRY = [(1, 1475), (3, 569), (4, 2400), (5, 809), (6, 1500)]

# Pickup from ground (gripper open, arm down)
POS_PICKUP_DOWN = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_PICKUP_GRAB = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_LIFT        = [(1, 1475), (3, 590), (4, 2450), (5, 700), (6, 1500)]

# Gentle place (lower block to floor, release)
POS_PLACE_DOWN = [(1, 1475), (3, 830), (4, 2170), (5, 2410), (6, 1500)]
POS_PLACE_OPEN = [(1, 2500), (3, 830), (4, 2170), (5, 2410), (6, 1500)]

# Backward drop into bin (folds arm over chassis)
POS_BACKWARD_FOLD = [(1, 1500), (3, 2400), (4, 700), (5, 1700), (6, 1500)]
POS_BACKWARD_DROP = [(1, 2020), (3, 2400), (4, 700), (5, 1700), (6, 1500)]

# Look forward (V1 vendor reset pose)
POS_LOOK_FORWARD = [(1, 1500), (3, 700), (4, 2425), (5, 790), (6, 1500)]

# Expressions
POS_LOOK_SAD = [(3, 800), (4, 2500), (5, 1900), (6, 1500)]


class Arm:
    """
    Arm controller with named positions and sequences.
    
    All servo positions defined here — no magic numbers in skill files.
    """
    
    def __init__(self, board):
        self.board = board
    
    def move(self, position, duration_ms=800):
        """Move to a position and wait for completion."""
        self.board.set_servo_position(duration_ms, position)
        time.sleep(duration_ms / 1000.0 + 0.1)
    
    def move_servo(self, servo_id, pulse, duration_ms=500):
        """Move a single servo."""
        self.board.set_servo_position(duration_ms, [(servo_id, pulse)])
        time.sleep(duration_ms / 1000.0 + 0.1)
    
    # === POSES ===
    
    def camera_forward(self):
        """Camera facing forward — default navigation pose."""
        self.move(POS_CAMERA_FORWARD, 800)
    
    def camera_down(self):
        """Camera tilted down — for close block inspection."""
        self.move(POS_CAMERA_DOWN, 800)
    
    def carry(self):
        """Carry position — block in gripper, arm up."""
        self.move(POS_CARRY, 800)
    
    def look_forward(self):
        """V1 vendor forward pose (slightly different from camera_forward)."""
        self.move_servo(1, 1500, 500)
        self.move_servo(3, 700, 1000)
        self.move_servo(4, 2425, 1000)
        self.move_servo(5, 790, 1000)
        self.move_servo(6, 1500, 1000)
    
    # === GRIPPER ===
    
    def gripper_open(self, duration_ms=400):
        """Open gripper."""
        self.move_servo(1, 2500, duration_ms)
    
    def gripper_close(self, duration_ms=400):
        """Close gripper on block."""
        self.move_servo(1, 1475, duration_ms)
    
    # === PICKUP SEQUENCES ===
    
    def pickup_front(self):
        """
        Front pickup — reach down, grab block, lift.
        
        Vendor-tested sequence from PathfinderBot V1.
        Robot must be positioned with block directly in front.
        """
        # Start from forward pose
        self.board.set_servo_position(2000, [(1, 1500)])
        self.board.set_servo_position(2000, [(3, 590)])
        self.board.set_servo_position(2000, [(4, 2500)])
        self.board.set_servo_position(2000, [(5, 700)])
        self.board.set_servo_position(2000, [(6, 1500)])
        
        # Lower wrist toward ground
        self.board.set_servo_position(1000, [(5, 1818)])
        time.sleep(1)
        
        # Position for grab
        self.board.set_servo_position(300, [(4, 2023)])
        self.board.set_servo_position(300, [(5, 2091)])
        time.sleep(0.3)
        
        # Open gripper wide
        self.board.set_servo_position(400, [(1, 1932)])
        time.sleep(0.4)
        
        # Lower shoulder, extend to block
        self.board.set_servo_position(800, [(3, 750)])
        self.board.set_servo_position(800, [(5, 2364)])
        time.sleep(0.8)
        
        # Close gripper
        self.board.set_servo_position(300, [(1, 1455)])
        self.board.set_servo_position(300, [(5, 2318)])
        time.sleep(0.3)
        
        # Lift
        self.board.set_servo_position(1000, [(5, 1841)])
        time.sleep(1)
        
        self.look_forward()
    
    def pickup_left(self):
        """Pick up block from left side (base rotates left)."""
        self.board.set_servo_position(1000, [(1, 2020)])
        self.board.set_servo_position(1000, [(3, 800)])
        self.board.set_servo_position(1000, [(4, 2020)])
        self.board.set_servo_position(1000, [(5, 2091)])
        self.board.set_servo_position(1000, [(6, 2500)])
        time.sleep(1)
        
        self.board.set_servo_position(800, [(3, 900)])
        self.board.set_servo_position(800, [(5, 2364)])
        time.sleep(0.8)
        
        self.board.set_servo_position(500, [(1, 1455)])
        self.board.set_servo_position(300, [(5, 2300)])
        time.sleep(0.3)
        
        self.board.set_servo_position(1000, [(5, 1841)])
        time.sleep(1)
        
        self.look_forward()
    
    def pickup_right(self):
        """Pick up block from right side (base rotates right)."""
        self.board.set_servo_position(1000, [(1, 2020)])
        self.board.set_servo_position(1000, [(3, 800)])
        self.board.set_servo_position(1000, [(4, 1800)])
        self.board.set_servo_position(1000, [(5, 2091)])
        self.board.set_servo_position(1000, [(6, 500)])
        time.sleep(1)
        
        self.board.set_servo_position(800, [(3, 800)])
        self.board.set_servo_position(800, [(5, 2450)])
        time.sleep(0.8)
        
        self.board.set_servo_position(500, [(1, 1455)])
        self.board.set_servo_position(300, [(5, 2318)])
        time.sleep(0.3)
        
        self.board.set_servo_position(1000, [(5, 1841)])
        time.sleep(1)
        
        self.look_forward()
    
    # === DROP/PLACE SEQUENCES ===
    
    def backward_drop(self):
        """
        Drop block into rear-mounted bin.
        
        Folds arm backward over chassis. No base rotation needed.
        Vendor-tested from PathfinderBot V1.
        """
        self.board.set_servo_position(2000, [(1, 1500)])
        self.board.set_servo_position(2000, [(3, 2400)])
        self.board.set_servo_position(2000, [(4, 700)])
        self.board.set_servo_position(2000, [(5, 1700)])
        time.sleep(2)
        
        self.board.set_servo_position(2000, [(1, 2020)])
        time.sleep(2.1)
        
        self.look_forward()
    
    def gentle_place(self):
        """
        Place block gently on the floor.
        
        Lower arm with block, open gripper at ground level, retract.
        No bounce — works on rubber tiles.
        """
        self.move(POS_PLACE_DOWN, 1200)
        time.sleep(0.3)
        self.move(POS_PLACE_OPEN, 500)
        time.sleep(0.3)
        self.move(POS_CAMERA_FORWARD, 1000)
    
    # === EXPRESSIONS ===
    
    def look_sad(self):
        """Sad expression — arm droops."""
        self.board.set_servo_position(1000, [(3, 800)])
        self.board.set_servo_position(1000, [(4, 2500)])
        self.board.set_servo_position(1000, [(5, 1900)])
        self.board.set_servo_position(1000, [(6, 1500)])
        time.sleep(0.5)
        self.board.set_servo_position(1000, [(3, 600)])
    
    def say_yes(self):
        """Nod up and down."""
        self.board.set_servo_position(1000, [(4, 2425)])
        self.board.set_servo_position(1000, [(5, 790)])
        self.board.set_servo_position(2000, [(3, 590)])
        time.sleep(0.2)
        for _ in range(3):
            self.board.set_servo_position(200, [(3, 500)])
            time.sleep(0.2)
            self.board.set_servo_position(200, [(3, 900)])
            time.sleep(0.2)
        self.board.set_servo_position(200, [(3, 700)])
    
    def say_no(self):
        """Shake side to side."""
        self.board.set_servo_position(1000, [(4, 2425)])
        self.board.set_servo_position(1000, [(5, 790)])
        time.sleep(0.2)
        for _ in range(3):
            self.board.set_servo_position(200, [(6, 1300)])
            time.sleep(0.2)
            self.board.set_servo_position(200, [(6, 1700)])
            time.sleep(0.2)
        self.board.set_servo_position(200, [(6, 1500)])
        time.sleep(0.2)
