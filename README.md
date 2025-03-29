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

---

### Documentation

March 1 – March 7
Initial Research & Cloud Training
Okay, so for the first week, we started off by messing around with different ML models on the cloud. We tried out a basic model, a CNN, and a multi-output CNN—this last one had the best results because it can handle all sensors together and is 42% smaller than running four separate CNNs. 

March 8 – March 10
Locking in the Model & Setting Up Pi #2
 From March 8 to 10, we got serious about which model to use. After checking out the MAE and RMSE, we all agreed that the multi-output CNN was the best choice.
 Meanwhile, we set up our Raspberry Pi #2 for inference. We installed all the libraries (TensorFlow, etc.) and copied over the trained models from the cloud. We did a quick test on Pi #2 to make sure everything runs smoothly.

March 11 – March 14
Testing on Pi #2 & Integrating the System
 This week, we ran some tests on Pi #2 using sample sensor data. We checked out the inference time, CPU usage. The multi-output CNN proved to be solid.
 At the same time, we got busy on Pi #1: setting up our front-end and back-end. We used ngrok to expose our endpoints securely and tested our communication with MQTT. We also made sure that Pi #3 (the sensor-reading unit) can send data over to Pi #2. Everything was connected and working so far

March 15 – March 17
Tweaking the Model & Benchmarking
 From 15th to 17th, we tried some optimizations on the multi-output CNN – things like quantization and pruning to see if we can get it running even faster on Pi #2.
 We then compared the baseline and our multi-output CNN side by side. The numbers (latency, CPU, memory) all pointed to the multi-output CNN being our champion.

March 18 – March 20
Front-End & Back-End Fine-Tuning
 This period was all about polishing things up. On Pi #1, we built a simple web dashboard using JS to show live sensor data and predictions such as adding some nice charts and stuff so it’s easy to see what’s happening in real time.
 We also stress-tested our back-end (MQTT/HTTP endpoints) to make sure they can handle continuous data from Pi #3. Our GitHub readme got updated with detailed notes on why we chose the multi-output CNN and how all three Pis work together.

March 21 – March 23
Hardening the Deployment & CI/CD Setup
 Between March 21 and 23, we set up startup scripts for our Pis so that everything auto-runs on reboot. 

March 24 – March 26
Extended Testing & Front-End Improvements
 From the 24th to 26th, we let our system run in a real environment (SIT Tennis court) to see if any issues pop up. We tweaked sensor sampling rates and even tried out TensorFlow Lite for faster inference.
 We also spent time making the front-end more user-friendly such as adding in a map visualisation

March 27 – March 29
Final Validation & Wrap-Up
 In the last few days, we did our final checks. We compared the baseline, single CNN, and multi-output CNN once more, confirming that the multi-output CNN has the best accuracy and is much smaller (42% less) than running four separate models.
 We made sure the sensor readings from Pi #3 show up correctly on the dashboard. Also, we recorded some demo videos and took screenshots for our GitHub documentation.

