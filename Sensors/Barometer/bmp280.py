import time
import board
import busio
import adafruit_bmp280

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize BMP280 (default I2C address is 0x76)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

# Set sea level pressure (adjust based on your location)
bmp280.sea_level_pressure = 1013.25  # Standard sea-level pressure in hPa

while True:
	print(f"Temperature: {bmp280.temperature:.2f} C")
	print(f"Pressure: {bmp280.pressure:.2f} hPa")
	print(f"Altitude: {bmp280.altitude:.2f} m\n")
	time.sleep(2)