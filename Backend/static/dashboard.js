// Initialize Socket.IO connection
const socket = io();

// Global variables to hold current sensor and forecast data
let currentReading = null;
let forecastData = null;

// Listen for sensor updates and update currentReading and safety indicators
socket.on("sensor_update", (data) => {
    console.log("Sensor update received:", data);
    currentReading = data;
    updateSafetyIndicators();
});


// Listen for forecast updates and update forecastData and safety indicators
socket.on("forecast_update", (data) => {
    console.log("Forecast update received:", data);
    forecastData = data;
    updateSafetyIndicators();
});

// Initialize Leaflet map centered on the new coordinates for Singapore
const map = L.map('map').setView([1.4137857851172828, 103.91225886502723], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Add a marker at the specified location
const marker = L.marker([1.4137857851172828, 103.91225886502723]).addTo(map);
marker.bindPopup("Click here for detailed sensor data");

// Function to update safety indicators for wind speed, air pressure, and humidity
function updateSafetyIndicators() {
    // Ensure we have both current and forecast data with at least one prediction
    if (!currentReading || !forecastData || forecastData.predictions.length === 0) {
        return;
    }
    
    // Use the first forecast prediction for analysis
    const forecastReading = forecastData.predictions[0];
    
    // --- Wind Speed Safety Indicator ---
    const currentWindSpeed = currentReading.wind_speed; // in m/s
    const forecastWindSpeed = forecastReading.wind_speed; // in m/s
    const currentWindKmh = currentWindSpeed * 3.6;
    const forecastWindKmh = forecastWindSpeed * 3.6;
    const windDiff = forecastWindKmh - currentWindKmh;
    let windSafety = "Safe";
    if (windDiff >= 10) {
        windSafety = "Avoid";
    } else if (windDiff >= 5) {
        windSafety = "Caution";
    }
    
    // --- Air Pressure Safety Indicator ---
    const currentPressure = currentReading.air_pressure; // in hPa
    const forecastPressure = forecastReading.air_pressure; // in hPa
    const pressureDiff = forecastPressure - currentPressure;
    let pressureSafety = "Safe";
    // A drop in pressure may indicate unstable weather
    if (pressureDiff <= -5) {
        pressureSafety = "Avoid";
    } else if (pressureDiff <= -3) {
        pressureSafety = "Caution";
    }
    
    // --- Humidity Safety Indicator ---
    const currentHumidity = currentReading.humidity; // in %
    const forecastHumidity = forecastReading.humidity; // in %
    const humidityDiff = forecastHumidity - currentHumidity;
    let humiditySafety = "Safe";
    // A significant increase in humidity might indicate discomfort or rain
    if (humidityDiff >= 20) {
        humiditySafety = "Avoid";
    } else if (humidityDiff >= 10) {
        humiditySafety = "Caution";
    }
    
    // Remove previous safety markers if they exist
    if (window.safetyMarkerWind) {
        map.removeLayer(window.safetyMarkerWind);
    }
    if (window.safetyMarkerPressure) {
        map.removeLayer(window.safetyMarkerPressure);
    }
    if (window.safetyMarkerHumidity) {
        map.removeLayer(window.safetyMarkerHumidity);
    }
    
    // Get the main marker's location and define an offset (in degrees)
    const markerLatLng = marker.getLatLng();
    const offset = 0.005;
    
    // Create a custom icon for wind speed indicator (displayed to the east)
    const windIcon = L.divIcon({
        className: 'safety-indicator',
        html: `<div style="background: white; border: 2px solid black; padding: 4px; border-radius: 4px;">Wind: ${windSafety}</div>`,
        iconSize: [80, 20],
        iconAnchor: [0, 0]
    });
    const windLatLng = L.latLng(markerLatLng.lat, markerLatLng.lng + offset);
    window.safetyMarkerWind = L.marker(windLatLng, { icon: windIcon, interactive: false }).addTo(map);
    
    // Create a custom icon for air pressure indicator (displayed to the north)
    const pressureIcon = L.divIcon({
        className: 'safety-indicator',
        html: `<div style="background: white; border: 2px solid black; padding: 4px; border-radius: 4px;">Pressure: ${pressureSafety}</div>`,
        iconSize: [100, 20],
        iconAnchor: [0, 0]
    });
    const pressureLatLng = L.latLng(markerLatLng.lat + offset, markerLatLng.lng);
    window.safetyMarkerPressure = L.marker(pressureLatLng, { icon: pressureIcon, interactive: false }).addTo(map);
    
    // Create a custom icon for humidity indicator (displayed to the west)
    const humidityIcon = L.divIcon({
        className: 'safety-indicator',
        html: `<div style="background: white; border: 2px solid black; padding: 4px; border-radius: 4px;">Humidity: ${humiditySafety}</div>`,
        iconSize: [100, 20],
        iconAnchor: [0, 0]
    });
    const humidityLatLng = L.latLng(markerLatLng.lat, markerLatLng.lng - offset);
    window.safetyMarkerHumidity = L.marker(humidityLatLng, { icon: humidityIcon, interactive: false }).addTo(map);
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
