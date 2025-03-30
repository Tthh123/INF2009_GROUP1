import json
import numpy as np
import pandas as pd
import datetime
import tensorflow as tf
import paho.mqtt.client as mqtt
import requests

#############################
# Configuration
#############################

# Function to retrieve dynamic ngrok port (if using ngrok)
def get_ngrok_mqtt_port():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json().get("tunnels", [])
        for tunnel in tunnels:
            if "tcp" in tunnel["public_url"]:
                return int(tunnel["public_url"].split(":")[-1])
    except Exception as e:
        print(f"Error fetching ngrok port: {e}")
    return None

ngrok_port = get_ngrok_mqtt_port()
if ngrok_port:
    MQTT_BROKER = "0.tcp.ap.ngrok.io"
    MQTT_PORT = ngrok_port
    print(f"Using dynamic ngrok port: {ngrok_port}")
else:
    MQTT_BROKER = "0.tcp.ap.ngrok.io"
    MQTT_PORT = 8883
    print("Failed to retrieve ngrok port; using port 8883.")

MQTT_TOPIC_SUB = "sensor/data"
MQTT_TOPIC_PUB = "forecast/predictions"
CACHE_SIZE = 27  # Cache 27 readings (one every 10 minutes)

# Sensor reading keys (as produced by the sensors)
sensor_feature_columns = ["air_pressure", "temperature", "humidity", "wind_speed"]
# Mapping from sensor keys to training keys
key_mapping = {
    "air_pressure": "p (mbar)",
    "temperature": "T (degC)",
    "humidity": "rh (%)",
    "wind_speed": "wv (m/s)"
}

# Example training statistics (replace with your actual values)
train_mean = pd.Series({
    "p (mbar)": 988.656301,
    "T (degC)": 9.107596,
    "rh (%)": 75.904082,
    "wv (m/s)": 2.15457
})
train_std = pd.Series({
    "p (mbar)": 8.296812,
    "T (degC)": 8.654242,
    "rh (%)": 16.557117,
    "wv (m/s)": 1.530114
})

# Model input parameters (should match your training configuration)
TIME_STEPS = CACHE_SIZE  # 27 readings expected
NUM_FEATURES = 4         # must equal len(sensor_feature_columns)

#############################
# Load TFLite Model
#############################
tflite_model_path = "multi_output_cnn.tflite"
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("✅ TFLite Model Loaded!")
print("Input details:", input_details)
print("Output details:", output_details)

#############################
# Helper Functions
#############################
def preprocess_sensor_data(sensor_readings):
    """
    Converts a list of sensor reading dicts into a normalized input tensor.
    Sensor readings are expected to have keys: 'air_pressure', 'temperature', 'humidity', 'wind_speed'.
    Normalization is applied using training values corresponding to:
      air_pressure -> "p (mbar)"
      temperature  -> "T (degC)"
      humidity     -> "rh (%)"
      wind_speed   -> "wv (m/s)"
    """
    # Create a NumPy array with shape (TIME_STEPS, NUM_FEATURES)
    data = np.array([[entry[sensor_key] for sensor_key in sensor_feature_columns] 
                     for entry in sensor_readings], dtype=np.float32)
    
    # Build arrays for mean and std using the mapped training keys
    mean_arr = np.array([train_mean[key_mapping[sensor_key]] for sensor_key in sensor_feature_columns], dtype=np.float32)
    std_arr  = np.array([train_std[key_mapping[sensor_key]] for sensor_key in sensor_feature_columns], dtype=np.float32)
    
    # Normalize the data
    data = (data - mean_arr) / std_arr
    
    # Reshape to (1, TIME_STEPS, NUM_FEATURES)
    return data.reshape(1, TIME_STEPS, NUM_FEATURES)

def run_prediction(sensor_readings):
    """
    Runs TFLite inference on the given sensor readings and unnormalizes the output.
    Only predictions at indices [5, 11, 17, 23] are kept.
    Returns a list of forecast objects with a timestamp and sensor predictions.
    """
    input_tensor = preprocess_sensor_data(sensor_readings)
    interpreter.set_tensor(input_details[0]['index'], input_tensor)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])
    
    # Unnormalize predictions using training stats (mapping same as input)
    mean_arr = np.array([train_mean[key_mapping[sensor_key]] for sensor_key in sensor_feature_columns], dtype=np.float32)
    std_arr  = np.array([train_std[key_mapping[sensor_key]] for sensor_key in sensor_feature_columns], dtype=np.float32)
    predictions_unnorm = predictions.copy()
    predictions_unnorm[0] = predictions_unnorm[0] * std_arr + mean_arr

    # Select indices 5, 11, 17, and 23 (forecast for next 1h, 2h, 3h, 4h)
    selected_indices = [5, 11, 17, 23]
    forecast = []
    start_dt = datetime.datetime.now()
    # For each selected index, assign a forecast time (1h, 2h, 3h, 4h ahead)
    for idx, i in enumerate(selected_indices):
        forecast_timestamp = (start_dt + datetime.timedelta(hours=idx + 1)).isoformat()
        pred = predictions_unnorm[0][i]
        # Create forecast using sensor reading keys
        forecast.append({
            "timestamp": forecast_timestamp,
            "air_pressure": round(float(pred[0]), 2),
            "temperature": round(float(pred[1]), 2),
            "humidity": round(float(pred[2]), 2),
            "wind_speed": round(float(pred[3]), 2)
        })
    return forecast

#############################
# MQTT Client Setup
#############################
sensor_cache = []  # Global cache for sensor readings

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code", rc)
    client.subscribe("sensor/data")

def on_message(client, userdata, message):
    global sensor_cache
    try:
        reading = json.loads(message.payload.decode("utf-8"))
        # Expect sensor reading keys: 'temperature', 'wind_speed', 'air_pressure', 'humidity'
        missing_keys = [key for key in sensor_feature_columns if key not in reading]
        if missing_keys:
            print(f"Warning: Missing keys {missing_keys} in sensor reading: {reading}")
            return
        # Optionally add a timestamp if not present
        if "timestamp" not in reading:
            reading["timestamp"] = datetime.datetime.now().isoformat()
        sensor_cache.append(reading)
        print(f"Received reading. Cache size: {len(sensor_cache)}")
        
        # When we have at least CACHE_SIZE readings, run prediction
        if len(sensor_cache) >= CACHE_SIZE:
            window = sensor_cache[-CACHE_SIZE:]
            forecast = run_prediction(window)
            publish_payload = {"predictions": forecast}
            client.publish("forecast/predictions", json.dumps(publish_payload))
            print("Published Forecast:")
            print(json.dumps(publish_payload, indent=2))
    except Exception as e:
        print("Error processing MQTT message:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to MQTT Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()