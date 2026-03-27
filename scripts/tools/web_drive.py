#!/usr/bin/env python3
"""
Simple web interface for driving the robot
Provides browser-based control with camera stream
"""

from flask import Flask, render_template, Response, jsonify, request
from lib.board import get_board as BoardController
import cv2
import time
import threading

app = Flask(__name__)

# Global state
board = BoardController()
camera = cv2.VideoCapture(0)
current_speed = 30
current_turn_speed = 0.5
is_moving = False
lock = threading.Lock()

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Main control page"""
    return render_template('drive.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/move', methods=['POST'])
def move():
    """Handle movement commands"""
    try:
        data = request.json
        direction = data.get('direction')
        speed = int(data.get('speed', current_speed))
        
        with lock:
            if direction == 'forward':
                board.set_motor_duty([(1, speed), (2, speed), (3, speed), (4, speed)])
            elif direction == 'backward':
                board.set_motor_duty([(1, -speed), (2, -speed), (3, -speed), (4, -speed)])
            elif direction == 'left':
                # Strafe left
                board.set_motor_duty([(1, -speed), (2, speed), (3, speed), (4, -speed)])
            elif direction == 'right':
                # Strafe right
                board.set_motor_duty([(1, speed), (2, -speed), (3, -speed), (4, speed)])
            elif direction == 'rotate_left':
                # Rotate counterclockwise
                board.set_motor_duty([(1, -speed), (2, speed), (3, -speed), (4, speed)])
            elif direction == 'rotate_right':
                # Rotate clockwise
                board.set_motor_duty([(1, speed), (2, -speed), (3, speed), (4, -speed)])
            elif direction == 'stop':
                board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        
        return jsonify({'status': 'ok'})
    except Exception as e:
        print(f"Error in move(): {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/set_speed', methods=['POST'])
def set_speed():
    """Update movement speed"""
    try:
        global current_speed
        data = request.json
        current_speed = int(data.get('speed', 30))
        return jsonify({'status': 'ok', 'speed': current_speed})
    except Exception as e:
        print(f"Error in set_speed(): {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/status')
def status():
    """Get robot status"""
    try:
        voltage = board.get_battery()
        if voltage and voltage < 100:
            battery = f"{voltage:.2f}V"
        else:
            battery = "Unknown"
    except:
        battery = "Unknown"
    
    return jsonify({
        'battery': battery,
        'speed': current_speed,
        'camera': 'active' if camera.isOpened() else 'inactive'
    })

if __name__ == '__main__':
    print("=" * 60)
    print("PathfinderV2 Web Control")
    print("=" * 60)
    print("\nStarting web server...")
    print("Open browser to: http://<ROBOT_IP>:5000")
    print("Press Ctrl+C to stop")
    print()
    
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        board.set_motor_duty([(1, 0), (2, 0), (3, 0), (4, 0)])
        camera.release()
