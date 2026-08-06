/**
 * BMI Calculator & Health Tracker - Frontend Logic
 * Interactive client-side JavaScript handling API calls, live clock,
 * Chart.js visualization, dynamic history updates, and DOM interactions.
 */

let bmiChart = null;
let lastCalculatedData = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    initClock();
    fetchUserList();
    initChart();
});

/**
 * Updates live date & time clock every second.
 */
function initClock() {
    const clockEl = document.getElementById("liveClock");
    function update() {
        const now = new Date();
        clockEl.textContent = now.toLocaleString("en-US", {
            weekday: "short",
            month: "short",
            day: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit"
        });
    }
    update();
    setInterval(update, 1000);
}

/**
 * Fetches distinct users from database and fills datalist auto-suggest dropdown.
 */
async function fetchUserList() {
    try {
        const res = await fetch("/api/users");
        const json = await res.json();
        if (json.success && json.users) {
            const datalist = document.getElementById("userList");
            datalist.innerHTML = json.users.map(u => `<option value="${escapeHtml(u)}">`).join("");
        }
    } catch (e) {
        console.error("Failed to load user list:", e);
    }
}

/**
 * Handles BMI calculation request.
 */
async function handleCalculate() {
    const username = document.getElementById("usernameInput").value.trim();
    const weight = document.getElementById("weightInput").value.trim();
    const height = document.getElementById("heightInput").value.trim();

    if (!username) { alert("Please enter a username."); return; }
    if (!weight) { alert("Please enter weight in kg."); return; }
    if (!height) { alert("Please enter height in meters."); return; }

    try {
        const res = await fetch("/api/calculate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, weight, height })
        });
        const json = await res.json();

        if (!json.success) {
            alert("Input Error: " + json.error);
            return;
        }

        const data = json.data;
        lastCalculatedData = data;

        // Update UI Result Card
        const bmiDisplay = document.getElementById("bmiValueDisplay");
        const badge = document.getElementById("categoryBadge");
        const message = document.getElementById("healthMessage");

        bmiDisplay.textContent = data.bmi.toFixed(2);
        bmiDisplay.style.color = data.color;

        badge.textContent = `CATEGORY: ${data.category.toUpperCase()}`;
        badge.style.backgroundColor = data.color;
        badge.style.color = "#FFFFFF";

        message.textContent = data.message;

        // Auto fetch history for this user
        handleFetchHistory(false);

    } catch (e) {
        alert("Server Error: " + e.message);
    }
}

/**
 * Saves current calculation to SQLite database.
 */
async function handleSave() {
    if (!lastCalculatedData) {
        // Trigger calculation if not done yet
        await handleCalculate();
        if (!lastCalculatedData) return;
    }

    try {
        const res = await fetch("/api/save", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(lastCalculatedData)
        });
        const json = await res.json();

        if (!json.success) {
            alert("Database Error: " + json.error);
            return;
        }

        alert(`Record Saved Successfully!\nSaved entry ID #${json.id} for user '${lastCalculatedData.username}'.`);
        fetchUserList();
        handleFetchHistory(true);

    } catch (e) {
        alert("Save Error: " + e.message);
    }
}

/**
 * Fetches user history and updates history table and Chart.js graph.
 */
async function handleFetchHistory(showAlertIfEmpty = true) {
    const username = document.getElementById("usernameInput").value.trim();
    if (!username) {
        if (showAlertIfEmpty) alert("Please enter a username to fetch history.");
        return;
    }

    document.getElementById("activeUserPill").textContent = `Active User: ${username}`;

    try {
        const res = await fetch(`/api/history/${encodeURIComponent(username)}`);
        const json = await res.json();

        if (!json.success) {
            alert("Error fetching history: " + json.error);
            return;
        }

        const records = json.records || [];
        renderHistoryTable(records);
        renderChart(username, records);

        if (records.length === 0 && showAlertIfEmpty) {
            alert(`No history records found for user '${username}'.`);
        }

    } catch (e) {
        console.error("Failed to fetch history:", e);
    }
}

/**
 * Renders history records into table DOM.
 */
function renderHistoryTable(records) {
    const tbody = document.getElementById("historyTableBody");
    if (records.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No records saved for this user yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = records.map(r => `
        <tr>
            <td>${escapeHtml(r.date)}</td>
            <td>${r.weight.toFixed(1)}</td>
            <td>${r.height.toFixed(2)}</td>
            <td><strong>${r.bmi.toFixed(2)}</strong></td>
            <td><span class="category-badge" style="background:${getCategoryColor(r.category)}; color:#fff; font-size:0.75rem; padding:2px 8px;">${escapeHtml(r.category)}</span></td>
            <td><button class="btn-delete-row" onclick="handleDeleteRecord(${r.id})">🗑️ Delete</button></td>
        </tr>
    `).join("");
}

/**
 * Deletes a specific record entry by ID.
 */
async function handleDeleteRecord(id) {
    if (!confirm(`Are you sure you want to delete Record ID #${id}?`)) return;

    try {
        const res = await fetch(`/api/record/${id}`, { method: "DELETE" });
        const json = await res.json();
        if (json.success) {
            handleFetchHistory(false);
            fetchUserList();
        } else {
            alert("Delete Error: " + json.error);
        }
    } catch (e) {
        alert("Error deleting record: " + e.message);
    }
}

/**
 * Clears all history records for active user.
 */
async function handleClearUserHistory() {
    const username = document.getElementById("usernameInput").value.trim();
    if (!username) { alert("Please enter a username."); return; }

    if (!confirm(`Are you sure you want to PERMANENTLY delete all records for user '${username}'?`)) return;

    try {
        const res = await fetch(`/api/user-history/${encodeURIComponent(username)}`, { method: "DELETE" });
        const json = await res.json();
        if (json.success) {
            alert(json.message);
            handleFetchHistory(false);
            fetchUserList();
        } else {
            alert("Clear Error: " + json.error);
        }
    } catch (e) {
        alert("Error clearing history: " + e.message);
    }
}

/**
 * Clears form inputs and resets calculation result display.
 */
function handleClear() {
    document.getElementById("usernameInput").value = "";
    document.getElementById("weightInput").value = "";
    document.getElementById("heightInput").value = "";

    const bmiDisplay = document.getElementById("bmiValueDisplay");
    const badge = document.getElementById("categoryBadge");
    const message = document.getElementById("healthMessage");

    bmiDisplay.textContent = "--.--";
    bmiDisplay.style.color = "#94A3B8";

    badge.textContent = "Enter details and click 'Calculate'";
    badge.style.backgroundColor = "#F1F5F9";
    badge.style.color = "#475569";

    message.textContent = "Your personalized health recommendation will appear here.";

    lastCalculatedData = null;
    document.getElementById("historyTableBody").innerHTML = `<tr><td colspan="6" class="empty-state">No user history loaded.</td></tr>`;
    document.getElementById("activeUserPill").textContent = "Select a user to view trends";

    if (bmiChart) {
        bmiChart.destroy();
        bmiChart = null;
    }
}

/**
 * Trigger show graph explicitly.
 */
function handleShowGraph() {
    handleFetchHistory(true);
}

/**
 * Initializes empty Chart.js line plot.
 */
function initChart() {
    const ctx = document.getElementById("bmiChart").getContext("2d");
    bmiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'BMI Trend',
                data: [],
                borderColor: '#2563EB',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2.5,
                pointRadius: 5,
                pointHoverRadius: 7,
                fill: true,
                tension: 0.2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: true, position: 'top' },
                tooltip: { callbacks: { label: ctx => `BMI: ${ctx.parsed.y}` } }
            },
            scales: {
                y: {
                    suggestedMin: 15,
                    suggestedMax: 35,
                    title: { display: true, text: 'BMI Value' }
                },
                x: {
                    title: { display: true, text: 'Date & Time' }
                }
            }
        }
    });
}

/**
 * Updates Chart.js dataset with fresh user history records.
 */
function renderChart(username, records) {
    if (!bmiChart) initChart();

    const labels = records.map(r => r.date);
    const dataPoints = records.map(r => r.bmi);

    bmiChart.data.labels = labels;
    bmiChart.data.datasets[0].label = `${username}'s BMI Progress`;
    bmiChart.data.datasets[0].data = dataPoints;
    bmiChart.update();
}

/**
 * Helper to get hex color code for BMI category.
 */
function getCategoryColor(category) {
    switch (category.toLowerCase()) {
        case "underweight": return "#2563EB";
        case "normal weight": return "#16A34A";
        case "overweight": return "#EA580C";
        case "obese": return "#DC2626";
        default: return "#64748B";
    }
}

/**
 * Helper to escape HTML characters.
 */
function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
