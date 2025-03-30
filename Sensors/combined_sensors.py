import time
import board
import busio
import adafruit_bmp280
import adafruit_dht
import serial
import paho.mqtt.client as mqtt
import json
import os

# Define sensor types and GPIO pins
SENSOR_BMP = adafruit_bmp280.Adafruit_BMP280_I2C(busio.I2C(board.SCL, board.SDA), address=0x76)
SENSOR_DHT = adafruit_dht.DHT22(board.D4)  # Use GPIO pin D4
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # For Anemometer

# Conversion equation parameters for Anemometer
A = 26.43  # Scaling factor from the extracted graph
B = -5.67  # Offset

# MQTT Configuration
mqtt_broker = os.getenv("MQTT_BROKER")  # MQTT Broker address (localhost for local testing)
mqtt_port = int(os.getenv("MQTT_PORT"))           # Default MQTT port
mqtt_user = os.getenv("MQTT_USER")           # MQTT username
mqtt_password = os.getenv("MQTT_PASSWORD")   # MQTT password
CA_CERT_PATH = "/home/team1/INF2009_GROUP1/ca.crt"  # Path to CA certificate
mqtt_topic = "sensor/data"  # Topic to publish data

# Create MQTT client
client = mqtt.Client()

# Connect to MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT loop in the background
client.loop_start()

# Set BMP280 sea level pressure (adjust based on your location)
SENSOR_BMP.sea_level_pressure = 1013.25  # Standard sea-level pressure in hPa
wind_speed=0
while True:
    try:
        # Read from BMP280 (air pressure)
        air_pressure = SENSOR_BMP.pressure

        # Read from DHT22 (temperature, humidity)
        temperature = SENSOR_DHT.temperature
        humidity = SENSOR_DHT.humidity

        # Read from Anemometer (wind speed)
        line = ser.readline().decode('utf-8').strip()  # Read & decode data
        if line:
            voltage = float(line)  # Convert to float
            wind_speed = A * voltage + B  # Convert voltage to wind speed
            wind_speed = max(wind_speed, 0)  # Ensure no negative wind speed

        # Create a combined JSON payload
        payload = {
            "temperature": temperature,
            "wind_speed": round(wind_speed, 2),
            "air_pressure": round(air_pressure, 2),
            "humidity": humidity,
        }

        # Print the combined data for debugging
        print(json.dumps(payload, indent=4))

        # Publish the combined data to the MQTT topic
        client.publish(mqtt_topic, json.dumps(payload))

    except Exception as e:
        print(f"Error: {e}")

    time.sleep(2)  # Wait 2 seconds before the next reading
