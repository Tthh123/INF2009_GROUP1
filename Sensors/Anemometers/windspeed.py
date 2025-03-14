import serial

# Open serial connection to Pico
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# Conversion equation parameters
A = 26.43  # Scaling factor from the extracted graph
B = -5.67  # Offset

while True:
    try:
        line = ser.readline().decode('utf-8').strip()  # Read & decode data
        if line:
            voltage = float(line)  # Convert to float
            wind_speed = A * voltage + B  # Convert voltage to wind speed
            wind_speed = max(wind_speed, 0)  # Ensure no negative wind speed
            print(f"Voltage: {voltage:.3f} V -> Wind Speed: {wind_speed:.2f} m/s")
    except Exception as e:
        print(f"Error: {e}")

