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

function updateSafetyFusion() {
    // Ensure we have both current and forecast data with at least one prediction
    if (!currentReading || !forecastData || forecastData.predictions.length === 0) {
        return;
    }
    
    // Use only the next 4 forecast predictions (or fewer if not available)
    const forecasts = forecastData.predictions.slice(0, 4);
    let maxOverallRiskValue = 0;
    
    // Calculate overall trends between current reading and the last forecast:
    // --- Pressure Trend ---
    const initialPressure = currentReading.air_pressure;
    const finalPressure = forecasts[forecasts.length - 1].air_pressure;
    const pressureDrop = initialPressure - finalPressure;
    let pressureTrendRisk = 0;
    if (pressureDrop >= 5) {
        pressureTrendRisk = 2;
    } else if (pressureDrop >= 3) {
        pressureTrendRisk = 1;
    }
    
    // --- Humidity Trend ---
    const initialHumidity = currentReading.humidity;
    const finalHumidity = forecasts[forecasts.length - 1].humidity;
    const humidityIncrease = finalHumidity - initialHumidity;
    let humidityTrendRisk = 0;
    if (humidityIncrease >= 20) {
        humidityTrendRisk = 2;
    } else if (humidityIncrease >= 10) {
        humidityTrendRisk = 1;
    }
    
    forecasts.forEach(forecastReading => {
        // --- Wind Speed (convert m/s to km/h) ---
        const currentWindKmh = currentReading.wind_speed * 3.6;
        const forecastWindKmh = forecastReading.wind_speed * 3.6;
        
        // Relative risk for wind speed (change from current reading)
        let windRelativeRisk = 0;
        const windDiff = forecastWindKmh - currentWindKmh;
        if (windDiff >= 10) {
            windRelativeRisk = 2;
        } else if (windDiff >= 5) {
            windRelativeRisk = 1;
        }
        // Absolute risk for wind speed (using thresholds suitable for Singapore)
        let windAbsoluteRisk = 0;
        if (forecastWindKmh >= 50) { // unusually strong winds
            windAbsoluteRisk = 2;
        } else if (forecastWindKmh >= 40) {
            windAbsoluteRisk = 1;
        }
        const windRisk = Math.max(windRelativeRisk, windAbsoluteRisk);
        
        // --- Air Pressure ---
        let pressureRelativeRisk = 0;
        const pressureDiff = forecastReading.air_pressure - currentReading.air_pressure;
        if (pressureDiff <= -5) {
            pressureRelativeRisk = 2;
        } else if (pressureDiff <= -3) {
            pressureRelativeRisk = 1;
        }
        let pressureAbsoluteRisk = 0;
        if (forecastReading.air_pressure < 1005) {
            pressureAbsoluteRisk = 2;
        } else if (forecastReading.air_pressure < 1010) {
            pressureAbsoluteRisk = 1;
        }
        // Combine the per-forecast risk with the trend risk
        const pressureRisk = Math.max(pressureRelativeRisk, pressureAbsoluteRisk, pressureTrendRisk);
        
        // --- Humidity ---
        let humidityRisk = 0;
        if (forecastReading.humidity >= 90) {
            humidityRisk = 2;
        } else if (forecastReading.humidity >= 80) {
            humidityRisk = 1;
        }
        // Combine with the trend risk
        const totalHumidityRisk = Math.max(humidityRisk, humidityTrendRisk);
        
        // --- Temperature ---
        let temperatureRisk = 0;
        // If the current temperature is already very high, skip further checks
        if (currentReading.temperature >= 35) {
            temperatureRisk = 2;
        } else {
            // Relative change check
            const tempDiff = Math.abs(forecastReading.temperature - currentReading.temperature);
            if (tempDiff >= 5) {
                temperatureRisk = 2;
            } else if (tempDiff >= 3) {
                temperatureRisk = 1;
            }
            // Absolute temperature thresholds for dangerous conditions in Singapore
            if (forecastReading.temperature >= 35) {
                temperatureRisk = Math.max(temperatureRisk, 2);
            } else if (forecastReading.temperature >= 33) {
                temperatureRisk = Math.max(temperatureRisk, 1);
            }
        }
        
        // --- Rain Formation Risk ---
        // Using meteorological principles:
        // - Warmer temperatures increase air's moisture capacity.
        // - A drop in pressure indicates approaching storm systems.
        // - High humidity near saturation signals condensation potential.
        let rainRisk = 0;
        if (
            forecastReading.temperature >= 33 && 
            forecastReading.humidity >= 80 && 
            forecastReading.air_pressure < 1010
        ) {
            rainRisk = 2;
        } else if (
            forecastReading.temperature >= 32 &&
            forecastReading.humidity >= 75 &&
            forecastReading.air_pressure < 1012
        ) {
            rainRisk = 1;
        }
        
        // Determine overall risk for this forecast reading by taking the maximum risk value
        const forecastRiskValue = Math.max(windRisk, pressureRisk, totalHumidityRisk, temperatureRisk, rainRisk);
        maxOverallRiskValue = Math.max(maxOverallRiskValue, forecastRiskValue);
    });
    
    // Map the maximum risk value to a label
    let overallRisk = "SAFE";
    if (maxOverallRiskValue === 2) {
        overallRisk = "AVOID";
    } else if (maxOverallRiskValue === 1) {
        overallRisk = "CAUTION";
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
    if (!currentReading || !forecastData || forecastData.predictions.length === 0) {
        alert("Sensor or forecast data not available yet.");
        return;
    }
    
    // Use only the next 4 forecast predictions for charting
    const forecastPredictions = forecastData.predictions.slice(0, 4);

    // Define labels: "Now" and then the times from forecast predictions
    const labels = ["Now", ...forecastPredictions.map(pred => {
        const date = new Date(pred.timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    })];

    // Define metrics to chart: current reading plus forecast values
    const metrics = {
        temperature: {
            label: "Temperature (°C)",
            current: currentReading.temperature,
            forecast: forecastPredictions.map(pred => pred.temperature)
        },
        wind_speed: {
            label: "Wind Speed (m/s)",
            current: currentReading.wind_speed,
            forecast: forecastPredictions.map(pred => pred.wind_speed)
        },
        air_pressure: {
            label: "Air Pressure (hPa)",
            current: currentReading.air_pressure,
            forecast: forecastPredictions.map(pred => pred.air_pressure)
        },
        humidity: {
            label: "Humidity (%)",
            current: currentReading.humidity,
            forecast: forecastPredictions.map(pred => pred.humidity)
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
