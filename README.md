# Smart Localised Weather Monitoring System

## Group 1
- Pang Yu Rui (2200861)
- Teo Hao Han Travis (2201113)
- Ang Jun Jie (2201196)
- Nik Mohammad Farhan (2201237)
- Wong Meng Lun Alan (2201038)

## 🛠️ Hardware and Tools Selection – Justification

This section outlines the rationale behind the selection of hardware and tools used for our project. All choices were made based on criteria such as **efficiency, suitability for remote outdoor use, and compatibility with edge computing frameworks**.

---

### ✅ Selected Hardware

| Component | Justification |
|----------|----------------|
| **Raspberry Pi 4** | Serves as the main **edge computing device**. Capable of handling multiple sensor inputs, local ML inference, and wireless communication. Chosen for its **balance of performance, power efficiency, and GPIO availability**. |
| **Raspberry Pi Pico** | Used as an **ADC (Analog to Digital Converter)** for the anemometer, since the Raspberry Pi 4 lacks native analog input. Lightweight and ideal for sensor interfacing. |
| **Temperature & Humidity Sensor (DHT22)** | Captures environmental data crucial for predicting microclimate changes. Offers **good accuracy, low cost**, and easy integration via GPIO. |
| **Barometric Sensor (BMP280)** | Detects changes in atmospheric pressure, aiding in **storm prediction and trend analysis**. Communicates via I2C, which is natively supported by the Raspberry Pi. |
| **Anemometer (SEN-TEM-025)** | Measures wind speed, essential for assessing outdoor weather safety. Outputs analog signal, requiring conversion via the Pi Pico. |

---

### 🧰 Software & Tools

| Tool | Justification |
|------|---------------|
| **Python** | Primary programming language for sensor data acquisition and processing. Widely supported on Raspberry Pi. |
| **TensorFlow Lite** | Lightweight ML framework used for **on-device inference** of weather classification models. Optimized for ARM-based devices. |
| **MQTT Protocol** | Lightweight messaging protocol used for **efficient sensor data transmission** between edge, fog, and cloud layers. |
| **Flask (Web Server)** | Enables real-time **data visualization via dashboard**. Simple and fast to deploy. |
| **Redis (NoSQL)** | Used for **storing sensor data** and model results in the cloud. Chosen for its speed and ease of integration with Flask. |
