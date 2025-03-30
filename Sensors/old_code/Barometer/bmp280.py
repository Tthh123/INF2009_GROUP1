import time
import board
import busio
import adafruit_bmp280
import paho.mqtt.client as mqtt
import json
import os

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize BMP280 (default I2C address is 0x76)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# Set sea level pressure (adjust based on your location)
bmp280.sea_level_pressure = 1013.25  # Standard sea-level pressure in hPa

# MQTT Configuration
mqtt_broker = os.getenv("MQTT_BROKER")  # MQTT Broker address (localhost for local testing)
mqtt_port = int(os.getenv("MQTT_PORT"))           # Default MQTT port
mqtt_user = os.getenv("MQTT_USER")           # MQTT username
mqtt_password = os.getenv("MQTT_PASSWORD")   # MQTT password
CA_CERT_PATH = "/home/team1/INF2009_GROUP1/ca.crt"  # Path to CA certificate
mqtt_topic = "sensor/data" # Topic to publish data

# Create an MQTT client
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop in the background to listen for messages (if needed)
client.loop_start()

while True:
	# Collect data from the BMP280 sensor
    # temperature = bmp280.temperature
    pressure = bmp280.pressure
    # altitude = bmp280.altitude

    # Print the sensor data (for debugging purposes)
    # print(f"Temperature: {temperature:.2f} C")
    print(f"Pressure: {pressure:.2f} hPa")
    # print(f"Altitude: {altitude:.2f} m\n")

	# Create a JSON payload to send to MQTT
    payload = {
        "air_pressure": round(pressure, 2),
    }

    # Publish the data to the MQTT topic
    client.publish(mqtt_topic, json.dumps(payload))
    time.sleep(2)
