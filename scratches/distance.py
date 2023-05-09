from flask import Flask, jsonify
import RPi.GPIO as GPIO
import time
import threading
from buzzer import Buzzer
from distance_sensor import UltrasonicSensor

app = Flask(__name__)






# Set up GPIO pins


# Endpoint to start measuring distance
@app.route('/start')
def start_measure():
    global measuring
    if not measuring:
        measuring = True
        # Start measurement loop in a separate thread
        t = threading.Thread(target=measurement_loop)
        t.start()
        return jsonify({'status': 'success', 'message': 'Measurement started.'})
    else:
        return jsonify({'status': 'error', 'message': 'Measurement already started.'})

# Endpoint to stop measuring distance
@app.route('/stop')
def stop_measure():
    global measuring
    if measuring:
        measuring = False
        return jsonify({'status': 'success', 'message': 'Measurement stopped.'})
    else:
        return jsonify({'status': 'error', 'message': 'Measurement not started.'})

# Endpoint to get current distance measurement
@app.route('/distance')
def get_distance():
    if measuring:
        distance = measure_distance()
        return jsonify({'status': 'success', 'distance': distance})
    else:
        return jsonify({'status': 'error', 'message': 'Measurement not started.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

# Clean up GPIO pins
GPIO.cleanup()
