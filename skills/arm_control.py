#!/usr/bin/env python3
"""
Arm Control Skill — Smooth Multi-Servo Movement

Moves all arm servos simultaneously for smooth, coordinated motion.
Supports named positions, action sequences, and interpolated transitions.

Servo Mapping (verified):
    1: Claw/Gripper (1475=closed, 2500=open)
    3: Wrist
    4: Elbow
    5: Shoulder
    6: Base rotation (1500=center/forward)
    (Servo 2 does not exist)
"""

import time
import json
from pathlib import Path
from lib.board_protocol import BoardController


# All servo IDs on this robot
SERVO_IDS = [1, 3, 4, 5, 6]

# Named positions: {name: {servo_id: pulse_width}}
POSITIONS = {
    'camera_forward': {1: 2500, 3: 590, 4: 2450, 5: 700, 6: 1500},
    'camera_down':    {1: 2500, 3: 590, 4: 2450, 5: 1214, 6: 1500},
    'block_close':    {1: 2500, 3: 590, 4: 2450, 5: 1694, 6: 1500},
    'pickup_ready':   {1: 1558, 3: 830, 4: 2170, 5: 2410, 6: 1500},
    'pickup_grab':    {1: 1475, 3: 830, 4: 2170, 5: 2410, 6: 1500},
    'pickup_lift':    {1: 1475, 3: 590, 4: 2450, 5: 700, 6: 1500},
    'gripper_open':   {1: 2500},
    'gripper_closed': {1: 1475},
    'rest':           {1: 2500, 3: 1500, 4: 1500, 5: 1500, 6: 1500},
}

# Action sequences: list of (position_dict, duration_ms)
SEQUENCES = {
    'pickup_ready': [
        # From block_close, lower arm to block (tested positions)
        ({1: 2500, 3: 830, 4: 2170, 5: 2410, 6: 1500}, 1000),  # Arm down to block, gripper open
        ({1: 1558, 3: 830, 4: 2170, 5: 2410, 6: 1500}, 300),   # Partially close around block
    ],
    'pickup_grab': [
        ({1: 1475, 3: 830, 4: 2170, 5: 2410, 6: 1500}, 400),  # Grip tight
    ],
    'pickup_lift': [
        ({1: 1475, 3: 590, 4: 2450, 5: 700, 6: 1500}, 1000),  # Lift to camera forward (carrying)
    ],
    'drop': [
        ({1: 2500}, 400),  # Open gripper
    ],
    'wave': [
        ({1: 1475, 3: 590, 4: 2000, 5: 500, 6: 1500}, 500),
        ({1: 1475, 3: 590, 4: 2000, 5: 500, 6: 1200}, 300),
        ({1: 1475, 3: 590, 4: 2000, 5: 500, 6: 1800}, 300),
        ({1: 1475, 3: 590, 4: 2000, 5: 500, 6: 1200}, 300),
        ({1: 1475, 3: 590, 4: 2000, 5: 500, 6: 1800}, 300),
        ({1: 1475, 3: 590, 4: 2450, 5: 700, 6: 1500}, 500),
    ],
    'nod_yes': [
        ({3: 590, 4: 2450, 5: 700}, 300),
        ({3: 590, 4: 2200, 5: 900}, 250),
        ({3: 590, 4: 2450, 5: 700}, 250),
        ({3: 590, 4: 2200, 5: 900}, 250),
        ({3: 590, 4: 2450, 5: 700}, 300),
    ],
    'shake_no': [
        ({6: 1500}, 200),
        ({6: 1200}, 250),
        ({6: 1800}, 250),
        ({6: 1200}, 250),
        ({6: 1800}, 250),
        ({6: 1500}, 200),
    ],
}


class ArmController:
    """
    Smooth arm control with named positions and action sequences.
    
    All movements send multiple servos in a single command,
    so they move simultaneously (smooth, coordinated).
    """
    
    def __init__(self, board=None):
        self.board = board or BoardController()
        self._current = {}  # Track current servo positions
        self._positions = dict(POSITIONS)
        self._sequences = dict(SEQUENCES)
        
        # Load saved positions from file
        self._saved_path = Path('/home/robot/code/pathfinder/saved_positions.json')
        self._load_saved_positions()
    
    def _load_saved_positions(self):
        """Load user-saved positions from JSON file"""
        if self._saved_path.exists():
            try:
                with open(self._saved_path) as f:
                    saved = json.load(f)
                    for name, positions in saved.items():
                        # Convert string keys to ints
                        self._positions[name] = {int(k): v for k, v in positions.items()}
            except Exception:
                pass
    
    def move_to(self, positions, duration_ms=500):
        """
        Move servos to specified positions simultaneously.
        
        Args:
            positions: Dict of {servo_id: pulse_width} 
                      Only specified servos move; others stay put.
            duration_ms: Movement duration in milliseconds
        """
        # Build servo list
        servo_list = [(sid, pos) for sid, pos in positions.items() if sid in SERVO_IDS]
        
        if servo_list:
            self.board.set_servo_position(duration_ms, servo_list)
            self._current.update(positions)
    
    def move_to_named(self, name, duration_ms=500):
        """
        Move to a named position.
        
        Args:
            name: Position name (from POSITIONS or saved positions)
            duration_ms: Movement duration
            
        Returns:
            True if position found and executed
        """
        positions = self._positions.get(name)
        if positions is None:
            return False
        
        self.move_to(positions, duration_ms)
        return True
    
    def run_sequence(self, name):
        """
        Run a named action sequence (series of movements).
        
        Args:
            name: Sequence name (from SEQUENCES)
            
        Returns:
            True if sequence found and executed
        """
        sequence = self._sequences.get(name)
        if sequence is None:
            return False
        
        for positions, duration_ms in sequence:
            self.move_to(positions, duration_ms)
            time.sleep(duration_ms / 1000.0 + 0.05)  # Wait for movement + small buffer
        
        return True
    
    def run_steps(self, steps):
        """
        Run a custom sequence of steps.
        
        Args:
            steps: List of (positions_dict, duration_ms) tuples
        """
        for positions, duration_ms in steps:
            self.move_to(positions, duration_ms)
            time.sleep(duration_ms / 1000.0 + 0.05)
    
    def interpolate(self, start, end, steps=5, total_ms=1000):
        """
        Smoothly interpolate between two positions.
        
        Creates intermediate positions for extra-smooth movement.
        
        Args:
            start: Start positions dict {servo_id: pulse}
            end: End positions dict {servo_id: pulse}
            steps: Number of intermediate steps
            total_ms: Total movement time
        """
        step_ms = total_ms // steps
        
        # Find servos that need to move
        servo_ids = set(start.keys()) | set(end.keys())
        
        for i in range(1, steps + 1):
            t = i / steps  # 0.0 to 1.0
            intermediate = {}
            
            for sid in servo_ids:
                s = start.get(sid, self._current.get(sid, 1500))
                e = end.get(sid, s)
                intermediate[sid] = int(s + (e - s) * t)
            
            self.move_to(intermediate, step_ms)
            time.sleep(step_ms / 1000.0)
    
    # ===== Convenience Methods =====
    
    def camera_forward(self, duration_ms=800):
        """Move to camera-forward position (see AprilTags)"""
        self.move_to_named('camera_forward', duration_ms)
    
    def camera_down(self, duration_ms=800):
        """Move to camera-down position (see blocks on floor)"""
        self.move_to_named('camera_down', duration_ms)
    
    def gripper_open(self, duration_ms=400):
        """Open gripper"""
        self.move_to({1: 2500}, duration_ms)
    
    def gripper_close(self, duration_ms=400):
        """Close gripper"""
        self.move_to({1: 1475}, duration_ms)
    
    def pickup(self):
        """Full pickup sequence: lower arm → grab → lift
        
        Assumes robot is already at block_close position
        (block directly in front, within arm reach).
        """
        self.run_sequence('pickup_ready')   # Arm down, open gripper
        time.sleep(0.2)
        self.run_sequence('pickup_grab')    # Close gripper tight
        time.sleep(0.3)
        self.run_sequence('pickup_lift')    # Lift to carry position
    
    def drop(self):
        """Drop block"""
        self.run_sequence('drop')
    
    def wave(self):
        """Wave gesture"""
        self.run_sequence('wave')
    
    def nod(self):
        """Nod yes gesture"""
        self.run_sequence('nod_yes')
    
    def shake(self):
        """Shake no gesture"""
        self.run_sequence('shake_no')
    
    # ===== Position Management =====
    
    def save_position(self, name, positions=None):
        """
        Save current or specified positions with a name.
        
        Args:
            name: Position name
            positions: Dict of {servo_id: pulse}. If None, uses _current.
        """
        if positions is None:
            positions = dict(self._current)
        
        self._positions[name] = positions
        
        # Save to file
        saveable = {}
        for n, p in self._positions.items():
            if n not in POSITIONS:  # Only save user positions, not defaults
                saveable[n] = p
        
        try:
            with open(self._saved_path, 'w') as f:
                json.dump(saveable, f, indent=2)
        except Exception:
            pass
    
    def list_positions(self):
        """List all available position names"""
        return list(self._positions.keys())
    
    def list_sequences(self):
        """List all available sequence names"""
        return list(self._sequences.keys())
    
    def get_position(self, name):
        """Get a named position's servo values"""
        return self._positions.get(name)


if __name__ == '__main__':
    print("ARM CONTROL DEMO")
    print("="*70)
    print()
    
    arm = ArmController()
    
    print("Positions:", arm.list_positions())
    print("Sequences:", arm.list_sequences())
    print()
    
    print("Moving to camera_forward (all servos simultaneously)...")
    arm.camera_forward(duration_ms=1000)
    time.sleep(1.5)
    
    print("Nodding yes...")
    arm.nod()
    time.sleep(0.5)
    
    print("Shaking no...")
    arm.shake()
    time.sleep(0.5)
    
    print("Back to camera_forward...")
    arm.camera_forward()
    time.sleep(1)
    
    print()
    print("Done! All movements were smooth multi-servo commands.")
