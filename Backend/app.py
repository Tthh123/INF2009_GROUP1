from flask import Flask, jsonify, request
from flask_mqtt import Mqtt
from flask_pymongo import PyMongo

app = Flask(__name__)

# Configure MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/weather_data"
mongo = PyMongo(app)

# Configure MQTT
app.config['MQTT_BROKER_URL'] = 'localhost'  # Change to your MQTT broker's IP
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TOPIC'] = 'sensor/data'

mqtt = Mqtt(app)

# Default route
@app.route('/')
def home():
    return jsonify({"message": "Flask Web Server Running"}), 200

# MQTT Message Handling
@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker!")
    mqtt.subscribe(app.config['MQTT_TOPIC'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    """Handles incoming MQTT messages and saves to MongoDB"""
    import json
    data = json.loads(message.payload.decode())
    mongo.db.sensors.insert_one(data)
    print(f"Received & Stored: {data}")

# Fetch stored sensor data
@app.route('/data', methods=['GET'])
def get_data():
    data = list(mongo.db.sensors.find({}, {"_id": 0}))
    return jsonify(data), 200

if __name__ == '__main__':
    mqtt.init_app(app)
    app.run(host='0.0.0.0', port=5000, debug=True)
