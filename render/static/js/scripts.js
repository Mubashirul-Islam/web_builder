// fetch("/monitor/")
//     .then(response => response.json())
//     .then(data => {
//         document.getElementById("content").innerHTML = `
//             <p><b>CPU Usage:</b> ${data.cpu_percent}%</p>
//             <p><b>Memory Usage:</b> ${data.memory_percent}%</p>
//             <p><b>Process CPU Usage:</b> ${data.process_cpu_percent}%</p>
//             <p><b>Process Memory Usage:</b> ${data.process_memory_mb}%</p>
        
//         `;
//     })
//     .catch(error => {
//         document.getElementById("content").innerText = "Error loading data";
//         console.error(error);
//     });