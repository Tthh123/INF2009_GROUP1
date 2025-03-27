import requests
import json
import redis
import datetime
from flask import Flask, jsonify, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

app = Flask(__name__)

# ? Configure Redis
redis_host = "localhost"
redis_port = 6379
redis_db = 0

# Connect to Redis
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)

# ? Function to get the latest ngrok port dynamically
def get_ngrok_mqtt_port():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json().get("tunnels", [])
        for tunnel in tunnels:
            if "tcp" in tunnel["public_url"]:  # Find the TCP tunnel
                return tunnel["public_url"].split(":")[-1]  # Extract the port number
    except Exception as e:
        print(f"Error fetching ngrok port: {e}")
    return None

# ? Get latest ngrok port dynamically
ngrok_port = get_ngrok_mqtt_port()

if ngrok_port:
    app.config['MQTT_BROKER_URL'] = "0.tcp.ap.ngrok.io"
    app.config['MQTT_BROKER_PORT'] = int(ngrok_port)
    print(f"Using dynamic ngrok port: {ngrok_port}")
else:
    print("? Failed to retrieve ngrok port. Make sure ngrok is running.")

app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = "sensor/data"

mqtt = Mqtt()
socketio = SocketIO(app, cors_allowed_origins="*")

# ? Default route
@app.route('/')
def home():
    return jsonify({"message": "Flask MQTT & Redis API Running"}), 200

# ? MQTT Message Handling
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("? Connected to MQTT Broker!")
    mqtt.subscribe(app.config['MQTT_TOPIC'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    """Handles incoming MQTT messages and saves to Redis with timestamp"""
    try:
        data = json.loads(message.payload.decode())
        timestamp = datetime.datetime.now().isoformat()  # Get current timestamp
        data_with_timestamp = {"timestamp": timestamp, **data}  # Add timestamp to data

        print(f"?? Received Data: {data_with_timestamp}")

        # Store latest sensor values (overwrite each time)
        r.hset("sensor_data", mapping=data_with_timestamp)

        # Store history of sensor readings with timestamp
        r.rpush("sensor_data_history", json.dumps(data_with_timestamp))
        
        socketio.emit('sensor_update', data_with_timestamp)

        print("?? Stored data in Redis.")

    except json.JSONDecodeError as e:
        print("? Error decoding JSON:", e)

# ? Fetch latest sensor data
@app.route('/data/latest', methods=['GET'])
def get_latest_data():
    latest_data = r.hgetall("sensor_data")
    return jsonify(latest_data), 200

# ? Fetch sensor data history
@app.route('/data/history', methods=['GET'])
def get_data_history():
    history = r.lrange("sensor_data_history", 0, -1)
    return jsonify([json.loads(item) for item in history]), 200
    
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    mqtt.init_app(app)
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
