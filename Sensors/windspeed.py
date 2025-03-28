import time
import serial
import paho.mqtt.client as mqtt
import json

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Conversion equation parameters
A = 26.43  # Scaling factor from the extracted graph
B = -5.67  # Offset

# MQTT Configuration
mqtt_broker = "localhost"  # MQTT Broker address (localhost for local testing)
mqtt_port = 1883           # Default MQTT port
mqtt_topic = "sensor/data"  # Topic to publish data

# Create an MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop in the background
client.loop_start()

while True:
    try:
        line = ser.readline().decode('utf-8').strip()  # Read & decode data
        if line:
            voltage = float(line)  # Convert to float
            wind_speed = A * voltage + B  # Convert voltage to wind speed
            wind_speed = max(wind_speed, 0)  # Ensure no negative wind speed
            print(f"Voltage: {voltage:.3f} V -> Wind Speed: {wind_speed:.2f} m/s")
            
            # Create a JSON payload with the wind speed
            payload = {
                "wind_speed": round(wind_speed, 2)
            }

            # Publish the data to the MQTT topic
            client.publish(mqtt_topic, json.dumps(payload))
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(2)

