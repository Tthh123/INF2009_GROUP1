import json
from datetime import datetime, timedelta
import random

# Generate fake sensor data every 10 minutes for 27 entries
start_time = datetime(2025, 3, 18, 10, 0, 0)  # Start from a given timestamp
data = []

for i in range(27):
    entry = {
        "timestamp": (start_time + timedelta(minutes=10 * i)).strftime("%Y-%m-%d %H:%M:%S"),
        "T (degC)": round(random.uniform(19.5, 20.5), 2),
        "wv (m/s)": round(random.uniform(2.5, 3.5), 2),
        "p (mbar)": round(random.uniform(1011.0, 1013.0), 2),
        "rh (%)": round(random.uniform(58.0, 62.0), 2)
    }
    data.append(entry)

# Save as a JSONL file
file_path = "fake_sensor_data.jsonl"
with open(file_path, "w") as f:
    for entry in data:
        f.write(json.dumps(entry) + "\n")

file_path