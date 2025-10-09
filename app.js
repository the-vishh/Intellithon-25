// Dashboard Data and Configuration
// Version: 2.1 - NULL CHECKS FIXED
console.log("✅ App.js v2.1 loaded - All null checks in place");

const dashboardData = {
  heroMetrics: {
    attacksPrevented: 2847,
    sitesScanned: 15432,
    detectionRate: 97.3,
    activeUsers: 1205,
  },
  threatData: [
    { time: "00:00", threats: 12 },
    { time: "02:00", threats: 8 },
    { time: "04:00", threats: 15 },
    { time: "06:00", threats: 23 },
    { time: "08:00", threats: 45 },
    { time: "10:00", threats: 38 },
    { time: "12:00", threats: 52 },
    { time: "14:00", threats: 41 },
    { time: "16:00", threats: 29 },
    { time: "18:00", threats: 36 },
    { time: "20:00", threats: 28 },
    { time: "22:00", threats: 19 },
  ],
  threatTypes: [
    { type: "Phishing", count: 156, color: "#ff4757" },
    { type: "Malware", count: 89, color: "#ff6348" },
    { type: "Suspicious", count: 234, color: "#ffa502" },
    { type: "Safe", count: 8945, color: "#26de81" },
  ],
  topSources: [
    { country: "Unknown/VPN", count: 89 },
    { country: "Russia", count: 67 },
    { country: "China", count: 45 },
    { country: "Nigeria", count: 32 },
    { country: "Brazil", count: 28 },
  ],
  recentActivity: [
    {
      timestamp: "2025-10-09 16:18:42",
      type: "Phishing",
      risk: "High",
      url: "fake-bank-login.com",
      user: "user1@company.com",
    },
    {
      timestamp: "2025-10-09 16:17:31",
      type: "Malware",
      risk: "High",
      url: "malicious-download.net",
      user: "user2@company.com",
    },
    {
      timestamp: "2025-10-09 16:16:15",
      type: "Suspicious",
      risk: "Medium",
      url: "suspicious-email.com",
      user: "user3@company.com",
    },
    {
      timestamp: "2025-10-09 16:15:03",
      type: "Phishing",
      risk: "High",
      url: "fake-paypal.org",
      user: "user4@company.com",
    },
    {
      timestamp: "2025-10-09 16:13:47",
      type: "Safe",
      risk: "Low",
      url: "legitimate-site.com",
      user: "user5@company.com",
    },
  ],
  systemStatus: {
    aiAccuracy: 97.3,
    processingSpeed: 0.23,
    lastUpdate: "2025-10-09 15:30:00",
    queueLength: 47,
    dbStatus: "online",
  },
};

// Chart instances
let threatsChart, threatTypesChart, threatSourcesChart;

// Initialize Dashboard
document.addEventListener("DOMContentLoaded", function () {
  initializeCharts();
  initializeActivityFeed();
  initializeRealTimeUpdates();
  initializeCounters();
  initializeEventListeners();
});

// Initialize Charts
function initializeCharts() {
  // Threats Over Time Chart
  const threatsCtx = document.getElementById("threatsChart").getContext("2d");
  threatsChart = new Chart(threatsCtx, {
    type: "line",
    data: {
      labels: dashboardData.threatData.map((d) => d.time),
      datasets: [
        {
          label: "Threats Detected",
          data: dashboardData.threatData.map((d) => d.threats),
          borderColor: "#1FB8CD",
          backgroundColor: "rgba(31, 184, 205, 0.1)",
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: "#1FB8CD",
          pointBorderColor: "#1FB8CD",
          pointHoverBackgroundColor: "#FFC185",
          pointHoverBorderColor: "#FFC185",
          pointRadius: 4,
          pointHoverRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "rgba(38, 40, 40, 0.9)",
          titleColor: "#f5f5f5",
          bodyColor: "#f5f5f5",
          borderColor: "#1FB8CD",
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              return `Threats: ${context.parsed.y}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: {
            color: "rgba(119, 124, 124, 0.2)",
            drawBorder: false,
          },
          ticks: {
            color: "#a7a9a9",
          },
        },
        y: {
          grid: {
            color: "rgba(119, 124, 124, 0.2)",
            drawBorder: false,
          },
          ticks: {
            color: "#a7a9a9",
          },
        },
      },
      interaction: {
        intersect: false,
        mode: "index",
      },
    },
  });

  // Threat Types Distribution Chart
  const threatTypesCtx = document
    .getElementById("threatTypesChart")
    .getContext("2d");
  threatTypesChart = new Chart(threatTypesCtx, {
    type: "doughnut",
    data: {
      labels: dashboardData.threatTypes.map((t) => t.type),
      datasets: [
        {
          data: dashboardData.threatTypes.map((t) => t.count),
          backgroundColor: dashboardData.threatTypes.map((t) => t.color),
          borderWidth: 2,
          borderColor: "#262828",
          hoverBorderWidth: 3,
          hoverBorderColor: "#1FB8CD",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#f5f5f5",
            padding: 20,
            usePointStyle: true,
            pointStyle: "circle",
          },
        },
        tooltip: {
          backgroundColor: "rgba(38, 40, 40, 0.9)",
          titleColor: "#f5f5f5",
          bodyColor: "#f5f5f5",
          borderColor: "#1FB8CD",
          borderWidth: 1,
          callbacks: {
            label: function (context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              return `${context.label}: ${context.parsed} (${percentage}%)`;
            },
          },
        },
      },
      cutout: "60%",
    },
  });

  // Top Threat Sources Chart
  const threatSourcesCtx = document
    .getElementById("threatSourcesChart")
    .getContext("2d");
  threatSourcesChart = new Chart(threatSourcesCtx, {
    type: "bar",
    data: {
      labels: dashboardData.topSources.map((s) => s.country),
      datasets: [
        {
          label: "Threat Count",
          data: dashboardData.topSources.map((s) => s.count),
          backgroundColor: [
            "#1FB8CD",
            "#FFC185",
            "#B4413C",
            "#ECEBD5",
            "#5D878F",
          ],
          borderColor: "#262828",
          borderWidth: 1,
          borderRadius: 4,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: "rgba(38, 40, 40, 0.9)",
          titleColor: "#f5f5f5",
          bodyColor: "#f5f5f5",
          borderColor: "#1FB8CD",
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          grid: {
            display: false,
          },
          ticks: {
            color: "#a7a9a9",
            maxRotation: 45,
          },
        },
        y: {
          grid: {
            color: "rgba(119, 124, 124, 0.2)",
            drawBorder: false,
          },
          ticks: {
            color: "#a7a9a9",
          },
        },
      },
    },
  });
}

// Initialize Activity Feed
function initializeActivityFeed() {
  const activityList = document.getElementById("activityList");

  // Exit early if element doesn't exist
  if (!activityList) return;

  function renderActivity() {
    if (!activityList) return;

    activityList.innerHTML = "";

    dashboardData.recentActivity.forEach((activity) => {
      const activityItem = document.createElement("div");
      activityItem.className = "activity-item";

      const riskLevel = activity.risk.toLowerCase();
      const timeAgo = getTimeAgo(activity.timestamp);

      activityItem.innerHTML = `
        <div class="activity-icon ${riskLevel}">
          ${getRiskIcon(activity.risk)}
        </div>
        <div class="activity-details">
          <h4>${activity.type} - ${activity.risk} Risk</h4>
          <p>${activity.url} • ${activity.user}</p>
        </div>
        <div class="activity-time">${timeAgo}</div>
      `;

      activityList.appendChild(activityItem);
    });
  }

  renderActivity();
}

// Helper Functions
function getRiskIcon(risk) {
  switch (risk.toLowerCase()) {
    case "high":
      return "⚠️";
    case "medium":
      return "⚡";
    case "low":
      return "✅";
    default:
      return "❓";
  }
}

function getTimeAgo(timestamp) {
  const now = new Date();
  const past = new Date(timestamp);
  const diffInMinutes = Math.floor((now - past) / (1000 * 60));

  if (diffInMinutes < 1) return "Just now";
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;

  const diffInHours = Math.floor(diffInMinutes / 60);
  if (diffInHours < 24) return `${diffInHours}h ago`;

  const diffInDays = Math.floor(diffInHours / 24);
  return `${diffInDays}d ago`;
}

// Counter Animation
function animateCounter(element, targetValue, duration = 2000) {
  const startValue = 0;
  const startTime = performance.now();

  function updateCounter(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // Easing function for smooth animation
    const easeOut = 1 - Math.pow(1 - progress, 3);
    const currentValue = Math.floor(
      startValue + (targetValue - startValue) * easeOut
    );

    if (typeof targetValue === "number" && targetValue > 1000) {
      element.textContent = currentValue.toLocaleString();
    } else if (
      typeof targetValue === "number" &&
      targetValue.toString().includes(".")
    ) {
      element.textContent = currentValue.toFixed(1) + "%";
    } else {
      element.textContent = currentValue;
    }

    if (progress < 1) {
      requestAnimationFrame(updateCounter);
    }
  }

  requestAnimationFrame(updateCounter);
}

// Initialize Counters
function initializeCounters() {
  animateCounter(
    document.getElementById("attacksPrevented"),
    dashboardData.heroMetrics.attacksPrevented
  );
  animateCounter(
    document.getElementById("sitesScanned"),
    dashboardData.heroMetrics.sitesScanned
  );
  animateCounter(
    document.getElementById("detectionRate"),
    dashboardData.heroMetrics.detectionRate
  );
  animateCounter(
    document.getElementById("activeUsers"),
    dashboardData.heroMetrics.activeUsers
  );
}

// Real-time Updates
function initializeRealTimeUpdates() {
  // Update metrics every 30 seconds
  setInterval(updateMetrics, 30000);

  // Update activity feed every 15 seconds
  setInterval(updateActivityFeed, 15000);

  // Update charts every 60 seconds
  setInterval(updateCharts, 60000);

  // Update system status every 10 seconds
  setInterval(updateSystemStatus, 10000);
}

function updateMetrics() {
  // Simulate real-time metric updates
  dashboardData.heroMetrics.attacksPrevented +=
    Math.floor(Math.random() * 5) + 1;
  dashboardData.heroMetrics.sitesScanned += Math.floor(Math.random() * 50) + 20;
  dashboardData.heroMetrics.activeUsers += Math.floor(Math.random() * 3);

  // Update display with animation (only if elements exist)
  const attacksElement = document.getElementById("attacksPrevented");
  const sitesElement = document.getElementById("sitesScanned");
  const usersElement = document.getElementById("activeUsers");

  if (attacksElement) {
    attacksElement.textContent =
      dashboardData.heroMetrics.attacksPrevented.toLocaleString();
  }
  if (sitesElement) {
    sitesElement.textContent =
      dashboardData.heroMetrics.sitesScanned.toLocaleString();
  }
  if (usersElement) {
    usersElement.textContent =
      dashboardData.heroMetrics.activeUsers.toLocaleString();
  }
}

function updateActivityFeed() {
  // Generate new activity
  const newActivity = generateRandomActivity();
  dashboardData.recentActivity.unshift(newActivity);

  // Keep only last 10 activities
  if (dashboardData.recentActivity.length > 10) {
    dashboardData.recentActivity = dashboardData.recentActivity.slice(0, 10);
  }

  initializeActivityFeed();
}

function generateRandomActivity() {
  const types = ["Phishing", "Malware", "Suspicious", "Safe"];
  const risks = ["High", "Medium", "Low"];
  const urls = [
    "suspicious-site.com",
    "fake-login.net",
    "malware-host.org",
    "phishing-attempt.com",
    "legitimate-site.com",
  ];
  const users = [
    "user1@company.com",
    "user2@company.com",
    "user3@company.com",
    "user4@company.com",
    "user5@company.com",
  ];

  const type = types[Math.floor(Math.random() * types.length)];
  let risk;

  // Assign risk based on type
  if (type === "Phishing" || type === "Malware") {
    risk = Math.random() > 0.3 ? "High" : "Medium";
  } else if (type === "Suspicious") {
    risk = "Medium";
  } else {
    risk = "Low";
  }

  return {
    timestamp: new Date().toISOString().replace("T", " ").substr(0, 19),
    type: type,
    risk: risk,
    url: urls[Math.floor(Math.random() * urls.length)],
    user: users[Math.floor(Math.random() * users.length)],
  };
}

function updateCharts() {
  // Update threats over time chart
  const newThreatCount = Math.floor(Math.random() * 30) + 10;
  const currentTime = new Date().toLocaleTimeString("en-US", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
  });

  // Remove oldest data point and add new one
  dashboardData.threatData.shift();
  dashboardData.threatData.push({ time: currentTime, threats: newThreatCount });

  // Update charts
  threatsChart.data.labels = dashboardData.threatData.map((d) => d.time);
  threatsChart.data.datasets[0].data = dashboardData.threatData.map(
    (d) => d.threats
  );
  threatsChart.update("none");

  // Update threat types with small random changes
  dashboardData.threatTypes.forEach((type) => {
    const change = Math.floor(Math.random() * 10) - 5; // -5 to +5
    type.count = Math.max(0, type.count + change);
  });

  threatTypesChart.data.datasets[0].data = dashboardData.threatTypes.map(
    (t) => t.count
  );
  threatTypesChart.update("none");
}

function updateSystemStatus() {
  // Update queue length
  const queueChange = Math.floor(Math.random() * 20) - 10; // -10 to +10
  dashboardData.systemStatus.queueLength = Math.max(
    0,
    dashboardData.systemStatus.queueLength + queueChange
  );

  // Update processing speed (simulate network fluctuations)
  const speedVariation = (Math.random() - 0.5) * 0.1; // ±0.05s
  dashboardData.systemStatus.processingSpeed = Math.max(
    0.1,
    dashboardData.systemStatus.processingSpeed + speedVariation
  );

  // Update display (only if elements exist)
  const queueElement = document.getElementById("queueLength");
  const speedElement = document.getElementById("processingSpeed");

  if (queueElement) {
    queueElement.textContent = dashboardData.systemStatus.queueLength;
  }
  if (speedElement) {
    speedElement.textContent =
      dashboardData.systemStatus.processingSpeed.toFixed(2) + "s";
  }
}

// Event Listeners
function initializeEventListeners() {
  // Navigation items
  document.querySelectorAll(".nav-item").forEach((item, index) => {
    item.addEventListener("click", function (e) {
      e.preventDefault();

      // Remove active class from all items
      document.querySelectorAll(".nav-item").forEach((navItem) => {
        navItem.classList.remove("active");
      });

      // Add active class to clicked item
      this.classList.add("active");

      // Show appropriate content based on navigation
      const navText = this.querySelector(".nav-text").textContent;
      showSection(navText);
    });
  });

  // Time range filter
  document.getElementById("timeRange").addEventListener("change", function () {
    const selectedRange = this.value;
    console.log(`Time range changed to: ${selectedRange}`);

    // Here you would typically update the data based on the selected range
    // For demo purposes, we'll just simulate a small change
    updateCharts();
  });

  // Chart click events for interactivity
  document
    .getElementById("threatsChart")
    .addEventListener("click", function (event) {
      const points = threatsChart.getElementsAtEventForMode(
        event,
        "nearest",
        { intersect: true },
        true
      );
      if (points.length) {
        const firstPoint = points[0];
        const label = threatsChart.data.labels[firstPoint.index];
        const value =
          threatsChart.data.datasets[firstPoint.datasetIndex].data[
            firstPoint.index
          ];
        console.log(`Clicked on ${label}: ${value} threats`);
      }
    });

  // Activity item click events
  document.addEventListener("click", function (e) {
    if (e.target.closest(".activity-item")) {
      const activityItem = e.target.closest(".activity-item");
      activityItem.style.backgroundColor = "rgba(31, 184, 205, 0.1)";
      setTimeout(() => {
        activityItem.style.backgroundColor = "";
      }, 500);
    }
  });
}

// Keyboard shortcuts
document.addEventListener("keydown", function (e) {
  // Ctrl/Cmd + R: Refresh dashboard
  if ((e.ctrlKey || e.metaKey) && e.key === "r") {
    e.preventDefault();
    location.reload();
  }

  // Ctrl/Cmd + 1-5: Navigate to different sections
  if ((e.ctrlKey || e.metaKey) && e.key >= "1" && e.key <= "5") {
    e.preventDefault();
    const navItems = document.querySelectorAll(".nav-item");
    const index = parseInt(e.key) - 1;
    if (navItems[index]) {
      navItems[index].click();
    }
  }
});

// Utility function to format numbers
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
}

// Performance monitoring
let lastUpdate = Date.now();
function trackPerformance() {
  const now = Date.now();
  const timeSinceLastUpdate = now - lastUpdate;

  if (timeSinceLastUpdate > 100) {
    // Log if update takes more than 100ms
    console.log(`Performance: Update took ${timeSinceLastUpdate}ms`);
  }

  lastUpdate = now;
}

// Add performance tracking to updates
const originalUpdateCharts = updateCharts;
updateCharts = function () {
  trackPerformance();
  originalUpdateCharts();
};

// Initialize tooltips for better UX
function initializeTooltips() {
  const elements = document.querySelectorAll("[data-tooltip]");
  elements.forEach((element) => {
    element.addEventListener("mouseenter", function () {
      const tooltip = document.createElement("div");
      tooltip.className = "tooltip";
      tooltip.textContent = this.getAttribute("data-tooltip");
      document.body.appendChild(tooltip);

      const rect = this.getBoundingClientRect();
      tooltip.style.left =
        rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px";
      tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + "px";
    });

    element.addEventListener("mouseleave", function () {
      const tooltip = document.querySelector(".tooltip");
      if (tooltip) {
        tooltip.remove();
      }
    });
  });
}

// Initialize tooltips when DOM is loaded
document.addEventListener("DOMContentLoaded", initializeTooltips);

// Show different sections based on navigation
function showSection(sectionName) {
  const mainContent = document.querySelector(".main-content");

  switch (sectionName) {
    case "Dashboard":
      // Already showing dashboard - reload it
      location.reload();
      break;

    case "Detection History":
      mainContent.innerHTML = `
        <header class="top-header">
          <div class="header-title">
            <h1>🕵️ Detection History</h1>
            <p>Complete timeline of all detected threats and security events</p>
          </div>
          <div class="header-controls">
            <button class="btn-secondary" id="clearHistoryBtn">
              <span>🗑️</span> Clear History
            </button>
            <button class="btn-primary" id="exportDataBtn">
              <span>📥</span> Export Data
            </button>
          </div>
        </header>

        <!-- Quick Stats Overview -->
        <section class="history-stats-overview">
          <div class="history-stat-card">
            <div class="stat-icon-wrapper red">
              <span class="stat-icon">🚨</span>
            </div>
            <div class="stat-details">
              <h3 id="totalThreatsBlocked">0</h3>
              <p>Threats Blocked</p>
              <span class="stat-badge danger">High Priority</span>
            </div>
          </div>

          <div class="history-stat-card">
            <div class="stat-icon-wrapper orange">
              <span class="stat-icon">⚠️</span>
            </div>
            <div class="stat-details">
              <h3 id="suspiciousSites">0</h3>
              <p>Suspicious Sites</p>
              <span class="stat-badge warning">Medium Risk</span>
            </div>
          </div>

          <div class="history-stat-card">
            <div class="stat-icon-wrapper green">
              <span class="stat-icon">✅</span>
            </div>
            <div class="stat-details">
              <h3 id="safeSitesScanned">0</h3>
              <p>Safe Sites Verified</p>
              <span class="stat-badge success">Secure</span>
            </div>
          </div>

          <div class="history-stat-card">
            <div class="stat-icon-wrapper blue">
              <span class="stat-icon">📊</span>
            </div>
            <div class="stat-details">
              <h3 id="totalScans">0</h3>
              <p>Total Scans</p>
              <span class="stat-badge info">All Time</span>
            </div>
          </div>
        </section>

        <!-- Advanced Filters -->
        <section class="history-filters-advanced">
          <div class="filter-group">
            <div class="filter-item search-filter">
              <span class="filter-icon">🔍</span>
              <input type="text" id="historySearch" placeholder="Search by URL, domain, or IP address..." class="search-input-enhanced">
            </div>

            <div class="filter-item">
              <label>Type</label>
              <select id="filterType" class="filter-select-enhanced">
                <option value="all">All Types</option>
                <option value="phishing">🎣 Phishing</option>
                <option value="malware">🦠 Malware</option>
                <option value="suspicious">⚠️ Suspicious</option>
                <option value="safe">✅ Safe</option>
              </select>
            </div>

            <div class="filter-item">
              <label>Risk Level</label>
              <select id="filterRisk" class="filter-select-enhanced">
                <option value="all">All Levels</option>
                <option value="critical">🔴 Critical</option>
                <option value="high">🟠 High</option>
                <option value="medium">🟡 Medium</option>
                <option value="low">🟢 Low</option>
              </select>
            </div>

            <div class="filter-item">
              <label>Time Period</label>
              <select id="filterTime" class="filter-select-enhanced">
                <option value="all">All Time</option>
                <option value="today">Today</option>
                <option value="week">Last 7 Days</option>
                <option value="month">Last 30 Days</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>

            <button class="btn-filter-reset" onclick="resetFilters()">
              <span>🔄</span> Reset
            </button>
          </div>
        </section>

        <!-- Detection History Timeline -->
        <section class="history-timeline-section">
          <div class="timeline-header">
            <h3>📅 Recent Detections</h3>
            <div class="view-toggle">
              <button class="view-btn active" data-view="timeline">
                <span>📋</span> Timeline
              </button>
              <button class="view-btn" data-view="table">
                <span>📊</span> Table
              </button>
            </div>
          </div>

          <!-- Timeline View -->
          <div class="history-timeline" id="timelineView">
            ${generateHistoryTimeline()}
          </div>

          <!-- Table View (Hidden by default) -->
          <div class="history-table-view" id="tableView" style="display: none;">
            <div class="table-container">
              <table class="history-table-enhanced">
                <thead>
                  <tr>
                    <th><input type="checkbox" id="selectAll"></th>
                    <th>Status</th>
                    <th>Timestamp</th>
                    <th>URL / Domain</th>
                    <th>Threat Type</th>
                    <th>Risk Level</th>
                    <th>Action Taken</th>
                    <th>Details</th>
                  </tr>
                </thead>
                <tbody id="historyTableBody">
                  ${generateHistoryRows()}
                </tbody>
              </table>
            </div>

            <!-- Pagination -->
            <div class="pagination-controls">
              <button class="btn-page" onclick="previousPage()">← Previous</button>
              <span class="page-info">Page <strong>1</strong> of <strong>5</strong></span>
              <button class="btn-page" onclick="nextPage()">Next →</button>
            </div>
          </div>
        </section>

        <!-- Empty State (show when no history) -->
        <div class="empty-state" id="emptyState" style="display: none;">
          <div class="empty-icon">🔍</div>
          <h3>No Detection History Yet</h3>
          <p>Start browsing and PhishGuard AI will track all security events here</p>
          <button class="btn-primary" onclick="showSection('Dashboard')">
            <span>🏠</span> Go to Dashboard
          </button>
        </div>
      `;
      initializeHistoryPage();
      break;

    case "Analytics":
      mainContent.innerHTML = `
        <header class="top-header">
          <div class="header-title">
            <h1>Advanced Analytics</h1>
            <p>Comprehensive threat intelligence and performance metrics</p>
          </div>
          <div class="header-controls">
            <select id="analyticsTimeRange" class="form-control time-select">
              <option value="today">Today</option>
              <option value="7d" selected>Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
            </select>
            <button class="btn-primary" id="exportReportBtn">📊 Export Report</button>
          </div>
        </header>

        <!-- Key Metrics Grid -->
        <section class="hero-stats">
          <div class="stat-card analytics-stat">
            <div class="stat-content">
              <div class="stat-icon phishing">🎯</div>
              <div class="stat-info">
                <h3>97.3%</h3>
                <p>Detection Accuracy</p>
                <div class="stat-trend positive">
                  <span class="trend-icon">↗</span>
                  <span>+2.1% from last period</span>
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card analytics-stat">
            <div class="stat-content">
              <div class="stat-icon scanning">⚡</div>
              <div class="stat-info">
                <h3>0.23s</h3>
                <p>Avg Response Time</p>
                <div class="stat-trend positive">
                  <span class="trend-icon">↘</span>
                  <span>15% faster</span>
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card analytics-stat">
            <div class="stat-content">
              <div class="stat-icon detection">📉</div>
              <div class="stat-info">
                <h3>0.65%</h3>
                <p>False Positive Rate</p>
                <div class="stat-trend positive">
                  <span class="trend-icon">↘</span>
                  <span>Excellent performance</span>
                </div>
              </div>
            </div>
          </div>

          <div class="stat-card analytics-stat">
            <div class="stat-content">
              <div class="stat-icon users">💰</div>
              <div class="stat-info">
                <h3>$12.4K</h3>
                <p>Estimated Threat Value Blocked</p>
                <div class="stat-trend positive">
                  <span class="trend-icon">🛡️</span>
                  <span>Protection impact</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Charts Section -->
        <section class="analytics-section">
          <div class="chart-grid">
            <!-- Threat Trends Over Time -->
            <div class="chart-container large">
              <div class="chart-header">
                <h3>📈 Threat Detection Trends</h3>
                <p>Daily threat patterns and detection rates</p>
              </div>
              <div class="chart-wrapper" style="position: relative; height: 280px;">
                <canvas id="analyticsTrendChart"></canvas>
              </div>
            </div>

            <!-- Attack Vectors Breakdown -->
            <div class="chart-container">
              <div class="chart-header">
                <h3>🎯 Attack Vector Distribution</h3>
                <p>How threats reach your users</p>
              </div>
              <div class="vector-breakdown">
                <div class="vector-item">
                  <div class="vector-header">
                    <span class="vector-icon">📧</span>
                    <span class="vector-name">Email Links</span>
                    <span class="vector-percent">45%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 45%; background: #ff4757"></div>
                  </div>
                  <span class="vector-count">1,247 threats</span>
                </div>

                <div class="vector-item">
                  <div class="vector-header">
                    <span class="vector-icon">📱</span>
                    <span class="vector-name">Social Media</span>
                    <span class="vector-percent">32%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 32%; background: #ffa502"></div>
                  </div>
                  <span class="vector-count">887 threats</span>
                </div>

                <div class="vector-item">
                  <div class="vector-header">
                    <span class="vector-icon">🔗</span>
                    <span class="vector-name">Direct URLs</span>
                    <span class="vector-percent">18%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 18%; background: #1FB8CD"></div>
                  </div>
                  <span class="vector-count">499 threats</span>
                </div>

                <div class="vector-item">
                  <div class="vector-header">
                    <span class="vector-icon">📢</span>
                    <span class="vector-name">Ads/Pop-ups</span>
                    <span class="vector-percent">5%</span>
                  </div>
                  <div class="progress-bar">
                    <div class="progress-fill" style="width: 5%; background: #5D878F"></div>
                  </div>
                  <span class="vector-count">138 threats</span>
                </div>
              </div>
            </div>

            <!-- Geographic Distribution -->
            <div class="chart-container">
              <div class="chart-header">
                <h3>🌍 Top Threat Origins</h3>
                <p>Geographic source of attacks</p>
              </div>
              <div class="chart-wrapper" style="position: relative; height: 250px;">
                <canvas id="geoChart"></canvas>
              </div>
            </div>

            <!-- Peak Activity Times -->
            <div class="chart-container">
              <div class="chart-header">
                <h3>⏰ Peak Threat Times</h3>
                <p>When attacks are most frequent</p>
              </div>
              <div class="time-heatmap">
                <div class="heatmap-item high">
                  <span class="time-label">12-2 PM</span>
                  <span class="threat-count">High: 234 threats</span>
                </div>
                <div class="heatmap-item medium">
                  <span class="time-label">9-11 AM</span>
                  <span class="threat-count">Medium: 156 threats</span>
                </div>
                <div class="heatmap-item medium">
                  <span class="time-label">3-5 PM</span>
                  <span class="threat-count">Medium: 143 threats</span>
                </div>
                <div class="heatmap-item low">
                  <span class="time-label">3-5 AM</span>
                  <span class="threat-count">Low: 34 threats</span>
                </div>
              </div>
            </div>

            <!-- User Risk Analysis -->
            <div class="chart-container large">
              <div class="chart-header">
                <h3>👥 User Risk Distribution</h3>
                <p>Risk levels across your organization</p>
              </div>
              <div class="risk-analysis">
                <div class="risk-segment-large low-risk">
                  <h4>60%</h4>
                  <p>Low Risk Users</p>
                  <span>726 users</span>
                </div>
                <div class="risk-segment-large medium-risk">
                  <h4>30%</h4>
                  <p>Medium Risk Users</p>
                  <span>363 users</span>
                </div>
                <div class="risk-segment-large high-risk">
                  <h4>10%</h4>
                  <p>High Risk Users</p>
                  <span>121 users</span>
                </div>
              </div>
            </div>

            <!-- AI Model Performance -->
            <div class="chart-container">
              <div class="chart-header">
                <h3>🤖 AI Model Performance</h3>
                <p>Machine learning metrics</p>
              </div>
              <div class="model-metrics">
                <div class="metric-row">
                  <span class="metric-label">Precision</span>
                  <div class="metric-bar-container">
                    <div class="metric-bar" style="width: 98.7%"></div>
                  </div>
                  <span class="metric-value">98.7%</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">Recall</span>
                  <div class="metric-bar-container">
                    <div class="metric-bar" style="width: 96.2%"></div>
                  </div>
                  <span class="metric-value">96.2%</span>
                </div>
                <div class="metric-row">
                  <span class="metric-label">F1-Score</span>
                  <div class="metric-bar-container">
                    <div class="metric-bar" style="width: 97.4%"></div>
                  </div>
                  <span class="metric-value">97.4%</span>
                </div>
                <div class="model-info">
                  <p><strong>Last Model Update:</strong> 2 hours ago</p>
                  <p><strong>Training Data:</strong> 2.3M samples</p>
                  <p><strong>Next Update:</strong> In 4 hours</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      `;
      initializeAnalyticsPage();
      break;

    case "Settings":
      mainContent.innerHTML = `
        <header class="top-header">
          <div class="header-title">
            <h1>Settings & Configuration</h1>
            <p>Customize your security preferences and system behavior</p>
          </div>
          <div class="header-controls">
            <div class="status-indicator">
              <div class="status-light active"></div>
              <span>Protection Active</span>
            </div>
          </div>
        </header>

        <!-- Settings Tabs -->
        <div class="settings-tabs">
          <button class="tab-button active" data-tab="protection">🛡️ Protection</button>
          <button class="tab-button" data-tab="notifications">🔔 Notifications</button>
          <button class="tab-button" data-tab="privacy">🔒 Privacy</button>
          <button class="tab-button" data-tab="advanced">⚙️ Advanced</button>
        </div>

        <section class="settings-section">
          <!-- Protection Tab -->
          <div class="tab-content active" data-tab="protection">
            <div class="settings-grid-enhanced">
              <div class="settings-card-enhanced">
                <h3>🛡️ Core Protection Features</h3>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Real-time URL Scanning</label>
                      <p>Scan all URLs before page load to block threats instantly</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked id="realtimeProtection">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                  <div class="setting-status success">Currently protecting all browsing activity</div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>AI-Powered Detection</label>
                      <p>Use machine learning to identify zero-day phishing attempts</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked id="aiDetection">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                  <div class="setting-status success">AI model accuracy: 97.3%</div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Automatic Threat Blocking</label>
                      <p>Block access to confirmed malicious websites automatically</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked id="autoBlock">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                  <div class="setting-status success">2,847 threats blocked this week</div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Download Protection</label>
                      <p>Scan downloaded files for malware before opening</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked id="downloadProtection">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>
              </div>

              <div class="settings-card-enhanced">
                <h3>⚙️ Detection Sensitivity</h3>

                <div class="sensitivity-slider-container">
                  <input type="range" min="1" max="3" value="2" class="sensitivity-slider" id="sensitivitySlider">
                  <div class="sensitivity-labels">
                    <span>Conservative</span>
                    <span>Balanced</span>
                    <span>Aggressive</span>
                  </div>
                </div>

                <div class="sensitivity-description" id="sensitivityDesc">
                  <strong>Balanced Mode</strong>
                  <p>Optimal balance between security and usability. May occasionally flag suspicious but legitimate sites.</p>
                  <div class="sensitivity-stats">
                    <div class="stat">
                      <span class="stat-label">Expected Accuracy</span>
                      <span class="stat-value">97%</span>
                    </div>
                    <div class="stat">
                      <span class="stat-label">False Positives</span>
                      <span class="stat-value">~2%</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="settings-card-enhanced">
                <h3>🌐 Protected Domains</h3>
                <p>Manage trusted and blocked domains</p>

                <div class="domain-list">
                  <h4>Whitelist (Trusted Sites)</h4>
                  <div class="domain-input-group">
                    <input type="text" placeholder="example.com" class="form-control" id="whitelistInput">
                    <button class="btn-primary" id="addWhitelistBtn">+ Add</button>
                  </div>
                  <div class="domain-chips" id="whitelistDomains">
                    <div class="chip">google.com <span class="chip-remove">×</span></div>
                    <div class="chip">github.com <span class="chip-remove">×</span></div>
                    <div class="chip">stackoverflow.com <span class="chip-remove">×</span></div>
                  </div>
                </div>

                <div class="domain-list">
                  <h4>Blacklist (Always Block)</h4>
                  <div class="domain-input-group">
                    <input type="text" placeholder="suspicious-site.com" class="form-control" id="blacklistInput">
                    <button class="btn-primary" id="addBlacklistBtn">+ Add</button>
                  </div>
                  <div class="domain-chips" id="blacklistDomains">
                    <div class="chip red">phishing-test.com <span class="chip-remove">×</span></div>
                    <div class="chip red">malware-host.net <span class="chip-remove">×</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Notifications Tab -->
          <div class="tab-content" data-tab="notifications">
            <div class="settings-grid-enhanced">
              <div class="settings-card-enhanced">
                <h3>🔔 Alert Preferences</h3>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Desktop Notifications</label>
                      <p>Show system notifications when threats are detected</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked>
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Sound Alerts</label>
                      <p>Play audio alert for high-risk threats</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Email Notifications</label>
                      <p>Receive email alerts for critical threats</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                  <div class="setting-sub-options">
                    <input type="email" placeholder="your-email@company.com" class="form-control" value="admin@company.com">
                  </div>
                </div>
              </div>

              <div class="settings-card-enhanced">
                <h3>📊 Report Frequency</h3>

                <div class="report-options">
                  <label class="radio-option">
                    <input type="radio" name="reportFreq" value="none">
                    <span>No reports</span>
                  </label>
                  <label class="radio-option">
                    <input type="radio" name="reportFreq" value="daily" checked>
                    <span>Daily summary</span>
                  </label>
                  <label class="radio-option">
                    <input type="radio" name="reportFreq" value="weekly">
                    <span>Weekly digest</span>
                  </label>
                  <label class="radio-option">
                    <input type="radio" name="reportFreq" value="monthly">
                    <span>Monthly report</span>
                  </label>
                </div>

                <div class="report-preview">
                  <h4>📧 Next Report: Tomorrow at 9:00 AM</h4>
                  <p>Includes: Threat summary, top risks, recommendations</p>
                  <button class="btn-secondary">Send Test Report</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Privacy Tab -->
          <div class="tab-content" data-tab="privacy">
            <div class="settings-grid-enhanced">
              <div class="settings-card-enhanced">
                <h3>🔒 Data Privacy</h3>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Anonymous Usage Statistics</label>
                      <p>Help improve PhishGuard by sharing anonymous usage data</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox" checked>
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div class="setting-item-enhanced">
                  <div class="setting-header">
                    <div class="setting-info">
                      <label>Cloud Sync</label>
                      <p>Sync settings and history across devices</p>
                    </div>
                    <label class="toggle-switch">
                      <input type="checkbox">
                      <span class="toggle-slider"></span>
                    </label>
                  </div>
                </div>

                <div class="setting-item-enhanced">
                  <label>Data Retention Period</label>
                  <select class="form-control">
                    <option>7 days</option>
                    <option selected>30 days</option>
                    <option>90 days</option>
                    <option>1 year</option>
                  </select>
                  <p class="setting-help">Historical data will be automatically deleted after this period</p>
                </div>

                <div class="danger-zone">
                  <h4>⚠️ Danger Zone</h4>
                  <button class="btn-danger">Clear All History</button>
                  <button class="btn-danger">Delete All Data</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Advanced Tab -->
          <div class="tab-content" data-tab="advanced">
            <div class="settings-grid-enhanced">
              <div class="settings-card-enhanced">
                <h3>⚙️ Advanced Configuration</h3>

                <div class="setting-item-enhanced">
                  <label>API Endpoint</label>
                  <input type="text" class="form-control" value="https://api.phishguard.ai/v1" placeholder="API URL">
                  <p class="setting-help">Custom backend endpoint for enterprise deployments</p>
                </div>

                <div class="setting-item-enhanced">
                  <label>Cache Duration (seconds)</label>
                  <input type="number" class="form-control" value="3600" min="60" max="86400">
                  <p class="setting-help">How long to cache URL scanning results</p>
                </div>

                <div class="setting-item-enhanced">
                  <label>Max Concurrent Scans</label>
                  <input type="number" class="form-control" value="10" min="1" max="50">
                  <p class="setting-help">Number of simultaneous URL scans allowed</p>
                </div>

                <div class="setting-item-enhanced">
                  <label>Debug Mode</label>
                  <label class="toggle-switch">
                    <input type="checkbox">
                    <span class="toggle-slider"></span>
                  </label>
                  <p class="setting-help">Enable verbose logging for troubleshooting</p>
                </div>

                <button class="btn-secondary">View Logs</button>
                <button class="btn-secondary">Export Configuration</button>
              </div>
            </div>
          </div>

          <!-- Save Bar -->
          <div class="settings-save-bar">
            <div class="save-message">
              <span id="saveStatus">All changes saved automatically</span>
            </div>
            <div class="save-actions">
              <button class="btn-secondary" id="resetSettingsBtn">Reset All</button>
              <button class="btn-primary" id="saveSettingsBtn">💾 Save Changes</button>
            </div>
          </div>
        </section>
      `;
      initializeSettingsPage();
      break;

    case "Help":
      mainContent.innerHTML = `
        <section class="help-section-enhanced">
          <!-- FAQ Section -->
          <div class="faq-section-enhanced">
            <h3>🤔 Frequently Asked Questions</h3>
            <p class="faq-subtitle">Click any question to expand the answer</p>

            <div class="faq-categories">
              <button class="faq-category-btn active" data-category="all">All</button>
              <button class="faq-category-btn" data-category="detection">Detection</button>
              <button class="faq-category-btn" data-category="privacy">Privacy</button>
              <button class="faq-category-btn" data-category="technical">Technical</button>
            </div>

            <div class="faq-list">
              <div class="faq-item-enhanced" data-category="detection">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>How does PhishGuard AI detect phishing sites?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p>PhishGuard AI uses a multi-layered approach to detect phishing threats:</p>
                  <ul>
                    <li><strong>Machine Learning Models:</strong> Advanced neural networks trained on millions of phishing samples (97.3% accuracy)</li>
                    <li><strong>URL Analysis:</strong> Examines domain patterns, suspicious characters, and known malicious indicators</li>
                    <li><strong>Content Inspection:</strong> Analyzes page structure, forms, and embedded scripts</li>
                    <li><strong>SSL Certificate Verification:</strong> Checks for invalid or suspicious certificates</li>
                    <li><strong>Real-time Threat Intelligence:</strong> Leverages global threat database updated every minute</li>
                  </ul>
                  <p>All analysis happens in milliseconds without impacting your browsing experience.</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="detection">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>What happens when a threat is detected?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p>When PhishGuard AI detects a threat, the following occurs:</p>
                  <ol>
                    <li>The page load is immediately blocked before any malicious code runs</li>
                    <li>A warning page is displayed with threat details</li>
                    <li>You can choose to go back safely or proceed at your own risk</li>
                    <li>The threat is logged in your Detection History</li>
                    <li>A notification is sent (if enabled in settings)</li>
                  </ol>
                  <p><strong>Note:</strong> You can always override the block if you believe it's a false positive.</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="detection">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>What should I do if a legitimate site is blocked?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p>If you encounter a false positive:</p>
                  <ol>
                    <li>Click "Report False Positive" on the warning page</li>
                    <li>Add the site to your whitelist in Settings → Protection</li>
                    <li>Our team reviews all reports within 24 hours</li>
                    <li>The site will be unblocked for all users if confirmed safe</li>
                  </ol>
                  <p><strong>Tip:</strong> Check if the URL is spelled correctly - attackers often use look-alike domains!</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="privacy">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>Does PhishGuard AI protect my privacy?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p><strong>Absolutely! Privacy is our top priority:</strong></p>
                  <ul>
                    <li>✅ Most URL scanning happens locally on your device</li>
                    <li>✅ Only anonymized URL hashes are sent to our servers (not full URLs)</li>
                    <li>✅ We never store or sell your browsing history</li>
                    <li>✅ All data is encrypted in transit using TLS 1.3</li>
                    <li>✅ You can enable "Privacy Mode" for 100% local processing</li>
                    <li>✅ GDPR & CCPA compliant</li>
                  </ul>
                  <p>Read our full <a href="#" class="help-link">Privacy Policy</a> for more details.</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="privacy">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>Can I use PhishGuard AI without creating an account?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p>Yes! PhishGuard AI works perfectly without an account. However, creating a free account provides benefits:</p>
                  <ul>
                    <li>Sync settings across devices</li>
                    <li>Access to detailed analytics and reports</li>
                    <li>Priority customer support</li>
                    <li>Custom whitelist/blacklist sync</li>
                  </ul>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="technical">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>How often is the threat database updated?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p><strong>Real-time updates:</strong></p>
                  <ul>
                    <li>Threat database: Updated every 60 seconds</li>
                    <li>AI model: Retrained every 6 hours</li>
                    <li>Extension updates: Automatic via Chrome Web Store</li>
                  </ul>
                  <p>You don't need to do anything - updates happen automatically in the background.</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="technical">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>Does PhishGuard AI slow down my browsing?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p><strong>No!</strong> PhishGuard AI is optimized for performance:</p>
                  <ul>
                    <li>Average scan time: 0.23 seconds</li>
                    <li>Cached results for frequently visited sites</li>
                    <li>Parallel processing doesn't block page loads</li>
                    <li>Minimal memory footprint (~50MB)</li>
                  </ul>
                  <p>Most users report no noticeable impact on browsing speed.</p>
                </div>
              </div>

              <div class="faq-item-enhanced" data-category="technical">
                <div class="faq-question" onclick="toggleFAQ(this)">
                  <h4>Which browsers are supported?</h4>
                  <span class="faq-toggle">+</span>
                </div>
                <div class="faq-answer">
                  <p>PhishGuard AI is available for:</p>
                  <ul>
                    <li>✅ Google Chrome (v90+)</li>
                    <li>✅ Microsoft Edge (v90+)</li>
                    <li>✅ Brave Browser (v1.20+)</li>
                    <li>✅ Opera (v76+)</li>
                    <li>🔜 Firefox (Coming soon)</li>
                    <li>🔜 Safari (In development)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Contact Support Section -->
          <div class="support-section">
            <h3>💬 Need More Help?</h3>
            <div class="support-grid">
              <div class="support-card">
                <div class="support-icon">📧</div>
                <h4>Email Support</h4>
                <p>Get help from our expert team</p>
                <p><strong>support@phishguard.ai</strong></p>
                <p class="support-response-time">⏱️ Response time: 2-4 hours</p>
                <button class="btn-primary">Send Email</button>
              </div>

              <div class="support-card">
                <div class="support-icon">💬</div>
                <h4>Live Chat</h4>
                <p>Chat with support agent</p>
                <p><strong>Available 24/7</strong></p>
                <p class="support-response-time">⏱️ Avg wait time: 2 minutes</p>
                <button class="btn-primary">Start Chat</button>
              </div>

              <div class="support-card">
                <div class="support-icon">🌐</div>
                <h4>Community Forum</h4>
                <p>Ask questions, share tips</p>
                <p><strong>12,000+ members</strong></p>
                <p class="support-response-time">👥 Community driven</p>
                <button class="btn-primary">Join Forum</button>
              </div>
            </div>
          </div>

          <!-- System Status -->
          <div class="system-status-help">
            <h4>System Status: <span class="status-badge-success">All Systems Operational</span></h4>
            <div class="status-details">
              <div class="status-item">✅ API Status: Online</div>
              <div class="status-item">✅ AI Model: Active</div>
              <div class="status-item">✅ Database: Operational</div>
              <div class="status-item">✅ Threat Updates: Real-time</div>
            </div>
          </div>
        </section>
      `;
      initializeHelpPage();
      break;
  }
}

// Generate history table rows
function generateHistoryTimeline() {
  const historyData = [
    {
      timestamp: "2025-10-09 16:32:15",
      type: "Phishing",
      risk: "Critical",
      url: "https://secure-paypal-verify.tk/login",
      domain: "secure-paypal-verify.tk",
      action: "Blocked",
      description: "Credential harvesting attempt detected",
      ip: "185.220.101.47",
      icon: "🎣",
    },
    {
      timestamp: "2025-10-09 15:45:12",
      type: "Malware",
      risk: "High",
      url: "https://free-software-download.ru/installer.exe",
      domain: "free-software-download.ru",
      action: "Blocked",
      description: "Trojan malware distribution site",
      ip: "91.203.5.165",
      icon: "🦠",
    },
    {
      timestamp: "2025-10-09 15:18:22",
      type: "Suspicious",
      risk: "Medium",
      url: "https://bit.ly/3xK9mNp",
      domain: "bit.ly",
      action: "Warned",
      description: "Suspicious URL shortener redirect",
      ip: "13.35.120.45",
      icon: "⚠️",
    },
    {
      timestamp: "2025-10-09 14:55:10",
      type: "Safe",
      risk: "Low",
      url: "https://github.com/dashboard",
      domain: "github.com",
      action: "Allowed",
      description: "Verified legitimate site",
      ip: "140.82.121.4",
      icon: "✅",
    },
    {
      timestamp: "2025-10-09 14:32:45",
      type: "Phishing",
      risk: "High",
      url: "https://microsoft-support-center.com/verify",
      domain: "microsoft-support-center.com",
      action: "Blocked",
      description: "Tech support scam detected",
      ip: "104.21.45.89",
      icon: "🎣",
    },
    {
      timestamp: "2025-10-09 13:28:33",
      type: "Safe",
      risk: "Low",
      url: "https://stackoverflow.com/questions",
      domain: "stackoverflow.com",
      action: "Allowed",
      description: "Verified legitimate site",
      ip: "151.101.1.69",
      icon: "✅",
    },
    {
      timestamp: "2025-10-09 12:15:20",
      type: "Suspicious",
      risk: "Medium",
      url: "https://urgentupdate.xyz/chrome-update",
      domain: "urgentupdate.xyz",
      action: "Blocked",
      description: "Fake software update page",
      ip: "172.67.178.123",
      icon: "⚠️",
    },
    {
      timestamp: "2025-10-09 11:42:18",
      type: "Safe",
      risk: "Low",
      url: "https://amazon.com/shopping-cart",
      domain: "amazon.com",
      action: "Allowed",
      description: "Verified legitimate site",
      ip: "52.94.236.248",
      icon: "✅",
    },
  ];

  return historyData
    .map((item) => {
      const riskClass = item.risk.toLowerCase();
      const typeClass = item.type.toLowerCase();

      return `
      <div class="timeline-item ${typeClass}" data-risk="${riskClass}">
        <div class="timeline-marker ${riskClass}">
          <span class="timeline-icon">${item.icon}</span>
        </div>
        <div class="timeline-content">
          <div class="timeline-header-content">
            <div class="timeline-title">
              <span class="threat-type-badge ${typeClass}">${item.type}</span>
              <span class="risk-badge ${riskClass}">${item.risk} Risk</span>
              <span class="action-badge ${item.action.toLowerCase()}">${
        item.action
      }</span>
            </div>
            <div class="timeline-time">
              <span class="time-icon">🕐</span>
              ${item.timestamp}
            </div>
          </div>

          <div class="timeline-body">
            <div class="url-display">
              <span class="url-icon">🔗</span>
              <code class="url-text">${item.url}</code>
              <button class="btn-copy" onclick="copyToClipboard('${
                item.url
              }')" title="Copy URL">
                📋
              </button>
            </div>

            <div class="threat-details">
              <div class="detail-row">
                <span class="detail-label">Domain:</span>
                <span class="detail-value">${item.domain}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">IP Address:</span>
                <span class="detail-value"><code>${item.ip}</code></span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Description:</span>
                <span class="detail-value">${item.description}</span>
              </div>
            </div>

            <div class="timeline-actions">
              <button class="btn-action-small" onclick="viewThreatDetails('${
                item.url
              }')">
                <span>🔍</span> View Details
              </button>
              <button class="btn-action-small" onclick="reportFalsePositive('${
                item.url
              }')">
                <span>⚠️</span> Report
              </button>
              <button class="btn-action-small" onclick="whitelistDomain('${
                item.domain
              }')">
                <span>✅</span> Whitelist
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
    })
    .join("");
}

function generateHistoryRows() {
  const tableHistory = [
    {
      timestamp: "2025-10-09 16:32:15",
      type: "Phishing",
      risk: "Critical",
      url: "https://secure-paypal-verify.tk/login",
      action: "Blocked",
      icon: "🚫",
    },
    {
      timestamp: "2025-10-09 15:45:12",
      type: "Malware",
      risk: "High",
      url: "https://free-software-download.ru/installer.exe",
      action: "Blocked",
      icon: "🚫",
    },
    {
      timestamp: "2025-10-09 15:18:22",
      type: "Suspicious",
      risk: "Medium",
      url: "https://bit.ly/3xK9mNp",
      action: "Warned",
      icon: "⚠️",
    },
    {
      timestamp: "2025-10-09 14:55:10",
      type: "Safe",
      risk: "Low",
      url: "https://github.com/dashboard",
      action: "Allowed",
      icon: "✅",
    },
    {
      timestamp: "2025-10-09 14:32:45",
      type: "Phishing",
      risk: "High",
      url: "https://microsoft-support-center.com/verify",
      action: "Blocked",
      icon: "🚫",
    },
    {
      timestamp: "2025-10-09 13:28:33",
      type: "Safe",
      risk: "Low",
      url: "https://stackoverflow.com/questions",
      action: "Allowed",
      icon: "✅",
    },
    {
      timestamp: "2025-10-09 12:15:20",
      type: "Suspicious",
      risk: "Medium",
      url: "https://urgentupdate.xyz/chrome-update",
      action: "Blocked",
      icon: "🚫",
    },
    {
      timestamp: "2025-10-09 11:42:18",
      type: "Safe",
      risk: "Low",
      url: "https://amazon.com/shopping-cart",
      action: "Allowed",
      icon: "✅",
    },
    ...dashboardData.recentActivity.map((item) => ({
      ...item,
      action: item.type === "Safe" ? "Allowed" : "Blocked",
      icon: item.type === "Safe" ? "✅" : "🚫",
    })),
  ];

  return tableHistory
    .map((item) => {
      const riskClass = item.risk.toLowerCase();
      const typeClass = item.type.toLowerCase();
      const statusIcon = item.icon;

      return `
    <tr class="table-row-${riskClass}" data-risk="${riskClass}" data-type="${typeClass}">
      <td><input type="checkbox" class="row-checkbox"></td>
      <td><span class="status-icon">${statusIcon}</span></td>
      <td><span class="timestamp">${item.timestamp}</span></td>
      <td>
        <div class="url-cell">
          <code class="url-code">${item.url}</code>
          <button class="btn-copy-small" onclick="copyToClipboard('${
            item.url
          }')" title="Copy">📋</button>
        </div>
      </td>
      <td>
        <span class="threat-badge ${typeClass}">
          ${
            item.type === "Phishing"
              ? "🎣"
              : item.type === "Malware"
              ? "🦠"
              : item.type === "Suspicious"
              ? "⚠️"
              : "✅"
          } ${item.type}
        </span>
      </td>
      <td>
        <span class="risk-level-badge ${riskClass}">
          ${
            item.risk === "Critical"
              ? "🔴"
              : item.risk === "High"
              ? "🟠"
              : item.risk === "Medium"
              ? "🟡"
              : "🟢"
          } ${item.risk}
        </span>
      </td>
      <td>
        <span class="action-badge-table ${item.action.toLowerCase()}">
          ${item.action}
        </span>
      </td>
      <td>
        <div class="action-buttons">
          <button class="btn-table-action" onclick="viewDetails('${
            item.url
          }')" title="View Details">
            🔍
          </button>
          <button class="btn-table-action" onclick="showMoreInfo('${
            item.url
          }')" title="More Info">
            ℹ️
          </button>
        </div>
      </td>
    </tr>
  `;
    })
    .join("");
}

// Initialize pages
function initializeHistoryPage() {
  console.log("🔄 Initializing History Page...");

  // Update stats
  updateHistoryStats();

  // Setup export and clear buttons with event listeners (with small delay to ensure DOM is ready)
  setTimeout(() => {
    setupExportDataButton();
    setupClearHistoryButton();
  }, 100);

  // View toggle functionality
  const viewButtons = document.querySelectorAll(".view-btn");
  viewButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      viewButtons.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");

      const view = this.dataset.view;
      const timelineView = document.getElementById("timelineView");
      const tableView = document.getElementById("tableView");

      if (view === "timeline") {
        timelineView.style.display = "block";
        tableView.style.display = "none";
      } else {
        timelineView.style.display = "none";
        tableView.style.display = "block";
      }
    });
  });

  // Search functionality
  const searchInput = document.getElementById("historySearch");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      filterHistory();
    });
  }

  // Filter dropdowns
  const filterType = document.getElementById("filterType");
  const filterRisk = document.getElementById("filterRisk");
  const filterTime = document.getElementById("filterTime");

  [filterType, filterRisk, filterTime].forEach((filter) => {
    if (filter) {
      filter.addEventListener("change", filterHistory);
    }
  });

  // Select all checkbox
  const selectAll = document.getElementById("selectAll");
  if (selectAll) {
    selectAll.addEventListener("change", function () {
      const checkboxes = document.querySelectorAll(".row-checkbox");
      checkboxes.forEach((cb) => (cb.checked = this.checked));
    });
  }
}

function updateHistoryStats() {
  // Count threats by type
  let threatsBlocked = 8;
  let suspiciousSites = 3;
  let safeSites = 12;
  let totalScans = 23;

  const stats = {
    totalThreatsBlocked: threatsBlocked,
    suspiciousSites: suspiciousSites,
    safeSitesScanned: safeSites,
    totalScans: totalScans,
  };

  // Update DOM
  const elements = {
    totalThreatsBlocked: document.getElementById("totalThreatsBlocked"),
    suspiciousSites: document.getElementById("suspiciousSites"),
    safeSitesScanned: document.getElementById("safeSitesScanned"),
    totalScans: document.getElementById("totalScans"),
  };

  Object.keys(elements).forEach((key) => {
    if (elements[key]) {
      elements[key].textContent = stats[key];
    }
  });
}

function filterHistory() {
  const searchTerm =
    document.getElementById("historySearch")?.value.toLowerCase() || "";
  const typeFilter = document.getElementById("filterType")?.value || "all";
  const riskFilter = document.getElementById("filterRisk")?.value || "all";

  console.log("Filtering:", { searchTerm, typeFilter, riskFilter });

  // Filter timeline items
  const timelineItems = document.querySelectorAll(".timeline-item");
  let visibleCount = 0;

  timelineItems.forEach((item) => {
    const text = item.textContent.toLowerCase();
    const itemRisk = item.dataset.risk;

    // Check if item matches all filters
    const matchesSearch = searchTerm === "" || text.includes(searchTerm);
    const matchesType =
      typeFilter === "all" || item.classList.contains(typeFilter);
    const matchesRisk = riskFilter === "all" || itemRisk === riskFilter;

    const shouldShow = matchesSearch && matchesType && matchesRisk;

    item.style.display = shouldShow ? "flex" : "none";
    if (shouldShow) visibleCount++;
  });

  console.log(
    `Showing ${visibleCount} of ${timelineItems.length} timeline items`
  );

  // Filter table rows
  const tableRows = document.querySelectorAll("#historyTableBody tr");
  let visibleTableRows = 0;

  tableRows.forEach((row) => {
    const text = row.textContent.toLowerCase();
    const rowRisk = row.dataset.risk;
    const rowType = row.dataset.type;

    const matchesSearch = searchTerm === "" || text.includes(searchTerm);
    const matchesType = typeFilter === "all" || rowType === typeFilter;
    const matchesRisk = riskFilter === "all" || rowRisk === riskFilter;

    const shouldShow = matchesSearch && matchesType && matchesRisk;

    row.style.display = shouldShow ? "" : "none";
    if (shouldShow) visibleTableRows++;
  });

  console.log(`Showing ${visibleTableRows} of ${tableRows.length} table rows`);
}

// Notification System
function showNotification(message, type = "info") {
  console.log(`Notification [${type}]: ${message}`);

  // Create notification element
  const notification = document.createElement("div");
  notification.className = `notification notification-${type}`;
  notification.innerHTML = `
    <span class="notification-icon">
      ${
        type === "success"
          ? "✅"
          : type === "error"
          ? "❌"
          : type === "warning"
          ? "⚠️"
          : "ℹ️"
      }
    </span>
    <span class="notification-message">${message}</span>
  `;

  // Add to body
  document.body.appendChild(notification);

  // Show notification with animation
  setTimeout(() => {
    notification.classList.add("show");
  }, 10);

  // Remove after 3 seconds
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

function resetFilters() {
  document.getElementById("historySearch").value = "";
  document.getElementById("filterType").value = "all";
  document.getElementById("filterRisk").value = "all";
  document.getElementById("filterTime").value = "all";
  filterHistory();
}

function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    showNotification("URL copied to clipboard!", "success");
  });
}

function viewThreatDetails(url) {
  alert("Viewing details for: " + url);
}

function reportFalsePositive(url) {
  if (confirm("Report this detection as a false positive?\n\n" + url)) {
    showNotification("Report submitted successfully", "success");
  }
}

function whitelistDomain(domain) {
  if (confirm("Add this domain to your whitelist?\n\n" + domain)) {
    showNotification("Domain added to whitelist", "success");
  }
}

function setupClearHistoryButton() {
  const clearBtn = document.getElementById("clearHistoryBtn");
  if (!clearBtn) {
    console.warn("⚠️ Clear History button not found");
    return;
  }

  console.log("✅ Clear History button found, attaching event listener");

  clearBtn.addEventListener("click", function () {
    console.log("🗑️ Clear History button clicked");

    if (
      confirm(
        "Are you sure you want to clear all detection history?\n\nThis action cannot be undone."
      )
    ) {
      console.log("✅ User confirmed - clearing history");

      // Get the table body
      const tableBody = document.getElementById("historyTableBody");
      if (tableBody) {
        // Clear all rows
        tableBody.innerHTML = "";
        console.log("✅ History table cleared");

        // Show empty state
        const emptyState = document.getElementById("emptyState");
        const historySection = document.querySelector(".history-section");

        if (emptyState && historySection) {
          historySection.style.display = "none";
          emptyState.style.display = "block";
          console.log("✅ Empty state displayed");
        }

        // Show success notification
        showNotification("History cleared successfully", "success");
      } else {
        console.error("❌ History table body not found");
      }
    } else {
      console.log("❌ User cancelled clear history");
    }
  });
}

// COMPLETE REWRITE: Export Data Functionality
function setupExportDataButton() {
  const exportBtn = document.getElementById("exportDataBtn");
  if (!exportBtn) {
    console.warn("Export button not found");
    return;
  }

  console.log("✅ Export Data button found, attaching event listener");

  exportBtn.addEventListener("click", function () {
    console.log("� Export Data button clicked!");

    try {
      // Detection history data
      const detectionData = {
        exportDate: new Date().toISOString(),
        totalThreats: 8,
        detections: [
          {
            id: 1,
            timestamp: "2025-10-09 16:23:45",
            threatType: "Phishing",
            riskLevel: "Critical",
            url: "https://secure-banking-verify.com/login",
            action: "Blocked",
            description: "Suspicious domain mimicking legitimate banking site",
          },
          {
            id: 2,
            timestamp: "2025-10-09 15:45:12",
            threatType: "Malware",
            riskLevel: "High",
            url: "https://free-software-download.ru/installer.exe",
            action: "Blocked",
            description: "Executable file from untrusted source",
          },
          {
            id: 3,
            timestamp: "2025-10-09 15:18:22",
            threatType: "Suspicious",
            riskLevel: "Medium",
            url: "https://bit.ly/3xK9mNp",
            action: "Warned",
            description: "URL shortener with unknown destination",
          },
          {
            id: 4,
            timestamp: "2025-10-09 14:55:10",
            threatType: "Safe",
            riskLevel: "Low",
            url: "https://github.com/dashboard",
            action: "Allowed",
            description: "Verified legitimate site",
          },
          {
            id: 5,
            timestamp: "2025-10-09 14:32:45",
            threatType: "Phishing",
            riskLevel: "High",
            url: "https://microsoft-support-center.com/verify",
            action: "Blocked",
            description: "Fake Microsoft support site",
          },
          {
            id: 6,
            timestamp: "2025-10-09 13:28:33",
            threatType: "Safe",
            riskLevel: "Low",
            url: "https://stackoverflow.com/questions",
            action: "Allowed",
            description: "Verified legitimate site",
          },
          {
            id: 7,
            timestamp: "2025-10-09 12:15:20",
            threatType: "Suspicious",
            riskLevel: "Medium",
            url: "https://urgentupdate.xyz/chrome-update",
            action: "Blocked",
            description: "Suspicious domain requesting software update",
          },
          {
            id: 8,
            timestamp: "2025-10-09 11:42:18",
            threatType: "Safe",
            riskLevel: "Low",
            url: "https://amazon.com/shopping-cart",
            action: "Allowed",
            description: "Verified legitimate site",
          },
        ],
      };

      // Convert to JSON string
      const jsonString = JSON.stringify(detectionData, null, 2);
      console.log("📄 JSON data created, size:", jsonString.length, "bytes");

      // Create blob
      const blob = new Blob([jsonString], { type: "application/json" });
      console.log("📦 Blob created");

      // Create object URL
      const url = URL.createObjectURL(blob);
      console.log("🔗 Object URL created:", url);

      // Create filename
      const timestamp = new Date()
        .toISOString()
        .replace(/[:.]/g, "-")
        .split("T")[0];
      const filename = `PhishGuard_DetectionHistory_${timestamp}.json`;
      console.log("📝 Filename:", filename);

      // Create temporary link and trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.style.display = "none";
      document.body.appendChild(a);

      console.log("🖱️ Triggering download...");
      a.click();

      // Cleanup
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        console.log("🧹 Cleanup complete");
        console.log(
          `✅ Export successful! File: ${filename}, Size: ${(
            jsonString.length / 1024
          ).toFixed(2)} KB`
        );
      }, 100);
    } catch (error) {
      console.error("❌ Export failed:", error);
    }
  });
}

// Make functions globally accessible for onclick handlers
window.viewDetails = viewDetails;
window.showMoreInfo = showMoreInfo;
window.copyToClipboard = copyToClipboard;
window.viewThreatDetails = viewThreatDetails;
window.reportFalsePositive = reportFalsePositive;
window.whitelistDomain = whitelistDomain;
window.previousPage = previousPage;
window.nextPage = nextPage;

function viewDetails(url) {
  alert("Detailed information for: " + url);
}

function showMoreInfo(url) {
  alert("Additional information for: " + url);
}

function previousPage() {
  console.log("Previous page");
}

function nextPage() {
  console.log("Next page");
}

// COMPLETE REWRITE: Export Analytics Report Functionality
function setupExportReportButton() {
  const exportBtn = document.getElementById("exportReportBtn");
  if (!exportBtn) {
    console.warn("⚠️ Export Report button not found");
    return;
  }

  console.log("✅ Export Report button found, attaching event listener");

  exportBtn.addEventListener("click", function () {
    console.log("🚀 Export Report button clicked!");

    try {
      // Get selected time range
      const timeRange =
        document.getElementById("analyticsTimeRange")?.value || "7d";
      console.log("📅 Time range:", timeRange);

      // Create comprehensive analytics report
      const analyticsReport = {
        reportMetadata: {
          generatedAt: new Date().toISOString(),
          reportType: "PhishGuard Analytics Report",
          timeRange: timeRange,
          version: "2.1",
        },
        performanceSummary: {
          detectionAccuracy: "97.3%",
          avgResponseTime: "0.23s",
          falsePositiveRate: "0.65%",
          estimatedThreatValueBlocked: "$12,400",
          totalThreatsBlocked: 2847,
          sitesScanned: 15432,
          activeUsers: 1205,
        },
        threatDetectionTrends: {
          period: "Last 7 Days",
          dailyData: [
            { day: "Monday", threats: 234, blocked: 228, allowed: 6 },
            { day: "Tuesday", threats: 198, blocked: 195, allowed: 3 },
            { day: "Wednesday", threats: 267, blocked: 263, allowed: 4 },
            { day: "Thursday", threats: 245, blocked: 241, allowed: 4 },
            { day: "Friday", threats: 289, blocked: 285, allowed: 4 },
            { day: "Saturday", threats: 156, blocked: 153, allowed: 3 },
            { day: "Sunday", threats: 178, blocked: 175, allowed: 3 },
          ],
          averageDaily: 224,
          totalThreats: 1567,
          peakDay: "Friday",
        },
        attackVectors: [
          {
            vector: "Email Links",
            percentage: 45,
            threatCount: 1247,
            trend: "increasing",
            riskLevel: "high",
          },
          {
            vector: "Social Media",
            percentage: 32,
            threatCount: 887,
            trend: "stable",
            riskLevel: "medium",
          },
          {
            vector: "Direct URLs",
            percentage: 18,
            threatCount: 499,
            trend: "decreasing",
            riskLevel: "medium",
          },
          {
            vector: "Ads/Pop-ups",
            percentage: 5,
            threatCount: 138,
            trend: "stable",
            riskLevel: "low",
          },
        ],
        geographicDistribution: {
          topOrigins: [
            { country: "Unknown/VPN", percentage: 35, threatCount: 970 },
            { country: "Russia", percentage: 22, threatCount: 610 },
            { country: "China", percentage: 18, threatCount: 499 },
            { country: "Nigeria", percentage: 12, threatCount: 333 },
            { country: "Other", percentage: 13, threatCount: 360 },
          ],
          totalCountries: 47,
          highRiskRegions: ["Eastern Europe", "Southeast Asia", "West Africa"],
        },
        temporalAnalysis: {
          peakThreatTimes: [
            {
              period: "12:00-14:00",
              level: "High",
              threatCount: 234,
              percentage: 21,
            },
            {
              period: "09:00-11:00",
              level: "Medium",
              threatCount: 156,
              percentage: 14,
            },
            {
              period: "15:00-17:00",
              level: "Medium",
              threatCount: 143,
              percentage: 13,
            },
            {
              period: "03:00-05:00",
              level: "Low",
              threatCount: 34,
              percentage: 3,
            },
          ],
          safestHours: ["02:00-04:00", "04:00-06:00"],
          riskiestHours: ["12:00-14:00", "18:00-20:00"],
        },
        userRiskAnalysis: {
          distribution: {
            lowRisk: {
              percentage: 60,
              userCount: 726,
              description: "Following best practices",
            },
            mediumRisk: {
              percentage: 30,
              userCount: 363,
              description: "Some risky behavior",
            },
            highRisk: {
              percentage: 10,
              userCount: 121,
              description: "Requires immediate attention",
            },
          },
          totalUsers: 1210,
          usersNeedingTraining: 121,
          complianceScore: "74%",
        },
        aiModelPerformance: {
          metrics: {
            precision: 98.7,
            recall: 96.2,
            f1Score: 97.4,
            accuracy: 97.8,
          },
          modelInfo: {
            lastUpdate: "2 hours ago",
            trainingDataSamples: "2.3M",
            nextUpdate: "In 4 hours",
            modelVersion: "v4.2.1",
          },
          improvements: [
            "Improved phishing detection by 3.2%",
            "Reduced false positives by 15%",
            "Enhanced malware signature recognition",
          ],
        },
        securityRecommendations: {
          critical: [
            "Schedule security training for 121 high-risk users",
            "Enable multi-factor authentication for vulnerable accounts",
          ],
          high: [
            "Review email security policies for improved protection",
            "Implement stricter URL filtering for social media links",
          ],
          medium: [
            "Update firewall rules to block high-risk regions",
            "Conduct quarterly security audits",
          ],
          actionItems: 6,
          estimatedImpact: "Reduce threats by 23%",
        },
      };

      // Convert to JSON string
      const jsonString = JSON.stringify(analyticsReport, null, 2);
      console.log(
        "📄 Analytics report JSON created, size:",
        jsonString.length,
        "bytes"
      );

      // Create blob
      const blob = new Blob([jsonString], { type: "application/json" });
      console.log("📦 Blob created");

      // Create object URL
      const url = URL.createObjectURL(blob);
      console.log("🔗 Object URL created:", url.substring(0, 50) + "...");

      // Create filename with timestamp
      const now = new Date();
      const timestamp = now.toISOString().replace(/[:.]/g, "-").slice(0, 19);
      const filename = `PhishGuard_Analytics_${timestamp}.json`;
      console.log("📝 Filename:", filename);

      // Create temporary link and trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.style.display = "none";
      document.body.appendChild(a);

      console.log("🖱️ Triggering download...");
      a.click();

      // Cleanup
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        const sizeKB = (jsonString.length / 1024).toFixed(2);
        console.log("🧹 Cleanup complete");
        console.log(
          `✅ Analytics report exported! File: ${filename}, Size: ${sizeKB} KB, Time Range: ${timeRange}`
        );
      }, 100);
    } catch (error) {
      console.error("❌ Export failed:", error);
    }
  });
}

function initializeAnalyticsPage() {
  console.log("📊 Initializing Analytics Page...");

  // Setup export report button with event listener (with delay for DOM)
  setTimeout(() => {
    setupExportReportButton();
  }, 100);

  // Initialize analytics charts
  setTimeout(() => {
    // Create analytics trend chart
    const ctx = document.getElementById("analyticsTrendChart");
    if (ctx) {
      new Chart(ctx.getContext("2d"), {
        type: "line",
        data: {
          labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
          datasets: [
            {
              label: "Threats Detected",
              data: [234, 198, 267, 245, 289, 156, 178],
              borderColor: "#1FB8CD",
              backgroundColor: "rgba(31, 184, 205, 0.1)",
              tension: 0.4,
              fill: true,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        },
      });
    }

    // Create geo chart
    const geoCtx = document.getElementById("geoChart");
    if (geoCtx) {
      new Chart(geoCtx.getContext("2d"), {
        type: "bar",
        data: {
          labels: ["Russia", "China", "Nigeria", "Brazil", "India"],
          datasets: [
            {
              data: [89, 67, 45, 32, 28],
              backgroundColor: [
                "#ff4757",
                "#ff6348",
                "#ffa502",
                "#FFC185",
                "#1FB8CD",
              ],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
        },
      });
    }
  }, 100);
}

function initializeSettingsPage() {
  // Settings tab switching
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const tabName = this.getAttribute("data-tab");

      // Remove active class from all
      tabButtons.forEach((btn) => btn.classList.remove("active"));
      tabContents.forEach((content) => content.classList.remove("active"));

      // Add active to clicked tab
      this.classList.add("active");
      document
        .querySelector(`[data-tab="${tabName}"].tab-content`)
        .classList.add("active");
    });
  });

  // Save settings functionality with event listener
  const saveSettingsBtn = document.getElementById("saveSettingsBtn");
  if (saveSettingsBtn) {
    saveSettingsBtn.addEventListener("click", function () {
      console.log("💾 Save Settings clicked");

      const saveStatus = document.getElementById("saveStatus");
      if (saveStatus) {
        // Collect all toggle switches and save their states
        const toggles = document.querySelectorAll('input[type="checkbox"]');
        const settings = {};

        toggles.forEach((toggle) => {
          if (toggle.id) {
            settings[toggle.id] = toggle.checked;
            console.log(`✅ Saved ${toggle.id}: ${toggle.checked}`);
          }
        });

        // Save to localStorage
        localStorage.setItem("phishguardSettings", JSON.stringify(settings));

        // Update status message
        saveStatus.textContent = "✓ Settings saved successfully!";
        saveStatus.style.color = "#1fb8cd";

        console.log("✅ All settings saved to localStorage");

        // Reset message after 3 seconds
        setTimeout(() => {
          saveStatus.textContent = "All changes saved automatically";
          saveStatus.style.color = "";
        }, 3000);
      }
    });
  }

  // Reset settings with event listener
  const resetSettingsBtn = document.getElementById("resetSettingsBtn");
  if (resetSettingsBtn) {
    resetSettingsBtn.addEventListener("click", function () {
      console.log("🔄 Reset Settings clicked");

      if (
        confirm(
          "Reset all settings to default values?\n\nThis will:\n• Enable all protection features\n• Reset sensitivity to Balanced\n• Clear whitelist and blacklist\n• Reset all notification preferences\n\nThis action cannot be undone."
        )
      ) {
        console.log("✅ User confirmed reset");

        // Clear localStorage
        localStorage.removeItem("phishguardSettings");

        // Reset all toggles to default (checked)
        const toggles = document.querySelectorAll('input[type="checkbox"]');
        toggles.forEach((toggle) => {
          toggle.checked = true;
          console.log(`✅ Reset ${toggle.id} to: true`);
        });

        // Reset sensitivity slider to middle (2)
        const sensitivitySlider = document.getElementById("sensitivitySlider");
        if (sensitivitySlider) {
          sensitivitySlider.value = 2;
          sensitivitySlider.dispatchEvent(new Event("input"));
          console.log("✅ Reset sensitivity to: Balanced (2)");
        }

        // Clear domain lists
        const whitelistDomains = document.getElementById("whitelistDomains");
        const blacklistDomains = document.getElementById("blacklistDomains");

        if (whitelistDomains) {
          whitelistDomains.innerHTML = `
            <div class="chip">google.com <span class="chip-remove">×</span></div>
            <div class="chip">github.com <span class="chip-remove">×</span></div>
            <div class="chip">stackoverflow.com <span class="chip-remove">×</span></div>
          `;
          console.log("✅ Reset whitelist to defaults");
        }

        if (blacklistDomains) {
          blacklistDomains.innerHTML = `
            <div class="chip red">phishing-test.com <span class="chip-remove">×</span></div>
            <div class="chip red">malware-host.net <span class="chip-remove">×</span></div>
          `;
          console.log("✅ Reset blacklist to defaults");
        }

        // Re-attach event listeners to chip remove buttons
        document.querySelectorAll(".chip-remove").forEach((btn) => {
          btn.addEventListener("click", function () {
            this.parentElement.remove();
          });
        });

        // Update status message
        const saveStatus = document.getElementById("saveStatus");
        if (saveStatus) {
          saveStatus.textContent = "✓ All settings reset to defaults!";
          saveStatus.style.color = "#1fb8cd";

          setTimeout(() => {
            saveStatus.textContent = "All changes saved automatically";
            saveStatus.style.color = "";
          }, 3000);
        }

        console.log("✅ Settings reset complete");
      } else {
        console.log("❌ User cancelled reset");
      }
    });
  }

  // Whitelist/Blacklist management with event listeners
  const addWhitelistBtn = document.getElementById("addWhitelistBtn");
  if (addWhitelistBtn) {
    addWhitelistBtn.addEventListener("click", function () {
      const input = document.getElementById("whitelistInput");
      if (input && input.value.trim()) {
        const domainValue = input.value.trim();
        const container = document.getElementById("whitelistDomains");
        const chip = document.createElement("div");
        chip.className = "chip";
        chip.innerHTML = `${domainValue} <span class="chip-remove">×</span>`;

        // Add event listener to the remove button
        const removeBtn = chip.querySelector(".chip-remove");
        removeBtn.addEventListener("click", function () {
          chip.remove();
        });

        container.appendChild(chip);
        input.value = "";
        console.log("✅ Added to whitelist:", domainValue);
      }
    });
  }

  const addBlacklistBtn = document.getElementById("addBlacklistBtn");
  if (addBlacklistBtn) {
    addBlacklistBtn.addEventListener("click", function () {
      const input = document.getElementById("blacklistInput");
      if (input && input.value.trim()) {
        const domainValue = input.value.trim();
        const container = document.getElementById("blacklistDomains");
        const chip = document.createElement("div");
        chip.className = "chip red";
        chip.innerHTML = `${domainValue} <span class="chip-remove">×</span>`;

        // Add event listener to the remove button
        const removeBtn = chip.querySelector(".chip-remove");
        removeBtn.addEventListener("click", function () {
          chip.remove();
        });

        container.appendChild(chip);
        input.value = "";
        console.log("✅ Added to blacklist:", domainValue);
      }
    });
  }

  // Add event listeners to existing chip remove buttons
  document.querySelectorAll(".chip-remove").forEach((btn) => {
    btn.addEventListener("click", function () {
      this.parentElement.remove();
    });
  });

  // Add Enter key support for whitelist input
  const whitelistInput = document.getElementById("whitelistInput");
  if (whitelistInput) {
    whitelistInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        addWhitelistBtn.click();
      }
    });
  }

  // Add Enter key support for blacklist input
  const blacklistInput = document.getElementById("blacklistInput");
  if (blacklistInput) {
    blacklistInput.addEventListener("keypress", function (e) {
      if (e.key === "Enter") {
        e.preventDefault();
        addBlacklistBtn.click();
      }
    });
  }

  // Sensitivity slider
  const sensitivitySlider = document.getElementById("sensitivitySlider");
  if (sensitivitySlider) {
    sensitivitySlider.addEventListener("input", function () {
      const descriptions = [
        {
          title: "Conservative Mode",
          desc: "Fewer false positives but may miss some threats. Best for experienced users.",
          accuracy: "92%",
          falsePos: "~0.5%",
        },
        {
          title: "Balanced Mode",
          desc: "Optimal balance between security and usability. Recommended for most users.",
          accuracy: "97%",
          falsePos: "~2%",
        },
        {
          title: "Aggressive Mode",
          desc: "Maximum protection. May flag more suspicious sites. Best for high-security environments.",
          accuracy: "99%",
          falsePos: "~5%",
        },
      ];
      const desc = descriptions[this.value - 1];
      const descEl = document.getElementById("sensitivityDesc");
      if (descEl) {
        descEl.innerHTML = `
          <strong>${desc.title}</strong>
          <p>${desc.desc}</p>
          <div class="sensitivity-stats">
            <div class="stat">
              <span class="stat-label">Expected Accuracy</span>
              <span class="stat-value">${desc.accuracy}</span>
            </div>
            <div class="stat">
              <span class="stat-label">False Positives</span>
              <span class="stat-value">${desc.falsePos}</span>
            </div>
          </div>
        `;
      }
    });
  }
}

// Global FAQ toggle function (must be defined before HTML uses it)
window.toggleFAQ = function (element) {
  const faqItem = element.parentElement;
  const answer = faqItem.querySelector(".faq-answer");
  const toggle = element.querySelector(".faq-toggle");

  if (faqItem.classList.contains("active")) {
    faqItem.classList.remove("active");
    toggle.textContent = "+";
  } else {
    // Close all other FAQs
    document.querySelectorAll(".faq-item-enhanced").forEach((item) => {
      item.classList.remove("active");
      item.querySelector(".faq-toggle").textContent = "+";
    });

    faqItem.classList.add("active");
    toggle.textContent = "−";
  }
};

// Global modal system for displaying help content
function showHelpModal(title, content) {
  // Remove existing modal if any
  const existingModal = document.querySelector(".help-modal-overlay");
  if (existingModal) {
    existingModal.remove();
  }

  // Create modal
  const modal = document.createElement("div");
  modal.className = "help-modal-overlay";
  modal.innerHTML = `
    <div class="help-modal">
      <div class="help-modal-header">
        <h2>${title}</h2>
        <button class="help-modal-close" onclick="this.closest('.help-modal-overlay').remove()">×</button>
      </div>
      <div class="help-modal-body">
        ${content}
      </div>
      <div class="help-modal-footer">
        <button class="btn-secondary" onclick="this.closest('.help-modal-overlay').remove()">Close</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Close on overlay click
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.remove();
    }
  });

  // Close on Escape key
  const escapeHandler = function (e) {
    if (e.key === "Escape") {
      modal.remove();
      document.removeEventListener("keydown", escapeHandler);
    }
  };
  document.addEventListener("keydown", escapeHandler);
}

// Global help content functions (must be defined before HTML uses them)
window.showGettingStarted = function () {
  showHelpModal(
    "Getting Started Guide",
    `
      <div class="help-content-modal">
        <div class="modal-section">
          <h3>📥 Step 1: Installation</h3>
          <p>You've already completed this step! PhishGuard AI is installed in your browser.</p>
          <ul>
            <li>The extension icon should appear in your browser toolbar</li>
            <li>Click the icon anytime to see protection status</li>
            <li>Green shield = Protection active</li>
          </ul>
        </div>

        <div class="modal-section">
          <h3>⚙️ Step 2: Configure Protection</h3>
          <p>Customize your security settings for optimal protection:</p>
          <ol>
            <li><strong>Go to Settings</strong> - Click the dashboard icon, then Settings</li>
            <li><strong>Choose Sensitivity</strong> - Balanced mode recommended for most users</li>
            <li><strong>Add Trusted Sites</strong> - Whitelist your frequently used websites</li>
            <li><strong>Enable Notifications</strong> - Get alerts when threats are detected</li>
          </ol>
        </div>

        <div class="modal-section">
          <h3>🌐 Step 3: Browse Safely</h3>
          <p>Now you're protected! Here's what happens automatically:</p>
          <ul>
            <li>✅ All URLs are scanned in real-time (0.23s average)</li>
            <li>✅ Threats are blocked before page loads</li>
            <li>✅ You'll see warnings for suspicious sites</li>
            <li>✅ Detection history is logged for your review</li>
          </ul>
        </div>

        <div class="modal-section">
          <h3>🎯 Step 4: Understanding Warnings</h3>
          <p>When PhishGuard AI detects a threat:</p>
          <ol>
            <li><strong>Red Warning Page</strong> - Page is blocked with threat details</li>
            <li><strong>Risk Level</strong> - High, Medium, or Low threat classification</li>
            <li><strong>Your Options</strong>:
              <ul>
                <li>Go Back (Recommended) - Return to safety</li>
                <li>Report False Positive - If you believe it's safe</li>
                <li>Proceed Anyway - Continue at your own risk</li>
              </ul>
            </li>
          </ol>
        </div>

        <div class="modal-section success-box">
          <h3>✅ You're All Set!</h3>
          <p><strong>PhishGuard AI is now protecting your browsing.</strong></p>
          <p>Check your Dashboard anytime to see:</p>
          <ul>
            <li>Number of threats blocked</li>
            <li>Recent detection history</li>
            <li>Analytics and trends</li>
          </ul>
        </div>

        <div class="modal-section">
          <h3>🆘 Need Help?</h3>
          <p>If you run into any issues:</p>
          <ul>
            <li>📧 Email: support@phishguard.ai</li>
            <li>💬 Live Chat: Available 24/7 in the Help section</li>
            <li>🌐 Community: Join our forum with 12,000+ members</li>
          </ul>
        </div>
      </div>
    `
  );
};

window.showVideoTutorials = function () {
  showHelpModal(
    "Video Tutorials",
    `
      <div class="help-content-modal">
        <p class="modal-intro">Watch step-by-step video guides to master PhishGuard AI</p>

        <div class="video-grid">
          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Installation & Setup</h4>
            <p>Complete walkthrough of installing and configuring PhishGuard AI</p>
            <div class="video-meta">
              <span>⏱️ 3:45</span>
              <span>👁️ 15.2K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Understanding Threat Detection</h4>
            <p>Learn how our AI identifies and blocks phishing attempts</p>
            <div class="video-meta">
              <span>⏱️ 5:20</span>
              <span>👁️ 12.8K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Dashboard Tour</h4>
            <p>Explore analytics, detection history, and reports</p>
            <div class="video-meta">
              <span>⏱️ 4:15</span>
              <span>👁️ 10.5K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Advanced Settings</h4>
            <p>Customize sensitivity, whitelists, and notifications</p>
            <div class="video-meta">
              <span>⏱️ 6:30</span>
              <span>👁️ 8.2K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Handling False Positives</h4>
            <p>What to do when legitimate sites are blocked</p>
            <div class="video-meta">
              <span>⏱️ 3:00</span>
              <span>👁️ 7.9K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Privacy & Security</h4>
            <p>Understanding data protection and privacy features</p>
            <div class="video-meta">
              <span>⏱️ 4:45</span>
              <span>👁️ 9.1K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Real Phishing Examples</h4>
            <p>See how PhishGuard AI catches real-world threats</p>
            <div class="video-meta">
              <span>⏱️ 7:12</span>
              <span>👁️ 18.4K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Team Management</h4>
            <p>Managing PhishGuard AI for your organization</p>
            <div class="video-meta">
              <span>⏱️ 5:55</span>
              <span>👁️ 6.3K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>API Integration</h4>
            <p>Integrate PhishGuard AI with your existing systems</p>
            <div class="video-meta">
              <span>⏱️ 8:20</span>
              <span>👁️ 4.7K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Troubleshooting Common Issues</h4>
            <p>Solutions to frequent problems and questions</p>
            <div class="video-meta">
              <span>⏱️ 6:00</span>
              <span>👁️ 11.2K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>Best Practices</h4>
            <p>Tips for maximizing protection and security</p>
            <div class="video-meta">
              <span>⏱️ 5:30</span>
              <span>👁️ 13.6K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>

          <div class="video-card">
            <div class="video-thumbnail">🎬</div>
            <h4>What's New in v2.0</h4>
            <p>Latest features and improvements explained</p>
            <div class="video-meta">
              <span>⏱️ 4:00</span>
              <span>👁️ 20.1K views</span>
            </div>
            <button class="btn-video">Watch Now</button>
          </div>
        </div>

        <div class="modal-section">
          <p class="text-center"><strong>📺 More videos coming soon!</strong></p>
          <p class="text-center">Subscribe to our YouTube channel for updates</p>
        </div>
      </div>
    `
  );
};

window.showUserManual = function () {
  showHelpModal(
    "Complete User Manual",
    `
      <div class="help-content-modal">
        <div class="manual-toc">
          <h3>📋 Table of Contents</h3>
          <ol>
            <li><a href="#intro">Introduction</a></li>
            <li><a href="#install">Installation</a></li>
            <li><a href="#features">Core Features</a></li>
            <li><a href="#dashboard">Dashboard</a></li>
            <li><a href="#settings">Settings</a></li>
            <li><a href="#detection">Detection History</a></li>
            <li><a href="#analytics">Analytics</a></li>
            <li><a href="#privacy">Privacy</a></li>
            <li><a href="#troubleshooting">Troubleshooting</a></li>
            <li><a href="#faq">FAQ</a></li>
          </ol>
        </div>

        <div class="modal-section" id="intro">
          <h3>1. Introduction</h3>
          <p><strong>PhishGuard AI</strong> is an advanced browser extension that uses artificial intelligence and machine learning to protect you from phishing attacks, malware, and malicious websites in real-time.</p>
          <p><strong>Key Benefits:</strong></p>
          <ul>
            <li>97.3% threat detection accuracy</li>
            <li>Real-time URL scanning (0.23s average)</li>
            <li>Zero-day phishing protection</li>
            <li>Privacy-first design</li>
            <li>Minimal performance impact</li>
          </ul>
        </div>

        <div class="modal-section" id="features">
          <h3>3. Core Features</h3>
          <h4>🛡️ Real-time Protection</h4>
          <p>All URLs are automatically scanned before pages load. Malicious sites are blocked instantly.</p>

          <h4>🤖 AI-Powered Detection</h4>
          <p>Advanced machine learning models analyze URLs, page content, SSL certificates, and behavioral patterns to identify threats.</p>

          <h4>📊 Analytics Dashboard</h4>
          <p>View detailed statistics on threats blocked, detection trends, attack vectors, and more.</p>

          <h4>⚙️ Customizable Settings</h4>
          <p>Adjust sensitivity levels, manage whitelists/blacklists, configure notifications, and more.</p>

          <h4>🔒 Privacy Protection</h4>
          <p>Most scanning happens locally. Only anonymized URL hashes are sent to servers. GDPR & CCPA compliant.</p>
        </div>

        <div class="modal-section" id="dashboard">
          <h3>4. Dashboard Overview</h3>
          <p>Access the dashboard by clicking "More Data" in the extension popup.</p>

          <h4>📈 Key Metrics</h4>
          <ul>
            <li><strong>Total Threats Blocked:</strong> Cumulative count of all blocked threats</li>
            <li><strong>Detection Rate:</strong> Percentage of malicious sites caught</li>
            <li><strong>Active Users:</strong> Number of protected users in your organization</li>
            <li><strong>Response Time:</strong> Average scan duration</li>
          </ul>

          <h4>📊 Charts & Visualizations</h4>
          <ul>
            <li><strong>Daily Phishing Attempts:</strong> Line chart showing threats over time</li>
            <li><strong>Threat Sources:</strong> Pie chart of attack origins</li>
            <li><strong>Attack Vectors:</strong> Distribution of threat types</li>
          </ul>
        </div>

        <div class="modal-section" id="settings">
          <h3>5. Settings Configuration</h3>

          <h4>🛡️ Protection Tab</h4>
          <ul>
            <li><strong>Real-time Scanning:</strong> Toggle URL protection on/off</li>
            <li><strong>AI Detection:</strong> Enable/disable machine learning analysis</li>
            <li><strong>Sensitivity Slider:</strong> Conservative / Balanced / Aggressive
              <ul>
                <li>Conservative: 92% accuracy, ~0.5% false positives</li>
                <li>Balanced: 97% accuracy, ~2% false positives (recommended)</li>
                <li>Aggressive: 99% accuracy, ~5% false positives</li>
              </ul>
            </li>
            <li><strong>Whitelist:</strong> Add trusted domains that will never be blocked</li>
            <li><strong>Blacklist:</strong> Always block specific domains</li>
          </ul>

          <h4>🔔 Notifications Tab</h4>
          <ul>
            <li><strong>Desktop Notifications:</strong> System alerts for threats</li>
            <li><strong>Sound Alerts:</strong> Audio warning for high-risk threats</li>
            <li><strong>Email Notifications:</strong> Critical alerts sent to your email</li>
            <li><strong>Report Frequency:</strong> Daily / Weekly / Monthly summaries</li>
          </ul>

          <h4>🔒 Privacy Tab</h4>
          <ul>
            <li><strong>Usage Statistics:</strong> Share anonymous data to improve service</li>
            <li><strong>Cloud Sync:</strong> Synchronize settings across devices</li>
            <li><strong>Data Retention:</strong> How long history is stored (7-365 days)</li>
          </ul>
        </div>

        <div class="modal-section" id="privacy">
          <h3>8. Privacy & Data Protection</h3>
          <p><strong>We take your privacy seriously:</strong></p>
          <ul>
            <li>✅ Most URL analysis happens on your device</li>
            <li>✅ Only SHA-256 hashes sent to servers (not full URLs)</li>
            <li>✅ No browsing history stored on our servers</li>
            <li>✅ All data encrypted with TLS 1.3</li>
            <li>✅ GDPR and CCPA compliant</li>
            <li>✅ No data sold to third parties</li>
          </ul>
          <p>Read our full <a href="#">Privacy Policy</a> for detailed information.</p>
        </div>

        <div class="modal-section success-box">
          <h3>📖 Complete Manual</h3>
          <p>This is an abbreviated version. Download the full 50-page PDF manual:</p>
          <button class="btn-primary" onclick="alert('Downloading PhishGuard_AI_Manual_v2.0.pdf')">📥 Download Full PDF Manual</button>
        </div>
      </div>
    `
  );
};

window.showTroubleshooting = function () {
  showHelpModal(
    "Troubleshooting Guide",
    `
      <div class="help-content-modal">
        <p class="modal-intro">Solutions to common issues and problems</p>

        <div class="troubleshooting-item">
          <h3>🚫 Issue: Legitimate Sites Are Being Blocked</h3>
          <div class="issue-solution">
            <h4>Symptoms:</h4>
            <ul>
              <li>You trust the website but PhishGuard AI blocks it</li>
              <li>Warning page appears for safe sites</li>
            </ul>
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Check the URL carefully</strong> - Attackers use look-alike domains (e.g., "paypa1.com" instead of "paypal.com")</li>
              <li><strong>Report False Positive:</strong> Click the button on the warning page</li>
              <li><strong>Add to Whitelist:</strong>
                <ul>
                  <li>Go to Settings → Protection</li>
                  <li>Scroll to "Protected Domains"</li>
                  <li>Add domain to Whitelist</li>
                </ul>
              </li>
              <li><strong>Adjust Sensitivity:</strong> Lower the detection sensitivity to Balanced or Conservative mode</li>
            </ol>
          </div>
        </div>

        <div class="troubleshooting-item">
          <h3>🐌 Issue: Browser Feels Slow</h3>
          <div class="issue-solution">
            <h4>Symptoms:</h4>
            <ul>
              <li>Pages load slower than usual</li>
              <li>Browser feels sluggish</li>
            </ul>
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Check Other Extensions:</strong> Disable other security extensions that might conflict</li>
              <li><strong>Increase Cache Duration:</strong>
                <ul>
                  <li>Settings → Advanced → Cache Duration</li>
                  <li>Increase to 7200 seconds (2 hours)</li>
                </ul>
              </li>
              <li><strong>Disable Debug Mode:</strong> Make sure Debug Mode is OFF in Advanced settings</li>
              <li><strong>Clear Browser Cache:</strong> Sometimes helps with performance</li>
              <li><strong>Contact Support:</strong> If issues persist, we can investigate further</li>
            </ol>
          </div>
        </div>

        <div class="troubleshooting-item">
          <h3>❌ Issue: Extension Not Working</h3>
          <div class="issue-solution">
            <h4>Symptoms:</h4>
            <ul>
              <li>Icon shows as inactive/grayed out</li>
              <li>No threats being detected</li>
              <li>Dashboard won't open</li>
            </ul>
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Check if Extension is Enabled:</strong>
                <ul>
                  <li>Go to chrome://extensions/</li>
                  <li>Find PhishGuard AI</li>
                  <li>Make sure toggle is ON (blue)</li>
                </ul>
              </li>
              <li><strong>Reload the Extension:</strong> Click the reload icon on chrome://extensions/</li>
              <li><strong>Restart Browser:</strong> Close and reopen Chrome/Edge</li>
              <li><strong>Reinstall Extension:</strong>
                <ul>
                  <li>Remove PhishGuard AI</li>
                  <li>Reinstall from Chrome Web Store</li>
                  <li>Your settings may be lost (export first if needed)</li>
                </ul>
              </li>
            </ol>
          </div>
        </div>

        <div class="troubleshooting-item">
          <h3>📊 Issue: Dashboard Shows "No Data"</h3>
          <div class="issue-solution">
            <h4>Symptoms:</h4>
            <ul>
              <li>Empty charts and graphs</li>
              <li>Zero threats shown</li>
            </ul>
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Just Installed?</strong> Data accumulates over time. Check back after browsing for a while.</li>
              <li><strong>Check Internet Connection:</strong> Dashboard needs to sync with servers</li>
              <li><strong>Clear Cache:</strong> Settings → Privacy → Clear All History</li>
              <li><strong>Re-login:</strong> Sign out and sign back in to your account</li>
            </ol>
          </div>
        </div>

        <div class="troubleshooting-item">
          <h3>🔔 Issue: Not Receiving Notifications</h3>
          <div class="issue-solution">
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Check Extension Permissions:</strong>
                <ul>
                  <li>Go to chrome://extensions/</li>
                  <li>Click "Details" on PhishGuard AI</li>
                  <li>Ensure "Notifications" permission is granted</li>
                </ul>
              </li>
              <li><strong>Check Browser Settings:</strong>
                <ul>
                  <li>chrome://settings/content/notifications</li>
                  <li>Make sure notifications are allowed</li>
                </ul>
              </li>
              <li><strong>Enable in PhishGuard Settings:</strong>
                <ul>
                  <li>Settings → Notifications</li>
                  <li>Toggle ON "Desktop Notifications"</li>
                </ul>
              </li>
            </ol>
          </div>
        </div>

        <div class="troubleshooting-item">
          <h3>🔐 Issue: Can't Access Certain Features</h3>
          <div class="issue-solution">
            <h4>Symptoms:</h4>
            <ul>
              <li>Features appear grayed out</li>
              <li>"Premium Only" labels</li>
            </ul>
            <h4>Solutions:</h4>
            <ol>
              <li><strong>Check Your Plan:</strong> Some features require Premium subscription</li>
              <li><strong>Upgrade Account:</strong> Settings → Account → Upgrade Plan</li>
              <li><strong>Enterprise Features:</strong> Contact sales for organization-wide licenses</li>
            </ol>
          </div>
        </div>

        <div class="modal-section error-box">
          <h3>❗ Still Having Issues?</h3>
          <p><strong>Contact our support team:</strong></p>
          <ul>
            <li>📧 Email: support@phishguard.ai (Response: 2-4 hours)</li>
            <li>💬 Live Chat: Available 24/7 in Help section</li>
            <li>🌐 Community Forum: Get help from other users</li>
          </ul>
          <p><strong>When contacting support, include:</strong></p>
          <ul>
            <li>Browser version (Chrome/Edge/Brave)</li>
            <li>Extension version (found in chrome://extensions/)</li>
            <li>Description of the issue</li>
            <li>Screenshots if applicable</li>
          </ul>
        </div>
      </div>
    `
  );
};

window.showBestPractices = function () {
  showHelpModal(
    "Security Best Practices",
    `
      <div class="help-content-modal">
        <p class="modal-intro">Maximize your protection with these expert tips</p>

        <div class="best-practice-card">
          <div class="practice-icon">🛡️</div>
          <h3>1. Keep Protection Always Active</h3>
          <p><strong>Why:</strong> Threats can appear at any moment. Constant protection is essential.</p>
          <ul>
            <li>Never disable real-time scanning unless absolutely necessary</li>
            <li>Check extension icon regularly - green shield means protected</li>
            <li>If you must disable temporarily, re-enable immediately after</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">⚙️</div>
          <h3>2. Use Balanced Sensitivity</h3>
          <p><strong>Why:</strong> Provides optimal protection without too many false positives.</p>
          <ul>
            <li>Balanced mode: 97% accuracy with only ~2% false positives</li>
            <li>Only use Conservative if you're an advanced user</li>
            <li>Use Aggressive for high-security environments (banking, healthcare)</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">📋</div>
          <h3>3. Maintain Your Whitelist</h3>
          <p><strong>Why:</strong> Reduces false positives for sites you trust.</p>
          <ul>
            <li>Add your banking websites to whitelist</li>
            <li>Include work-related domains</li>
            <li>Add frequently used services (email, cloud storage)</li>
            <li><strong>Warning:</strong> Only whitelist domains you absolutely trust!</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">🔔</div>
          <h3>4. Enable Notifications</h3>
          <p><strong>Why:</strong> Stay informed about threats in real-time.</p>
          <ul>
            <li>Desktop notifications for immediate awareness</li>
            <li>Email alerts for critical threats</li>
            <li>Daily summary reports to review activity</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">📊</div>
          <h3>5. Review Your Dashboard Weekly</h3>
          <p><strong>Why:</strong> Understand your threat landscape and trends.</p>
          <ul>
            <li>Check which types of threats are targeting you</li>
            <li>Review detection history for patterns</li>
            <li>Look at analytics to see peak threat times</li>
            <li>Adjust settings based on what you learn</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">🔍</div>
          <h3>6. Always Verify URLs</h3>
          <p><strong>Why:</strong> PhishGuard AI is highly accurate but not perfect.</p>
          <ul>
            <li>Look for HTTPS and padlock icon</li>
            <li>Check for spelling mistakes in domain (paypa1.com vs paypal.com)</li>
            <li>Hover over links before clicking</li>
            <li>Be suspicious of shortened URLs (bit.ly, tinyurl)</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">⚠️</div>
          <h3>7. Never Override High-Risk Warnings</h3>
          <p><strong>Why:</strong> High-risk threats are very dangerous.</p>
          <ul>
            <li>If PhishGuard AI says "High Risk" - trust it and go back</li>
            <li>Only override "Medium" or "Low" warnings if you're certain</li>
            <li>When in doubt, close the tab and search for the official site</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">🔐</div>
          <h3>8. Use Strong Passwords + 2FA</h3>
          <p><strong>Why:</strong> PhishGuard AI protects against phishing, but password security is also crucial.</p>
          <ul>
            <li>Use unique passwords for each site</li>
            <li>Enable two-factor authentication (2FA) everywhere possible</li>
            <li>Use a password manager (1Password, Bitwarden, LastPass)</li>
            <li>Never share passwords via email or text</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">👥</div>
          <h3>9. Educate Your Team</h3>
          <p><strong>Why:</strong> Human error is the weakest link in security.</p>
          <ul>
            <li>Share PhishGuard AI with colleagues and family</li>
            <li>Conduct regular security training</li>
            <li>Share threat examples from your Detection History</li>
            <li>Create a culture of security awareness</li>
          </ul>
        </div>

        <div class="best-practice-card">
          <div class="practice-icon">🔄</div>
          <h3>10. Keep Everything Updated</h3>
          <p><strong>Why:</strong> Updates include critical security patches.</p>
          <ul>
            <li>PhishGuard AI updates automatically</li>
            <li>Keep your browser updated to latest version</li>
            <li>Update your operating system regularly</li>
            <li>Check for extension updates weekly</li>
          </ul>
        </div>

        <div class="modal-section success-box">
          <h3>✅ Follow These Practices</h3>
          <p><strong>By following these best practices, you'll maximize your protection against phishing and cyber threats.</strong></p>
          <p>Remember: PhishGuard AI is a powerful tool, but security is a combination of technology and smart behavior!</p>
        </div>
      </div>
    `
  );
};

window.showSecurityGuide = function () {
  showHelpModal(
    "Complete Security Guide",
    `
      <div class="help-content-modal">
        <p class="modal-intro">Understand phishing threats and how to stay protected</p>

        <div class="modal-section">
          <h3>🎣 What is Phishing?</h3>
          <p><strong>Phishing</strong> is a cyber attack where criminals impersonate legitimate organizations to steal your sensitive information (passwords, credit cards, personal data).</p>

          <h4>Common Phishing Types:</h4>
          <ul>
            <li><strong>Email Phishing:</strong> Fake emails from "banks" or "services"</li>
            <li><strong>Spear Phishing:</strong> Targeted attacks on specific individuals</li>
            <li><strong>Smishing:</strong> Phishing via SMS text messages</li>
            <li><strong>Vishing:</strong> Voice phishing via phone calls</li>
            <li><strong>Clone Phishing:</strong> Duplicates of legitimate emails with malicious links</li>
          </ul>
        </div>

        <div class="modal-section error-box">
          <h3>🚩 Red Flags to Watch For</h3>
          <ol>
            <li><strong>Urgent Language:</strong> "Your account will be closed!" "Act now!"</li>
            <li><strong>Suspicious Sender:</strong> Email from @gmai1.com instead of @gmail.com</li>
            <li><strong>Generic Greetings:</strong> "Dear Customer" instead of your actual name</li>
            <li><strong>Misspellings:</strong> Poor grammar and typos</li>
            <li><strong>Suspicious Links:</strong> Hover to see real URL (often different from text)</li>
            <li><strong>Unexpected Attachments:</strong> .exe, .zip files you didn't request</li>
            <li><strong>Too Good to Be True:</strong> "You won $1,000,000!" scams</li>
            <li><strong>Request for Sensitive Info:</strong> Legitimate companies never ask for passwords via email</li>
          </ol>
        </div>

        <div class="modal-section">
          <h3>🛡️ How PhishGuard AI Protects You</h3>

          <h4>1. URL Analysis</h4>
          <p>Examines domain structure, age, registrar, and patterns to identify suspicious sites.</p>

          <h4>2. Machine Learning</h4>
          <p>AI models trained on 2.3M phishing samples recognize patterns humans might miss.</p>

          <h4>3. Content Analysis</h4>
          <p>Scans page structure, forms, JavaScript, and embedded content for threats.</p>

          <h4>4. SSL Verification</h4>
          <p>Checks certificate validity, issuer, and domain match.</p>

          <h4>5. Threat Intelligence</h4>
          <p>Real-time database of known malicious sites updated every 60 seconds.</p>

          <h4>6. Behavioral Analysis</h4>
          <p>Detects suspicious behavior like excessive redirects or hidden iframes.</p>
        </div>

        <div class="modal-section">
          <h3>✅ What To Do When You Encounter Phishing</h3>

          <h4>If PhishGuard AI Blocks a Site:</h4>
          <ol>
            <li><strong>Don't Proceed:</strong> Trust the warning - go back to safety</li>
            <li><strong>Don't Enter Information:</strong> Never type passwords on blocked sites</li>
            <li><strong>Report It:</strong> Click "Report Threat" to help us track attacks</li>
            <li><strong>Tell Others:</strong> Warn colleagues if it's a targeted attack</li>
          </ol>

          <h4>If You Clicked a Phishing Link:</h4>
          <ol>
            <li><strong>Don't Panic:</strong> Act quickly but calmly</li>
            <li><strong>Disconnect:</strong> Immediately close the browser tab</li>
            <li><strong>Change Passwords:</strong> If you entered any credentials, change them NOW</li>
            <li><strong>Enable 2FA:</strong> Add extra security to compromised accounts</li>
            <li><strong>Scan for Malware:</strong> Run antivirus scan</li>
            <li><strong>Monitor Accounts:</strong> Watch for suspicious activity</li>
            <li><strong>Report:</strong> Contact your IT department or the impersonated organization</li>
          </ol>
        </div>

        <div class="modal-section">
          <h3>🎓 Real-World Phishing Examples</h3>

          <div class="example-box">
            <h4>Example 1: Fake Banking Email</h4>
            <p><strong>Subject:</strong> "URGENT: Verify your account within 24 hours"</p>
            <p><strong>Red Flags:</strong></p>
            <ul>
              <li>Urgent deadline pressure</li>
              <li>Generic greeting ("Dear Customer")</li>
              <li>Link goes to bankofamer1ca.com (note the "1")</li>
              <li>Threat of account closure</li>
            </ul>
            <p><strong>PhishGuard AI Detection:</strong> HIGH RISK - Clone Phishing Attack</p>
          </div>

          <div class="example-box">
            <h4>Example 2: Fake Package Delivery</h4>
            <p><strong>Subject:</strong> "Your package couldn't be delivered"</p>
            <p><strong>Red Flags:</strong></p>
            <ul>
              <li>You didn't order anything</li>
              <li>Suspicious tracking link</li>
              <li>From @fedex-delivery.com (not @fedex.com)</li>
              <li>Asks for "delivery fee" payment</li>
            </ul>
            <p><strong>PhishGuard AI Detection:</strong> HIGH RISK - Credential Harvesting</p>
          </div>

          <div class="example-box">
            <h4>Example 3: Fake Tech Support</h4>
            <p><strong>Message:</strong> "Your Microsoft Windows license has expired"</p>
            <p><strong>Red Flags:</strong></p>
            <ul>
              <li>Microsoft doesn't send these alerts</li>
              <li>Requests remote access to your computer</li>
              <li>Demands payment for "renewal"</li>
              <li>Phone number to call "support"</li>
            </ul>
            <p><strong>PhishGuard AI Detection:</strong> HIGH RISK - Tech Support Scam</p>
          </div>
        </div>

        <div class="modal-section success-box">
          <h3>💡 Key Takeaways</h3>
          <ul>
            <li>✅ Always verify URLs before entering sensitive information</li>
            <li>✅ Trust PhishGuard AI warnings - they're there to protect you</li>
            <li>✅ When in doubt, contact the organization directly via official channels</li>
            <li>✅ Enable 2FA on all important accounts</li>
            <li>✅ Keep PhishGuard AI updated and active</li>
            <li>✅ Report suspicious emails to your IT department</li>
            <li>✅ Educate yourself and others about phishing tactics</li>
          </ul>
        </div>

        <div class="modal-section">
          <h3>📚 Additional Resources</h3>
          <ul>
            <li><a href="#">📄 Phishing Statistics 2025</a></li>
            <li><a href="#">🎬 Video: Real Phishing Attacks Explained</a></li>
            <li><a href="#">📖 Whitepaper: The State of Phishing</a></li>
            <li><a href="#">🔗 FTC Consumer Alerts</a></li>
            <li><a href="#">🔗 Anti-Phishing Working Group (APWG)</a></li>
          </ul>
        </div>
      </div>
    `
  );
};

// Initialize Help Page - sets up FAQ filters and search
function initializeHelpPage() {
  // FAQ toggle functionality is now global (defined above)

  // Add click event listeners to FAQ questions (backup to inline onclick)
  console.log("Initializing Help Page - attaching FAQ click listeners...");
  const faqQuestions = document.querySelectorAll(".faq-question");
  console.log("Found", faqQuestions.length, "FAQ questions");

  faqQuestions.forEach((question, index) => {
    question.addEventListener("click", function (e) {
      console.log("FAQ question clicked via event listener!", index);
      window.toggleFAQ(this);
    });
  });

  // FAQ category filter
  const categoryBtns = document.querySelectorAll(".faq-category-btn");
  categoryBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const category = this.getAttribute("data-category");

      categoryBtns.forEach((b) => b.classList.remove("active"));
      this.classList.add("active");

      const faqItems = document.querySelectorAll(".faq-item-enhanced");
      faqItems.forEach((item) => {
        if (
          category === "all" ||
          item.getAttribute("data-category") === category
        ) {
          item.style.display = "block";
        } else {
          item.style.display = "none";
        }
      });
    });
  });

  // Help search
  const searchInput = document.getElementById("helpSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const query = this.value.toLowerCase();
      const faqItems = document.querySelectorAll(".faq-item-enhanced");

      faqItems.forEach((item) => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(query) ? "block" : "none";
      });
    });
  }
}

// Log when app.js finishes loading
console.log("✅ App.js fully loaded - All functions initialized");
