#!/usr/bin/env python3
"""
Web Control Interface for PathfinderV2

Provides:
- Live video stream
- Drive controls (WASD/arrows)
- Servo sliders (6 servos)
- Save/load arm positions
- Real-time battery monitoring

Usage:
    python3 web_control.py
    Then open: http://10.10.10.134:8080
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.board import get_board
BoardController = None  # Use get_board() instead

app = Flask(__name__)

# Global state
board = get_board()
camera = None  # Opened lazily to avoid locking camera on import

def get_camera():
    """Get or open camera (lazy initialization)"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(0.5)
    return camera

# Servo positions (match startup script camera-forward position)
servo_positions = {
    1: 2500,  # Claw (Gripper open)
    3: 590,   # Wrist
    4: 2450,  # Elbow
    5: 700,   # Shoulder
    6: 1500   # Base (center/forward)
}

# Saved positions
saved_positions = {}

# Motor power (global, can be adjusted via web interface)
motor_power = {
    'drive': 30,
    'turn': 30
}

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        cam = get_camera()
        success, frame = cam.read()
        if not success:
            break
        
        # Add battery voltage overlay
        mv = board.get_battery()
        if mv:
            voltage = mv / 1000.0
            color = (0, 255, 0) if voltage > 8.2 else (0, 165, 255) if voltage > 8.0 else (0, 0, 255)
            cv2.putText(frame, f"Battery: {voltage:.2f}V", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Add servo positions overlay
        y_pos = 70
        for servo_id in sorted(servo_positions.keys()):
            pos = servo_positions[servo_id]
            cv2.putText(frame, f"S{servo_id}: {pos}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Serve main control page"""
    return render_template('control.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/drive', methods=['POST'])
def drive():
    """Drive motor control"""
    try:
        data = request.json
        direction = data.get('direction')
        
        # Safety check: prevent motor commands at low battery
        mv = board.get_battery()
        if mv:
            voltage = mv / 1000.0
            if voltage < 7.8 and direction != 'stop':
                return jsonify({'status': 'error', 
                              'message': f'Battery too low ({voltage:.2f}V) - Replace batteries!'})
        
        drive_pwr = motor_power['drive']
        turn_pwr = motor_power['turn']
        
        # Limit max power to prevent crashes
        drive_pwr = min(drive_pwr, 40)
        turn_pwr = min(turn_pwr, 40)
        
        if direction == 'forward':
            board.set_motor_duty([(1, drive_pwr), (2, drive_pwr), 
                                  (3, drive_pwr), (4, drive_pwr)])
        elif direction == 'backward':
            board.set_motor_duty([(1, -drive_pwr), (2, -drive_pwr), 
                                  (3, -drive_pwr), (4, -drive_pwr)])
        elif direction == 'left':
            board.set_motor_duty([(1, -turn_pwr), (2, turn_pwr), 
                                  (3, -turn_pwr), (4, turn_pwr)])
        elif direction == 'right':
            board.set_motor_duty([(1, turn_pwr), (2, -turn_pwr), 
                                  (3, turn_pwr), (4, -turn_pwr)])
        elif direction == 'strafe_left':
            board.set_motor_duty([(1, -drive_pwr), (2, drive_pwr), 
                                  (3, drive_pwr), (4, -drive_pwr)])
        elif direction == 'strafe_right':
            board.set_motor_duty([(1, drive_pwr), (2, -drive_pwr), 
                                  (3, -drive_pwr), (4, drive_pwr)])
        elif direction == 'stop':
            board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        # Emergency stop on any error
        try:
            board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        except:
            pass
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/servo', methods=['POST'])
def servo():
    """Servo control"""
    data = request.json
    servo_id = int(data.get('servo'))
    position = int(data.get('position'))
    
    # Update position
    servo_positions[servo_id] = position
    
    # Send to board
    board.set_servo_position(500, [(servo_id, position)])
    
    return jsonify({'status': 'ok', 'servo': servo_id, 'position': position})

@app.route('/save_position', methods=['POST'])
def save_position():
    """Save current arm position"""
    data = request.json
    name = data.get('name')
    
    saved_positions[name] = servo_positions.copy()
    
    # Save to file
    with open('/home/robot/code/pathfinder/saved_positions.json', 'w') as f:
        json.dump(saved_positions, f, indent=2)
    
    return jsonify({'status': 'ok', 'name': name, 'positions': servo_positions})

@app.route('/load_position', methods=['POST'])
def load_position():
    """Load saved arm position"""
    data = request.json
    name = data.get('name')
    
    if name in saved_positions:
        positions = saved_positions[name]
        
        # Apply all servos
        servo_list = [(sid, pos) for sid, pos in positions.items()]
        board.set_servo_position(500, servo_list)
        
        # Update state
        servo_positions.update(positions)
        
        return jsonify({'status': 'ok', 'name': name, 'positions': positions})
    else:
        return jsonify({'status': 'error', 'message': 'Position not found'})

@app.route('/get_positions', methods=['GET'])
def get_positions():
    """Get all saved positions"""
    return jsonify({'positions': list(saved_positions.keys()), 
                   'current': servo_positions})

@app.route('/battery', methods=['GET'])
def battery():
    """Get battery voltage"""
    mv = board.get_battery()
    voltage = mv / 1000.0 if mv else 0
    
    return jsonify({'voltage': voltage, 
                   'status': 'good' if voltage > 8.2 else 'low' if voltage > 8.0 else 'critical'})

@app.route('/motor_power', methods=['GET'])
def get_motor_power():
    """Get current motor power settings"""
    return jsonify(motor_power)

@app.route('/motor_power', methods=['POST'])
def set_motor_power():
    """Set motor power"""
    data = request.json
    if 'drive' in data:
        motor_power['drive'] = int(data['drive'])
    if 'turn' in data:
        motor_power['turn'] = int(data['turn'])
    return jsonify({'status': 'ok', 'motor_power': motor_power})

# Load saved positions on startup
try:
    with open('/home/robot/code/pathfinder/saved_positions.json', 'r') as f:
        saved_positions = json.load(f)
        # Convert string keys to ints for servo_positions dict
        for name, positions in saved_positions.items():
            saved_positions[name] = {int(k): v for k, v in positions.items()}
except FileNotFoundError:
    pass

if __name__ == '__main__':
    print("="*70)
    print("PathfinderV2 Web Control")
    print("="*70)
    print()
    
    # Position robot to startup/camera-forward position
    print("Positioning robot to startup position...")
    try:
        # Turn off sonar LEDs (both LEDs on the sonar)
        board.set_rgb([(0, 0, 0, 0), (1, 0, 0, 0)])
        
        # Stop motors
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        
        # Move to camera-forward position (ONE SERVO AT A TIME to avoid power spike)
        camera_forward = [
            (1, 2500),  # Claw open
            (6, 1500),  # Base center
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]
        
        print("  Moving servos sequentially...")
        for servo_id, pwm in camera_forward:
            board.set_servo_position(800, [(servo_id, pwm)])  # Slower speed (800ms)
            time.sleep(0.5)  # Longer delay between servos
        
        print("  Robot positioned to camera-forward")
    except Exception as e:
        print(f"  Warning: Could not position robot: {e}")
    
    print()
    print("Starting web server...")
    print("Open in browser: http://10.10.10.134:8080")
    print()
    print("Controls:")
    print("  WASD or Arrow keys - Drive")
    print("  Q/E - Strafe left/right")
    print("  Space - Stop")
    print("  Sliders - Servo control")
    print("  Save/Load - Store arm positions")
    print()
    
    app.run(host='0.0.0.0', port=8080, threaded=True)
