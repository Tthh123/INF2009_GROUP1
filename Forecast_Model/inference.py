import numpy as np
import tflite_runtime.interpreter as tflite

# Load the TFLite model
interpreter = tflite.Interpreter(model_path="your_model.tflite")
interpreter.allocate_tensors()

# Get input & output tensors
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print("✅ Model Loaded!")
print("Input Details:", input_details)
print("Output Details:", output_details)

# Example: Create a fake input for testing
input_shape = input_details[0]['shape']  # (1, time_steps, features)
test_input = np.random.rand(*input_shape).astype(np.float32)

# Set the input tensor
interpreter.set_tensor(input_details[0]['index'], test_input)

# Run inference
interpreter.invoke()

# Get the output tensor
predictions = interpreter.get_tensor(output_details[0]['index'])
print("📌 Predictions:", predictions)