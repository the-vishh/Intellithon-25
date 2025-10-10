// API Configuration - Replace with your backend URL
const API_BASE_URL = "http://localhost:5000/api"; // Change this to your backend URL

// Chart.js default configuration
Chart.defaults.color = "#e5e7eb";
Chart.defaults.borderColor = "rgba(255, 255, 255, 0.1)";

// Fetch dashboard data from backend
async function fetchDashboardData() {
  try {
    // TODO: Replace with your actual API endpoint
    const response = await fetch(`${API_BASE_URL}/dashboard`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching dashboard data:", error);
    // Return mock data if API fails
    return getMockData();
  }
}

// Mock data for testing (remove when backend is ready)
function getMockData() {
  return {
    dailyAttempts: 1234,
    blockedPercentage: 89,
    newVariants: 12,
    topSource: "Social Media",
    miniTrend: [20, 35, 30, 45, 50, 55, 48],
    threatSources: {
      labels: ["Social Media", "Email", "SMS", "Other"],
      data: [45, 30, 15, 10],
      colors: ["#3b82f6", "#10b981", "#06b6d4", "#8b5cf6"],
    },
    phishingTrend: {
      labels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"],
      data: [20, 35, 45, 50, 65, 70, 60],
    },
    attackDistribution: {
      labels: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
      data: [30, 45, 35, 50, 55, 60, 52, 48, 42, 38],
    },
  };
}

// Update dashboard statistics
function updateStats(data) {
  document.getElementById("daily-attempts").textContent =
    data.dailyAttempts.toLocaleString();
  document.getElementById(
    "blocked-percentage"
  ).textContent = `${data.blockedPercentage}%`;
  document.getElementById("new-variants").textContent = data.newVariants;
  document.getElementById("top-source").textContent = data.topSource;
}

// Create mini trend chart
function createMiniTrendChart(data) {
  const ctx = document.getElementById("miniTrendChart").getContext("2d");
  const canvas = document.getElementById("miniTrendChart");

  // Set explicit dimensions
  canvas.style.maxWidth = "200px";
  canvas.style.height = "50px";

  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.map((_, i) => i + 1),
      datasets: [
        {
          data: data,
          borderColor: "#4ade80",
          backgroundColor: "rgba(74, 222, 128, 0.1)",
          borderWidth: 2,
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          pointBackgroundColor: "#4ade80",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
      scales: {
        x: { display: false },
        y: { display: false },
      },
      layout: {
        padding: 0,
      },
    },
  });
}

// Create threat sources pie chart
function createThreatPieChart(data) {
  const ctx = document.getElementById("threatPieChart").getContext("2d");
  new Chart(ctx, {
    type: "pie",
    data: {
      labels: data.labels,
      datasets: [
        {
          data: data.data,
          backgroundColor: data.colors,
          borderWidth: 2,
          borderColor: "#3c3c50",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            padding: 15,
            font: { size: 12 },
            color: "#e5e7eb",
          },
        },
      },
    },
  });
}

// Create phishing trend line chart
function createTrendLineChart(data) {
  const ctx = document.getElementById("trendLineChart").getContext("2d");
  new Chart(ctx, {
    type: "line",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Phishing Attempts",
          data: data.data,
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.3)",
          borderWidth: 3,
          tension: 0.4,
          fill: true,
          pointRadius: 4,
          pointBackgroundColor: "#3b82f6",
          pointBorderColor: "#fff",
          pointBorderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#9ca3af" },
        },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255, 255, 255, 0.1)" },
          ticks: { color: "#9ca3af" },
        },
      },
    },
  });
}

// Create attack distribution bar chart
function createDistributionBarChart(data) {
  const ctx = document.getElementById("distributionBarChart").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: data.labels,
      datasets: [
        {
          label: "Attacks",
          data: data.data,
          backgroundColor: "#4ade80",
          borderRadius: 4,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#9ca3af" },
        },
        y: {
          beginAtZero: true,
          grid: { color: "rgba(255, 255, 255, 0.1)" },
          ticks: { color: "#9ca3af" },
        },
      },
    },
  });
}

// Initialize dashboard
async function initDashboard() {
  const data = await fetchDashboardData();

  updateStats(data);
  createMiniTrendChart(data.miniTrend);
  createThreatPieChart(data.threatSources);
  createTrendLineChart(data.phishingTrend);
  createDistributionBarChart(data.attackDistribution);
}

// Auto-refresh dashboard every 30 seconds
function setupAutoRefresh() {
  setInterval(async () => {
    console.log("Refreshing dashboard data...");
    const data = await fetchDashboardData();
    updateStats(data);
  }, 30000); // 30 seconds
}

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
  initDashboard();
  setupAutoRefresh();
});

// Export functions for external use
window.dashboardAPI = {
  refresh: initDashboard,
  fetchData: fetchDashboardData,
};
