// Initialize Socket.IO connection
const socket = io();

// Global variables to hold current sensor and forecast data
let currentReading = null;
let forecastData = null;

// Listen for sensor updates and update currentReading and the overall safety indicator
socket.on("sensor_update", (data) => {
    console.log("Sensor update received:", data);
    currentReading = data;
    updateSafetyFusion();
});

// Listen for forecast updates and update forecastData and the overall safety indicator
socket.on("forecast_update", (data) => {
    console.log("Forecast update received:", data);
    forecastData = data;
    updateSafetyFusion();
});

// Initialize Leaflet map centered on the new coordinates for Singapore
const map = L.map('map').setView([1.4137857851172828, 103.91225886502723], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Add a marker at the specified location
const marker = L.marker([1.4137857851172828, 103.91225886502723]).addTo(map);
marker.bindPopup("Click here for detailed sensor data");

// Function to update the overall safety indicator using sensor fusion
function updateSafetyFusion() {
    // Ensure we have both current and forecast data with at least one prediction
    if (!currentReading || !forecastData || forecastData.predictions.length === 0) {
        return;
    }
    
    // Use the first forecast prediction for the sensor fusion
    const forecastReading = forecastData.predictions[0];
    
    // --- Wind Speed (convert m/s to km/h) ---
    const currentWindKmh = currentReading.wind_speed * 3.6;
    const forecastWindKmh = forecastReading.wind_speed * 3.6;
    let windRisk = 0;
    const windDiff = forecastWindKmh - currentWindKmh;
    if (windDiff >= 10) {
        windRisk = 2;
    } else if (windDiff >= 5) {
        windRisk = 1;
    }
    
    // --- Air Pressure ---
    let pressureRisk = 0;
    const pressureDiff = forecastReading.air_pressure - currentReading.air_pressure;
    if (pressureDiff <= -5) {
        pressureRisk = 2;
    } else if (pressureDiff <= -3) {
        pressureRisk = 1;
    }
    
    // --- Humidity ---
    let humidityRisk = 0;
    const humidityDiff = forecastReading.humidity - currentReading.humidity;
    if (humidityDiff >= 20) {
        humidityRisk = 2;
    } else if (humidityDiff >= 10) {
        humidityRisk = 1;
    }
    
    // --- Temperature ---
    let temperatureRisk = 0;
    const tempDiff = Math.abs(forecastReading.temperature - currentReading.temperature);
    if (tempDiff >= 5) {
        temperatureRisk = 2;
    } else if (tempDiff >= 3) {
        temperatureRisk = 1;
    }
    
    // Sensor Fusion: Determine overall risk using the highest risk level detected
    const riskScores = [windRisk, pressureRisk, humidityRisk, temperatureRisk];
    let overallRisk = "SAFE";
    if (riskScores.includes(2)) {
        overallRisk = "AVOID";
    } else if (riskScores.includes(1)) {
        overallRisk = "CAUTION";
    } else {
        overallRisk = "SAFE";
    }
    
    // Remove previous overall safety marker if it exists
    if (window.overallSafetyMarker) {
        map.removeLayer(window.overallSafetyMarker);
    }
    
    // Create a custom div icon for the overall safety indicator
    const overallIcon = L.divIcon({
        className: 'safety-indicator',
        html: `<div style="background: white; border: 2px solid black; padding: 4px; border-radius: 4px;">Overall: ${overallRisk}</div>`,
        iconSize: [120, 20],
        iconAnchor: [0, 0]
    });
    
    // Place the overall safety indicator at an offset from the main marker (north-east)
    const markerLatLng = marker.getLatLng();
    const offset = 0.005;
    const overallLatLng = L.latLng(markerLatLng.lat + offset, markerLatLng.lng + offset);
    window.overallSafetyMarker = L.marker(overallLatLng, { icon: overallIcon, interactive: false }).addTo(map);
}

// Function to create charts using Chart.js
function createCharts() {
    if (!currentReading || !forecastData) {
        alert("Sensor or forecast data not available yet.");
        return;
    }

    // Define labels: "Now" and then the times from forecast predictions
    const labels = ["Now", ...forecastData.predictions.map(pred => {
        const date = new Date(pred.timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    })];

    // Define metrics to chart: current reading plus forecast values
    const metrics = {
        temperature: {
            label: "Temperature (C)",
            current: currentReading.temperature,
            forecast: forecastData.predictions.map(pred => pred.temperature)
        },
        wind_speed: {
            label: "Wind Speed (m/s)",
            current: currentReading.wind_speed,
            forecast: forecastData.predictions.map(pred => pred.wind_speed)
        },
        air_pressure: {
            label: "Air Pressure (hPa)",
            current: currentReading.air_pressure,
            forecast: forecastData.predictions.map(pred => pred.air_pressure)
        },
        humidity: {
            label: "Humidity (%)",
            current: currentReading.humidity,
            forecast: forecastData.predictions.map(pred => pred.humidity)
        }
    };

    // Get the charts container and clear any existing content
    const chartsContainer = document.getElementById("charts-container");
    chartsContainer.innerHTML = ""; // Clear previous charts

    // For each metric, create a canvas and draw the chart
    for (const key in metrics) {
        const metric = metrics[key];

        // Create a new canvas element for the chart
        const canvas = document.createElement("canvas");
        canvas.id = key + "-chart";
        chartsContainer.appendChild(canvas);

        // Create a new line chart using Chart.js
        new Chart(canvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: metric.label,
                    data: [metric.current, ...metric.forecast],
                    fill: false,
                    borderColor: 'blue',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
}

// When the main marker is clicked, display the charts
marker.on('click', function() {
    // Assume there is a div with id "charts-container" to show the charts
    createCharts();
});
