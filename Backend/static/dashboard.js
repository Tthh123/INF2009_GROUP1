// Initialize Socket.IO connection
const socket = io();

// Global variables to hold current sensor and forecast data
let currentReading = null;
let forecastData = null;

// Listen for sensor updates and update currentReading
socket.on("sensor_update", (data) => {
    console.log("Sensor update received:", data);
    currentReading = data;
});

// Listen for forecast updates and update forecastData
socket.on("forecast_update", (data) => {
    console.log("Forecast update received:", data);
    forecastData = data;
});

// Initialize Leaflet map centered on Singapore
const map = L.map('map').setView([1.3521, 103.8198], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

// Add a marker at a hardcoded location (Singapore)
const marker = L.marker([1.3521, 103.8198]).addTo(map);
marker.bindPopup("Click here for detailed sensor data");

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
            label: "Temperature (°C)",
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

// When the marker is clicked, display the charts
marker.on('click', function() {
    // Assume there is a div with id "charts-container" to show the charts
    createCharts();
});
