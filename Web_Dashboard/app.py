import requests
import json
import redis
import datetime
from flask import Flask, jsonify, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

app = Flask(__name__)

# Configure Redis
redis_host = "localhost"
redis_port = 6379
redis_db = 0

# Connect to Redis
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# Configure MQTT to use localhost
app.config['MQTT_BROKER_URL'] = "localhost"
app.config['MQTT_BROKER_PORT'] = 1883  # Default MQTT port
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = "sensor/data"  # Primary sensor topic

mqtt = Mqtt()
socketio = SocketIO(app, cors_allowed_origins="*")

# Default route
@app.route('/')
def home():
    return jsonify({"message": "Flask MQTT & Redis API Running"}), 200

# MQTT Message Handling
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    # Subscribe to both topics
    mqtt.subscribe(app.config['MQTT_TOPIC'])
    mqtt.subscribe("forecast/data")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    topic = message.topic
    try:
        data = json.loads(message.payload.decode())
        timestamp = datetime.datetime.now().isoformat()
        if topic == app.config['MQTT_TOPIC']:
            # Process sensor data
            data_with_timestamp = {"timestamp": timestamp, **data}
            print(f"Received Sensor Data: {data_with_timestamp}")
            
            # Store latest sensor values (overwrite each time)
            r.hset("sensor_data", mapping=data_with_timestamp)
            # Store history of sensor readings with timestamp
            r.rpush("sensor_data_history", json.dumps(data_with_timestamp))
            
            # Emit sensor update via Socket.IO
            socketio.emit('sensor_update', data_with_timestamp)
            print("Stored sensor data in Redis.")
        
        elif topic == "forecast/data":
            # Process forecast data
            print(f"Received Forecast Data: {data}")
            r.set("forecast_data", json.dumps(data))
            # Emit forecast update via Socket.IO
            socketio.emit('forecast_update', data)
            print("Stored forecast data in Redis.")
            
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)

# Fetch latest sensor data
@app.route('/data/latest', methods=['GET'])
def get_latest_data():
    latest_data = r.hgetall("sensor_data")
    return jsonify(latest_data), 200

# Fetch sensor data history
@app.route('/data/history', methods=['GET'])
def get_data_history():
    history = r.lrange("sensor_data_history", 0, -1)
    return jsonify([json.loads(item) for item in history]), 200

# Dashboard route renders the template which should include map & chart containers
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    mqtt.init_app(app)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
