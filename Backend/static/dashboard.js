const tableBody = document.querySelector("#data-table tbody");

const socket = io();

socket.on("sensor_update", (entry) => {
  const row = document.createElement("tr");
  row.innerHTML = `
    <td>${new Date(entry.timestamp).toLocaleString()}</td>
    <td>${entry.temp ?? '-'}</td>
    <td>${entry.humidity ?? '-'}</td>
    <td>${entry.location ?? '-'}</td>
  `;
  // Insert new data at the top
  tableBody.prepend(row);
});
