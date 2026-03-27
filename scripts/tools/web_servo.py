#!/usr/bin/env python3
"""
Web interface for servo control
Provides sliders to position each arm servo
"""

from flask import Flask, render_template, jsonify, request
from lib.board import get_board as BoardController
import threading

app = Flask(__name__)

board = BoardController()
lock = threading.Lock()

# Current servo positions
# NOTE: Servo 2 is empty/unused
servo_positions = {
    1: 2500,  # Gripper (2500=open, 1475=closed - never go below 1475!)
    3: 1500,  # Wrist
    4: 1500,  # Elbow
    5: 1500,  # Shoulder
    6: 1500   # Base
}

@app.route('/')
def index():
    """Main servo control page"""
    return render_template('servo.html')

@app.route('/set_servo', methods=['POST'])
def set_servo():
    """Set individual servo position"""
    try:
        data = request.json
        servo_id = int(data.get('servo'))
        position = int(data.get('position'))
        
        # Clamp to valid range
        # Special case: Gripper (servo 1) must not go below 1475 (fully closed)
        if servo_id == 1:
            position = max(1475, min(2500, position))
        else:
            position = max(500, min(2500, position))
        
        with lock:
            board.set_servo_position(300, [(servo_id, position)])
            servo_positions[servo_id] = position
        
        return jsonify({'status': 'ok', 'servo': servo_id, 'position': position})
    except Exception as e:
        print(f"Error in set_servo(): {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/get_positions')
def get_positions():
    """Get current servo positions"""
    return jsonify(servo_positions)

@app.route('/preset/<name>')
def preset(name):
    """Apply preset positions"""
    presets = {
        'rest': {
            1: 2500,  # Gripper open
            3: 1500,  # Wrist neutral
            4: 1300,  # Elbow bent
            5: 1700,  # Shoulder lowered
            6: 1500   # Base center
        },
        'forward': {
            1: 2500,  # Gripper open
            3: 590,   # Wrist
            4: 2450,  # Elbow
            5: 700,   # Shoulder
            6: 1500   # Base (forward)
        }
    }
    
    if name not in presets:
        return jsonify({'status': 'error', 'message': 'Unknown preset'}), 404
    
    try:
        positions = presets[name]
        with lock:
            # Move all servos to preset
            for servo_id, pos in positions.items():
                board.set_servo_position(500, [(servo_id, pos)])
                servo_positions[servo_id] = pos
        
        return jsonify({'status': 'ok', 'preset': name, 'positions': positions})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("PathfinderV2 Servo Control")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open browser to: http://<ROBOT_IP>:5001")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5001, threaded=True)
    except KeyboardInterrupt:
        print("\nStopping...")
