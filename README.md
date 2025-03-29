# Smart Localised Weather Monitoring System

## Group 1
- Pang Yu Rui (2200861)
- Teo Hao Han Travis (2201113)
- Ang Jun Jie (2201196)
- Nik Mohammad Farhan (2201237)
- Wong Meng Lun Alan (2201038)

## ⚙️ Setup Instructions

Follow the steps below to set up the project on your local machine or Raspberry Pi:

### 1. Clone the Repository

```bash
git clone https://github.com/Tthh123/INF2009_GROUP1.git
cd INF2009_GROUP1
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Sensor Configuration

Ensure that all sensors are properly connected to your Raspberry Pi using the correct GPIO, I2C, or UART pins.

### 5. Running the Application

- **Edge Node (Sensor Collection + Inference):**

  ```bash
  python3 Sensors/combined_sensors.py
  ```

- **Fog Node (ML Training / Model Update):**

  ```bash
  python Forecast_Model/inference.py
  ```

- **Cloud Node (Flask Server + Dashboard):**

  ```bash
  python3 Web_Dashboard/app.py
  ```

  
## 1. Work Packages and Responsibilities

This section outlines the work packages and designated responsibilities for each team member. Tasks have been divided based on the system architecture: **Cloud**, **Fog**, and **Edge**, with clearly defined scopes to ensure collaboration and accountability.

---

### ☁️ Cloud Pi [All code commits are under Travis' account due to the limitations of PIs]

**1. Frontend Development – Travis**  
- Designed and implemented the **user-facing dashboard** using Flask and web technologies.  
- Responsible for **data visualization** of sensor readings and weather alerts.  
- Ensured responsive design and usability of the dashboard interface.

**2. Backend Development – Jun Jie**  
- Developed the **Flask server API** to handle incoming data and serve predictions to the frontend.  
- Connected the backend to a **Redis (NoSQL) database** for storing sensor and forecast data.  
- Ensured smooth handling of API routes and response formatting.

**3. Communication Protocol – Alan**  
- Implemented **MQTT messaging** between edge, fog, and cloud layers.  
- Configured **ngrok tunneling** for remote testing and webhook-based communications.  
- Ensured secure and reliable transmission of both sensor data and alerts.

---

### 🌫️ Fog Pi

**ML Model Training – Farhan**  
- Designed and trained the **Convolutional Neural Network (CNN)** for weather condition classification.  
- Utilized **TensorFlow Lite** to convert and optimize models for edge deployment.  
- Periodically retrains the model using new sensor datasets and handles versioning of model updates.

---

### 🛰️ Edge Pi

**Sensor Integration & Interface Protocols – Yu Rui**  
- Configured environmental sensors: **DHT22, BMP280, Anemometer** for accurate data collection.  
- Programmed the **data acquisition scripts** using Python.  
- Handled **low-level interface protocols** such as I2C, GPIO, and UART to ensure sensor communication with the Raspberry Pi.  
- Integrated Raspberry Pi Pico as an **ADC bridge** for analog sensor (anemometer) readings.





## 2. Hardware and Tools Selection – Justification

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

## 3. Machine Learning

### 🎯 Purpose

The goal of our machine learning model is to **predict short-term weather conditions** based on historical sensor data. Every 10 minutes, our model forecasts the next 4 hours of:

- **Temperature (°C)**
- **Relative Humidity (%)**
- **Air Pressure (mbar)**
- **Wind Speed (m/s)**

This enables real-time, hyper-local weather forecasting for remote deployments — especially useful in outdoor or mountainous regions where weather stations are sparse.

---

### 📦 Dataset

We trained our model using the [BGC-Jena Climate Dataset](https://www.bgc-jena.mpg.de/wetter/), which provides comprehensive weather sensor readings at **10-minute intervals**.

Key Features:
- `T (degC)`: Temperature
- `rh (%)`: Relative Humidity
- `p (mbar)`: Air Pressure
- `wv (m/s)`: Wind Speed

---

### ⏳ Problem Formulation: Time Series Forecasting

We use a **sliding window** approach for training:
- **Input Window**: Last 27 time steps (i.e. past 270 minutes) (CNNs were used, with a kernel size of 4)
- **Output Window**: Next 24 time steps (i.e. 4 hours into the future)

This allows the model to learn temporal patterns and forecast trends for each feature.

---

### 🛠️ Frameworks Used

- **Training**: TensorFlow (Keras API)
- **Inference**: TensorFlow Lite for on-device execution
- Optimized for **Raspberry Pi 5** using TFLite’s lightweight runtime

---

### 🧪 Models Experimented

| Model               | Description                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| **Baseline**        | Predicts the last observed value for all future time steps (one for each weather variable)  |
| **CNN (per feature)** | Separate convolutional models for each weather variable                    |
| **Multi-output CNN** | A single model that predicts all 4 features at once for all 24 time steps |

---

### ✅ Why Multi-Output CNN Was Chosen

- Comparable accuracy to individual CNNs
- But with **much smaller model size** and **lower inference overhead**
- Ideal for real-time forecasting on **resource-constrained edge devices** like Raspberry Pi

---

### 📊 Experimental Results

#### 🔹 MAE and RMSE Comparison

| Model            | MAE (Temp) | MAE (Pressure) | MAE (Humidity) | MAE (Wind Speed) | RMSE (Temp) | RMSE (Pressure) | RMSE (Humidity) | RMSE (Wind Speed) |
|------------------|------------|----------------|----------------|------------------|-------------|------------------|------------------|--------------------|
| **Baseline (4 models)**     | TBC       | TBC           | TBC          | TBC             | TBC        | TBC             |TBC            | TBC               |
| **CNN (4 models)**     | TBC     | TBC         | TBC         | TBC           | TBC      | TBC          | TBC          | TBC             |
| **Multi-output CNN** | **0.976**       | 0.504           | 3.972           | 0.673            | 1.392        | 0.693             | 5.890             | 0.911               |

#### 🔹 Model Size Comparison (TFLite)

| Model Type        | Approximate TFLite Model Size |
|-------------------|-------------------------------|
| **Baseline (x4)**     | ~48 KB (4 x 12 KB)              |
| **CNN (4 models)**     | ~196 KB (4 × 49 KB)              |
| **Multi-output CNN** | **115 KB**                        |

✅ **Conclusion**:  
The **multi-output CNN** achieves near-parity in accuracy with the individual CNNs, while drastically reducing model size and computational overhead — making it ideal for **real-time, on-device inference** on edge devices like the Raspberry Pi.

---

### 📦 Deployment Details

- The final **multi-output CNN** model is exported as a `.tflite` file.
- It runs directly on a Raspberry Pi 5 via `tflite-runtime`.
- Inference is quick - forecasts are published via MQTT every 10 minutes.

## 4. Web Dashboard

For the main dashboard, we would have a map of Singapore, which shows all the active weather stations (But we only have 1 for now), and each weather station would display their safety alert consisting of AVOID, CAUTION, AVOID which is dependent on the data that we receive/predict. 

![image](https://github.com/user-attachments/assets/5da9ca03-a85f-42c5-8d3b-c9e87254b46e)

For more information, if the user clicks on a weather station it would show 4 charts: Temperature, Humidity, Pressure, Wind Speed, it will show the next 4 predicted hours' reading.

![image](https://github.com/user-attachments/assets/9087e83a-658b-4d37-9d20-5093f774c85b)


## 5. Project Progress

### March 1 – March 7
**Initial Research & Cloud Training**  
- Okay, so for the first week, we started off by messing around with different ML models on the cloud. We tried out a basic model, a CNN, and a multi-output CNN—this last one had the best results because it can handle all sensors together and is 42% smaller than running four separate CNNs. 

### March 8 – March 10
**Locking in the Model & Setting Up Pi #2**  
- From March 8 to 10, we got serious about which model to use. After checking out the MAE and RMSE, we all agreed that the multi-output CNN was the best choice.
- Meanwhile, we set up our Raspberry Pi #2 for inference. We installed all the libraries (TensorFlow, etc.) and copied over the trained models from the cloud. We did a quick test on Pi #2 to make sure everything runs smoothly.

### March 11 – March 14
**Testing on Pi #2 & Integrating the System**  
- This week, we ran some tests on Pi #2 using sample sensor data. We checked out the inference time, CPU usage. The multi-output CNN proved to be solid.
- At the same time, we got busy on Pi #1: setting up our front-end and back-end. We used ngrok to expose our endpoints securely and tested our communication with MQTT. We also made sure that Pi #3 (the sensor-reading unit) can send data over to Pi #2. Everything was connected and working so far

### March 15 – March 17
**Tweaking the Model & Benchmarking**  
- From 15th to 17th, we tried some optimizations on the multi-output CNN – things like quantization and pruning to see if we can get it running even faster on Pi #2.
- We then compared the baseline and our multi-output CNN side by side. The numbers (latency, CPU, memory) all pointed to the multi-output CNN being our champion.

### March 18 – March 20
**Front-End & Back-End Fine-Tuning**  
- This period was all about polishing things up. On Pi #1, we built a simple web dashboard using JS to show live sensor data and predictions such as adding some nice charts and stuff so it’s easy to see what’s happening in real time.
- We also stress-tested our back-end (MQTT/HTTP endpoints) to make sure they can handle continuous data from Pi #3. Our GitHub readme got updated with detailed notes on why we chose the multi-output CNN and how all three Pis work together.

### March 21 – March 23
**Hardening the Deployment & CI/CD Setup**  
- Between March 21 and 23, we set up startup scripts for our Pis so that everything auto-runs on reboot. 

### March 24 – March 26
**Extended Testing & Front-End Improvements**  
- From the 24th to 26th, we let our system run in a real environment (SIT Tennis court) to see if any issues pop up. We tweaked sensor sampling rates and even tried out TensorFlow Lite for faster inference.
- We also spent time making the front-end more user-friendly such as adding in a map visualisation

### March 27 – March 29
**Final Validation & Wrap-Up**  
- In the last few days, we did our final checks. We compared the baseline, single CNN, and multi-output CNN once more, confirming that the multi-output CNN has the best accuracy and is much smaller (42% less) than running four separate models.
- We made sure the sensor readings from Pi #3 show up correctly on the dashboard. Also, we recorded some demo videos and took screenshots for our GitHub documentation.

