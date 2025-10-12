// 📊 ENHANCED POPUP WITH REAL-TIME USER ANALYTICS
// End-to-End Encrypted Personal Dashboard

// Configuration
const API_BASE = "http://localhost:8080/api";
const REFRESH_INTERVAL = 5000; // 5 seconds
let userId = null;
let deviceFingerprint = null;
let refreshTimer = null;

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener("DOMContentLoaded", async () => {
  console.log("🚀 PhishGuard AI Enhanced Popup Loading...");

  try {
    // Get or generate user ID
    userId = await getUserId();
    deviceFingerprint = generateDeviceFingerprint();

    console.log("✅ User ID:", userId);

    // Initial data load
    await loadUserAnalytics();

    // Start auto-refresh
    startAutoRefresh();

    // Setup event listeners
    setupEventListeners();

    // 🔴 Connect to live threat feed (SSE)
    connectLiveThreatFeed();

    console.log("✅ Popup ready with real-time analytics");
  } catch (error) {
    console.error("❌ Failed to initialize popup:", error);
    showError("Failed to initialize dashboard");
  }
});

// ==========================================
// USER ANALYTICS API
// ==========================================

async function loadUserAnalytics() {
  try {
    // Check if userId is available
    if (!userId) {
      console.warn("⚠️ User ID not yet available, skipping analytics load");
      return;
    }

    const response = await fetch(
      `${API_BASE}/user/${userId}/analytics?device_fingerprint=${deviceFingerprint}`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    console.log("📊 User analytics loaded:", data);

    // Update all UI components
    updateMainStats(data);
    updateActivityFeed(data.recent_activities);
    updateThreatBreakdown(data.threat_breakdown);
    updateDevicePerformance(data.device_performance);
    updateThreatSources(data.threat_sources);
    updateModelInfo(data.model_info);

    // Update last refresh time
    updateLastRefreshTime();
  } catch (error) {
    console.error("❌ Failed to load analytics:", error);
    showError("Unable to load analytics. Using cached data.");
  }
}

// ==========================================
// UI UPDATE FUNCTIONS
// ==========================================

function updateMainStats(data) {
  // Total threats blocked
  document.getElementById("total-blocked").textContent = formatNumber(
    data.total_threats_blocked
  );

  // Today's blocked threats
  document.getElementById("blocked-trend").innerHTML = `
        <span class="trend-icon">📈</span>
        <span class="trend-text">+${data.threats_last_24h} today</span>
    `;

  // Scans last 24h
  document.getElementById("scans-24h").textContent = formatNumber(
    data.activities_last_24h
  );

  // Processing speed
  const speed = data.device_performance.processing_speed_ms;
  document.getElementById("processing-speed").textContent = `${speed.toFixed(
    1
  )}ms`;

  // Update speed badge
  const speedBadge = document.getElementById("speed-badge");
  if (speed < 100) {
    speedBadge.className = "stat-badge success";
    speedBadge.textContent = "✅ Meeting target";
  } else {
    speedBadge.className = "stat-badge warning";
    speedBadge.textContent = "⚠️ Above target";
  }

  // Model version
  document.getElementById("model-version").textContent =
    data.model_info.version;

  // Model status
  const modelStatus = document.getElementById("model-status");
  if (data.model_info.update_available) {
    modelStatus.className = "stat-badge warning";
    modelStatus.textContent = "🔄 Update available";
  } else {
    modelStatus.className = "stat-badge success";
    modelStatus.textContent = "✅ Up to date";
  }
}

function updateActivityFeed(activities) {
  const feed = document.getElementById("activity-feed");

  if (!activities || activities.length === 0) {
    feed.innerHTML = `
            <div class="activity-item empty">
                <p>No recent activity</p>
            </div>
        `;
    return;
  }

  // Show last 5 activities
  feed.innerHTML = activities
    .slice(0, 5)
    .map((activity) => {
      const timeAgo = getTimeAgo(new Date(activity.timestamp));
      const threatIcon = getThreatIcon(
        activity.threat_type,
        activity.is_phishing
      );
      const actionColor =
        activity.action_taken === "blocked" ? "danger" : "warning";

      // Decrypt URL client-side (if encrypted)
      const displayUrl = decryptUrl(activity.encrypted_url) || activity.domain;

      return `
            <div class="activity-item ${
              activity.is_phishing ? "threat" : "safe"
            }">
                <div class="activity-icon">${threatIcon}</div>
                <div class="activity-content">
                    <div class="activity-url">${truncateUrl(displayUrl)}</div>
                    <div class="activity-meta">
                        <span class="activity-time">${timeAgo}</span>
                        <span class="activity-action ${actionColor}">${
        activity.action_taken
      }</span>
                        <span class="activity-confidence">${(
                          activity.confidence * 100
                        ).toFixed(0)}%</span>
                    </div>
                </div>
                <div class="activity-badge ${activity.threat_level.toLowerCase()}">
                    ${activity.threat_level}
                </div>
            </div>
        `;
    })
    .join("");
}

function updateThreatBreakdown(breakdown) {
  const total =
    breakdown.phishing +
    breakdown.malware +
    breakdown.cryptojacking +
    breakdown.scam;

  if (total === 0) {
    // Show "No threats detected" message
    document.getElementById("phishing-count").textContent = "0";
    document.getElementById("malware-count").textContent = "0";
    document.getElementById("crypto-count").textContent = "0";
    document.getElementById("scam-count").textContent = "0";
    return;
  }

  // Update counts and bars
  updateThreatType("phishing", breakdown.phishing, total);
  updateThreatType("malware", breakdown.malware, total);
  updateThreatType("crypto", breakdown.cryptojacking, total);
  updateThreatType("scam", breakdown.scam, total);
}

function updateThreatType(type, count, total) {
  const percentage = total > 0 ? (count / total) * 100 : 0;

  document.getElementById(`${type}-count`).textContent = count;
  document.getElementById(`${type}-bar`).style.width = `${percentage}%`;
}

function updateDevicePerformance(performance) {
  // Database status
  const dbSize = performance.local_db_size_mb.toFixed(1);
  document.getElementById("db-size").textContent = `${dbSize} MB`;

  // Cache hit rate
  const cacheRate = (performance.cache_hit_rate * 100).toFixed(0);
  document.getElementById("cache-rate").textContent = `${cacheRate}%`;

  // Memory usage
  const memoryUsage = performance.memory_usage_mb.toFixed(1);
  document.getElementById("memory-usage").textContent = `${memoryUsage} MB`;

  // Scan queue
  const pending = performance.pending_scans;
  const queueText = pending > 0 ? `${pending} pending` : "Empty";
  document.getElementById("scan-queue").textContent = queueText;

  // Update queue color
  const queueElement = document.getElementById("scan-queue");
  if (pending > 10) {
    queueElement.style.color = "#f59e0b"; // Warning
  } else if (pending > 0) {
    queueElement.style.color = "#3b82f6"; // Info
  } else {
    queueElement.style.color = "#10b981"; // Success
  }
}

function updateThreatSources(sources) {
  const container = document.getElementById("threat-sources");

  if (!sources || sources.length === 0) {
    container.innerHTML = `
            <div class="source-item empty">
                <p>No geographic threat data yet</p>
            </div>
        `;
    return;
  }

  // Show top 5 countries
  container.innerHTML = sources
    .slice(0, 5)
    .map((source) => {
      const flagEmoji = getCountryFlag(source.country_code);

      return `
            <div class="source-item">
                <div class="source-flag">${flagEmoji}</div>
                <div class="source-content">
                    <div class="source-name">${source.country_name}</div>
                    <div class="source-bar">
                        <div class="source-fill" style="width: ${source.percentage}%"></div>
                    </div>
                </div>
                <div class="source-count">${source.threat_count}</div>
            </div>
        `;
    })
    .join("");
}

function updateModelInfo(modelInfo) {
  const lastUpdated = getTimeAgo(new Date(modelInfo.last_updated));

  // Update model card
  document.getElementById("model-version").textContent = modelInfo.version;

  // Update status badge
  const statusBadge = document.getElementById("model-status");
  if (modelInfo.update_available) {
    statusBadge.className = "stat-badge warning";
    statusBadge.textContent = `🔄 Update to ${modelInfo.next_version}`;
    statusBadge.style.cursor = "pointer";
    statusBadge.onclick = () => updateModel(modelInfo.next_version);
  } else {
    statusBadge.className = "stat-badge success";
    statusBadge.textContent = `✅ Updated ${lastUpdated}`;
  }
}

// ==========================================
// EVENT HANDLERS
// ==========================================

function setupEventListeners() {
  // Check current URL
  document
    .getElementById("check-current-url")
    .addEventListener("click", async () => {
      const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true,
      });
      checkUrl(tab.url);
    });

  // View full dashboard
  document
    .getElementById("view-full-dashboard")
    .addEventListener("click", () => {
      chrome.tabs.create({ url: "http://localhost:3000" });
    });

  // Export data
  document.getElementById("export-data").addEventListener("click", () => {
    exportUserData();
  });
}

// ==========================================
// 🔴 REAL-TIME THREAT FEED (SSE)
// ==========================================

let eventSource = null;

function connectLiveThreatFeed() {
  try {
    // Check if userId is available
    if (!userId) {
      console.warn(
        "⚠️ User ID not yet available, skipping live feed connection"
      );
      return;
    }

    // Close existing connection
    if (eventSource) {
      eventSource.close();
    }

    // Create new EventSource connection
    eventSource = new EventSource(`${API_BASE}/user/${userId}/threats/live`);

    eventSource.onopen = () => {
      console.log("🔴 Connected to live threat feed");
      const liveIndicator = document.querySelector(".live-indicator");
      if (liveIndicator) {
        liveIndicator.style.display = "flex";
      }
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("🚨 New threat detected:", data);

        if (data.type === "new_threat") {
          // Update threats blocked counter with animation
          const counter = document.getElementById("total-blocked");
          const currentCount = parseInt(counter.textContent.replace(/,/g, ""));
          animateCounter(counter, currentCount, currentCount + 1);

          // Show live notification
          showLiveThreatNotification(data);

          // Refresh analytics to show new data
          setTimeout(() => loadUserAnalytics(), 500);
        }
      } catch (error) {
        console.error("Failed to parse SSE message:", error);
      }
    };

    eventSource.onerror = (error) => {
      console.error("❌ SSE connection error:", error);
      const liveIndicator = document.querySelector(".live-indicator");
      if (liveIndicator) {
        liveIndicator.style.display = "none";
      }

      // Attempt to reconnect after 5 seconds
      setTimeout(() => {
        console.log("🔄 Attempting to reconnect to live feed...");
        connectLiveThreatFeed();
      }, 5000);
    };
  } catch (error) {
    console.error("Failed to connect to live threat feed:", error);
  }
}

function showLiveThreatNotification(threat) {
  // Create notification element
  const notification = document.createElement("div");
  notification.className = "live-notification";
  notification.innerHTML = `
    <div class="notification-icon">🚨</div>
    <div class="notification-content">
      <div class="notification-title">New Threat Blocked!</div>
      <div class="notification-domain">${threat.domain}</div>
      <div class="notification-type">${threat.threat_type} - ${threat.threat_level}</div>
    </div>
  `;

  document.body.appendChild(notification);

  // Animate in
  setTimeout(() => notification.classList.add("show"), 10);

  // Remove after 5 seconds
  setTimeout(() => {
    notification.classList.remove("show");
    setTimeout(() => notification.remove(), 300);
  }, 5000);
}

function animateCounter(element, start, end) {
  const duration = 500;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);

    const current = Math.floor(start + (end - start) * progress);
    element.textContent = formatNumber(current);

    if (progress < 1) {
      requestAnimationFrame(update);
    }
  }

  requestAnimationFrame(update);
}

// Cleanup on popup close
window.addEventListener("beforeunload", () => {
  if (eventSource) {
    eventSource.close();
  }
});

async function checkUrl(url) {
  try {
    const response = await fetch(`${API_BASE}/check-url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url,
        user_id: userId,
        device_fingerprint: deviceFingerprint,
        sensitivity_mode: await getSensitivityMode(),
      }),
    });

    const result = await response.json();

    // Show result notification
    showNotification(result);

    // Refresh analytics
    await loadUserAnalytics();
  } catch (error) {
    console.error("❌ URL check failed:", error);
    showError("Unable to check URL");
  }
}

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

async function getUserId() {
  const result = await chrome.storage.local.get("userId");

  if (!result.userId) {
    // Generate new user ID
    const newUserId = crypto.randomUUID();
    await chrome.storage.local.set({ userId: newUserId });
    return newUserId;
  }

  return result.userId;
}

function generateDeviceFingerprint() {
  const ua = navigator.userAgent;
  const version = chrome.runtime.getManifest().version;

  // Simple fingerprint (in production, use more sophisticated method)
  const fingerprint = btoa(`${ua}-${version}-${navigator.language}`);
  return fingerprint.substring(0, 64);
}

async function getSensitivityMode() {
  const result = await chrome.storage.local.get("sensitivityMode");
  return result.sensitivityMode || "balanced";
}

function decryptUrl(encryptedUrl) {
  // Client-side decryption using user's encryption key
  // TODO: Implement AES-256-GCM decryption
  // For now, return encrypted marker
  return encryptedUrl ? "[ENCRYPTED]" : null;
}

function startAutoRefresh() {
  refreshTimer = setInterval(async () => {
    await loadUserAnalytics();
  }, REFRESH_INTERVAL);
}

function updateLastRefreshTime() {
  document.getElementById("last-update").textContent = `Last updated: Just now`;
}

function showError(message) {
  // Show error toast
  console.error(message);
  // TODO: Implement toast notification
}

function showNotification(result) {
  // Show result notification
  const message = result.is_phishing
    ? `🚫 Threat detected! Confidence: ${(result.confidence * 100).toFixed(0)}%`
    : `✅ Safe website. Confidence: ${(result.confidence * 100).toFixed(0)}%`;

  console.log(message);
  // TODO: Implement toast notification
}

async function updateModel(nextVersion) {
  console.log(`🔄 Updating model to ${nextVersion}...`);
  // TODO: Implement model update
}

async function exportUserData() {
  console.log("📥 Exporting user data...");
  // TODO: Implement data export (encrypted JSON)
}

// ==========================================
// FORMATTING HELPERS
// ==========================================

function formatNumber(num) {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
}

function truncateUrl(url, maxLength = 30) {
  if (!url) return "Unknown";
  if (url.length <= maxLength) return url;
  return url.substring(0, maxLength) + "...";
}

function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);

  if (seconds < 60) return "Just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

function getThreatIcon(threatType, isPhishing) {
  if (!isPhishing) return "✅";

  switch (threatType) {
    case "phishing":
      return "🎣";
    case "malware":
      return "🦠";
    case "cryptojacking":
      return "💎";
    case "ransomware":
      return "🔒";
    case "scam":
      return "💰";
    default:
      return "⚠️";
  }
}

function getCountryFlag(countryCode) {
  // Convert country code to flag emoji
  if (!countryCode || countryCode.length !== 2) return "🌍";

  const codePoints = countryCode
    .toUpperCase()
    .split("")
    .map((char) => 127397 + char.charCodeAt());

  return String.fromCodePoint(...codePoints);
}

// ==========================================
// CLEANUP
// ==========================================

window.addEventListener("unload", () => {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
});
