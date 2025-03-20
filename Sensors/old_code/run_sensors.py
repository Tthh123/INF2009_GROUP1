import subprocess

# Define the scripts to run
scripts = ["Anemometers/windspeed.py", "Barometer/bmp280.py", "Temp_Humidity_Sensor/dht22.py"]

# Start all scripts as background processes
processes = [subprocess.Popen(["python3", script]) for script in scripts]

# Keep the launcher running
try:
    for process in processes:
        process.wait()
except KeyboardInterrupt:
    # If interrupted, terminate all subprocesses
    for process in processes:
        process.terminate()
