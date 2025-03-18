import time
import board
import adafruit_dht

# Define sensor type and GPIO pin
SENSOR = adafruit_dht.DHT22(board.D4)  # Use board.D4 instead of raw GPIO number

while True:
    try:
        temperature = SENSOR.temperature
        humidity = SENSOR.humidity
        
        if humidity is not None and temperature is not None:
            print(f"Temperature: {temperature:.2f}C  Humidity: {humidity:.2f}%")
        else:
            print("Failed to retrieve data from sensor")

    except RuntimeError as error:
        # Catch errors which occur due to bad sensor readings
        print(f"Error reading from sensor: {error}")
    
    except Exception as error:
        SENSOR.exit()
        raise error

    time.sleep(2)  # Wait 2 seconds before retrying
