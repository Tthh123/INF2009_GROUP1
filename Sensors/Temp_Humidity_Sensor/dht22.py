import time
import board
import adafruit_dht
import paho.mqtt.client as mqtt
import json

# Define sensor type and GPIO pin
SENSOR = adafruit_dht.DHT22(board.D4)  # Use board.D4 instead of raw GPIO number

# MQTT Configuration
mqtt_broker = "localhost"  # MQTT Broker address (localhost for local testing)
mqtt_port = 1883           # Default MQTT port
mqtt_topic = "sensor/data" # Topic to publish data

# Create an MQTT client
client = mqtt.Client()

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the MQTT client loop in the background
client.loop_start()

while True:
    try:
        temperature = SENSOR.temperature
        humidity = SENSOR.humidity
        
        if humidity is not None and temperature is not None:
            # Print the sensor data
            print(f"Temperature: {temperature:.2f}C  Humidity: {humidity:.2f}%")
            
            # Create a JSON payload to send to MQTT
            payload = {
                "temperature": temperature,
                "humidity": humidity
            }

            # Publish the data to the MQTT topic
            client.publish(mqtt_topic, json.dumps(payload))
        else:
            print("Failed to retrieve data from sensor")

    except RuntimeError as error:
        # Catch errors which occur due to bad sensor readings
        print(f"Error reading from sensor: {error}")
    
    except Exception as error:
        SENSOR.exit()
        raise error

    time.sleep(2)  # Wait 2 seconds before retrying
