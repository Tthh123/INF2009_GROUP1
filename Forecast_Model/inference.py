import json
import numpy as np
import pandas as pd
import tensorflow as tf

############################
# 1. Define train_mean and train_std
############################
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

############################
# 2. File Paths
############################
jsonl_file_path = "fake_sensor_data.jsonl"
tflite_model_path = "multi_output_cnn.tflite"

############################
# 3. Load the TFLite Model
############################
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

# Get model input & output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("Model loaded!")
print("Input details:", input_details)
print("Output details:", output_details)

############################
# 4. Read and Preprocess Sensor Data
############################
# Load JSONL sensor readings
sensor_readings = []
with open(jsonl_file_path, "r") as f:
    for line in f:
        sensor_readings.append(json.loads(line))

feature_columns = ["p (mbar)", "T (degC)", "rh (%)", "wv (m/s)"]

# Convert to NumPy array [time_steps, features]
input_data = np.array([[entry[col] for col in feature_columns] for entry in sensor_readings],
                      dtype=np.float32)

# Expand dims to [1, time_steps, features] for a single batch
input_data = np.expand_dims(input_data, axis=0)
print("Raw input data shape:", input_data.shape)

# Ensure shape matches the model's expected input shape
expected_shape = tuple(input_details[0]['shape'])
if input_data.shape != expected_shape:
    raise ValueError(f"Input shape mismatch: Expected {expected_shape}, got {input_data.shape}")

############################
# 5. Normalize Input Data
############################
# We'll do this in vectorized form, ensuring the feature order matches
mean_arr = train_mean[feature_columns].values.astype(np.float32)
std_arr = train_std[feature_columns].values.astype(np.float32)

# input_data shape: (1, time_steps, num_features)
# mean_arr, std_arr shape: (4,) in the same feature order
input_data[0] = (input_data[0] - mean_arr) / std_arr

############################
# 6. Run Inference
############################
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()
predictions = interpreter.get_tensor(output_details[0]['index'])

print("Predictions (normalized):")
print(predictions)

############################
# 7. Unnormalize Predictions
############################
# We'll make a copy and unnormalize in place
predictions_unnorm = predictions.copy()

# predictions shape: (1, time_steps, features)
predictions_unnorm[0] = predictions_unnorm[0] * std_arr + mean_arr

print("\nPredictions (unnormalized):")
for i, pred in enumerate(predictions_unnorm[0]):
    # Convert each feature vector to a dictionary
    pred_dict = dict(zip(feature_columns, pred))
    print(f"Reading {i}: {pred_dict}")