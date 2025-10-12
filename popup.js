// ============================================================================
// POPUP.JS - PHISHING PROTECTOR
// ============================================================================
console.log("🚀 Popup.js loaded successfully!");
console.log("📅 Script loaded at:", new Date().toISOString());

// DOM Elements
const toggleSwitch = document.getElementById("toggle-switch");
const toggleStatus = document.getElementById("toggle-status");
const phishingCount = document.getElementById("phishing-count");
const mainToggleTitle = document.querySelector(".toggle-title");

// Real data from backend
let blockedCount = 0;

// Load real statistics and protection state on popup open
chrome.runtime.sendMessage({ action: "getStatistics" }, (response) => {
  if (response && response.statistics) {
    blockedCount = response.statistics.phishingSitesBlocked || 0;
    phishingCount.textContent = blockedCount;
  }
});

// Load protection enabled state from storage
chrome.storage.local.get(["protectionEnabled"], (result) => {
  const isEnabled = result.protectionEnabled !== false; // Default to true
  toggleSwitch.checked = isEnabled;
  updateToggleState();
});

// Handle toggle switch changes
toggleSwitch.addEventListener("change", function () {
  updateToggleState();

  // Send toggle state to background script
  const isEnabled = toggleSwitch.checked;
  chrome.runtime.sendMessage(
    {
      action: "toggleProtection",
      enabled: isEnabled,
    },
    (response) => {
      console.log(`Protection ${isEnabled ? "ENABLED" : "DISABLED"}`, response);
    }
  );

  // Save to storage
  chrome.storage.local.set({ protectionEnabled: isEnabled });
});

// Update UI based on toggle state
function updateToggleState() {
  const isEnabled = toggleSwitch.checked;
  const toggleText = isEnabled ? "ON" : "OFF";
  const toggleColor = isEnabled ? "#6e42ef" : "#d9534f";

  toggleStatus.textContent = toggleText;
  toggleStatus.style.color = toggleColor;
  mainToggleTitle.innerHTML = `Protection is <span id="toggle-status" style="color: ${toggleColor}">${toggleText}</span>`;
}

// Initialize toggle state
updateToggleState();

// Advanced Controls Toggle
const advancedToggle = document.getElementById("advanced-toggle");
const advancedContent = document.getElementById("advanced-content");
const toggleIcon = document.getElementById("toggle-icon");

advancedToggle.addEventListener("click", function () {
  advancedContent.classList.toggle("expanded");
  toggleIcon.classList.toggle("rotated");
});

// Explanation display functions
function showExplanation(explanation) {
  const explanationSection = document.getElementById("explanation-section");
  const verdictIcon = document.getElementById("verdict-icon");
  const verdictTitle = document.getElementById("verdict-title");
  const verdictMessage = document.getElementById("verdict-message");
  const confidenceFill = document.getElementById("confidence-fill");
  const confidenceText = document.getElementById("confidence-text");

  // Show explanation section
  explanationSection.style.display = "block";

  // Update verdict
  const verdict = explanation.verdict;
  verdictIcon.textContent = verdict.icon;
  verdictTitle.textContent = verdict.message;
  verdictMessage.textContent = `Confidence: ${(
    verdict.confidence * 100
  ).toFixed(1)}%`;

  // Update confidence bar
  const confidencePercent = verdict.confidence * 100;
  confidenceFill.style.width = `${confidencePercent}%`;
  confidenceText.textContent = `Confidence: ${confidencePercent.toFixed(1)}%`;

  // Update verdict colors based on severity
  if (verdict.severity === "CRITICAL" || verdict.severity === "HIGH") {
    confidenceFill.style.background =
      "linear-gradient(90deg, #ef4444 0%, #dc2626 100%)";
    verdictTitle.style.color = "#ef4444";
  } else if (verdict.severity === "MEDIUM") {
    confidenceFill.style.background =
      "linear-gradient(90deg, #f97316 0%, #ea580c 100%)";
    verdictTitle.style.color = "#f97316";
  } else {
    confidenceFill.style.background =
      "linear-gradient(90deg, #22c55e 0%, #16a34a 100%)";
    verdictTitle.style.color = "#22c55e";
  }

  // Show risk score
  if (explanation.risk_breakdown) {
    const riskScoreContainer = document.getElementById("risk-score-container");
    const riskScoreFill = document.getElementById("risk-score-fill");
    const riskScoreText = document.getElementById("risk-score-text");

    riskScoreContainer.style.display = "block";
    const riskScore = explanation.risk_breakdown.score;
    riskScoreFill.style.width = `${riskScore}%`;
    riskScoreText.textContent = `${Math.round(riskScore)}/100`;
  }

  // Show reasons
  if (explanation.reasons && explanation.reasons.length > 0) {
    const topReasonsContainer = document.getElementById(
      "top-reasons-container"
    );
    const reasonsList = document.getElementById("reasons-list");

    topReasonsContainer.style.display = "block";
    reasonsList.innerHTML = "";

    // Show top 5 reasons
    explanation.reasons.slice(0, 5).forEach((reason) => {
      const li = document.createElement("li");
      li.className = reason.risk_level.toLowerCase();
      li.innerHTML = `
                <span class="reason-icon">${reason.icon}</span>
                <span class="reason-text">${reason.text}</span>
            `;
      reasonsList.appendChild(li);
    });
  }

  // Show recommendations
  if (explanation.recommendations && explanation.recommendations.length > 0) {
    const recommendationsContainer = document.getElementById(
      "recommendations-container"
    );
    const recommendationsList = document.getElementById("recommendations-list");

    recommendationsContainer.style.display = "block";
    recommendationsList.innerHTML = "";

    explanation.recommendations.forEach((rec) => {
      const li = document.createElement("li");
      li.className = rec.priority.toLowerCase();
      li.innerHTML = `
                <span class="recommendation-icon">${rec.icon}</span>
                <span class="recommendation-text">${rec.text}</span>
            `;
      recommendationsList.appendChild(li);
    });
  }
}

function hideExplanation() {
  document.getElementById("explanation-section").style.display = "none";
}

// Send URL Button Handler
const sendUrlBtn = document.getElementById("send-url-btn");

if (!sendUrlBtn) {
  console.error("❌ ERROR: send-url-btn not found in DOM!");
} else {
  console.log("✅ Send URL button found and listener attached");
}

// Test function to ensure everything works
async function testAnalysis() {
  console.log("🧪 Testing analysis system...");

  // Test 1: Check if chrome.tabs API works
  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    console.log("✅ chrome.tabs.query works:", tab?.url);
  } catch (e) {
    console.error("❌ chrome.tabs.query failed:", e);
  }

  // Test 2: Check if background script responds
  try {
    chrome.runtime.sendMessage({ action: "getStatistics" }, (response) => {
      if (chrome.runtime.lastError) {
        console.error("❌ Background script error:", chrome.runtime.lastError);
      } else if (response) {
        console.log("✅ Background script responding:", response);
      } else {
        console.warn("⚠️ Background script not responding (no response)");
      }
    });
  } catch (e) {
    console.error("❌ sendMessage failed:", e);
  }
}

// Run test on load
testAnalysis();

sendUrlBtn.addEventListener("click", async function (event) {
  console.log("🔘 Send URL button clicked!", event);
  event.preventDefault(); // Prevent any default behavior

  // Get current tab URL
  try {
    console.log("📡 Querying active tab...");
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });

    console.log("📋 Tab info:", tab);

    if (!tab || !tab.url) {
      console.error("❌ No tab or URL found");
      alert("Error: Unable to get current tab URL");
      return;
    }

    const currentUrl = tab.url;
    console.log("✅ Checking URL:", currentUrl);

    // Show loading state
    console.log("🔄 Setting button to analyzing state...");
    sendUrlBtn.innerHTML = "<span>Analyzing...</span>";
    sendUrlBtn.disabled = true;
    console.log("✅ Button state updated");

    // Send message to background script for analysis
    // Add timeout to reset button if no response
    const timeoutId = setTimeout(() => {
      console.warn("Request timeout - resetting button");
      sendUrlBtn.innerHTML = "<span>Send URL</span>";
      sendUrlBtn.disabled = false;
      alert(
        "Request timeout. The backend may not be responding.\n\nTip: Check if background.js is loaded and ML API is running."
      );
    }, 10000); // 10 second timeout

    chrome.runtime.sendMessage(
      {
        action: "checkURL",
        url: currentUrl,
      },
      (response) => {
        // Clear timeout
        clearTimeout(timeoutId);

        // Reset button state
        sendUrlBtn.innerHTML = "<span>Send URL</span>";
        sendUrlBtn.disabled = false;

        console.log("Received response:", response);

        // Check for chrome runtime errors
        if (chrome.runtime.lastError) {
          console.error("Chrome runtime error:", chrome.runtime.lastError);
          alert(`Error: ${chrome.runtime.lastError.message}`);
          return;
        }

        // Check if response is undefined (no listener)
        if (!response) {
          console.error(
            "No response from background script - listener may not be working"
          );
          alert(
            "Extension Error: No response from background script.\n\nPossible causes:\n1. Background script not loaded\n2. Message listener not registered\n3. Action name mismatch"
          );
          return;
        }

        if (response && response.result) {
          // Check if ML API returned an error
          if (response.result.error) {
            console.error("ML API error:", response.result.error);
            alert(
              `Error: ML API is not available.\n\n${response.result.error}\n\nPlease ensure:\n1. Redis is running (port 6379)\n2. Python ML Service is running (port 8000)\n3. Rust API Gateway is running (port 8080)`
            );
            return;
          }

          // Convert ML API result to explanation format
          const mlResult = response.result;
          const explanation = {
            verdict: {
              message: mlResult.is_phishing
                ? "⚠️ WARNING: This site may be a phishing attempt!"
                : "✅ This site appears to be legitimate",
              severity: mlResult.is_phishing ? "HIGH" : "SAFE",
              confidence: mlResult.confidence || 0.85,
              icon: mlResult.is_phishing ? "⚠️" : "✅",
              action: mlResult.is_phishing ? "BLOCK" : "ALLOW",
            },
            risk_breakdown: {
              score: mlResult.is_phishing ? 85 : 15,
              breakdown: {
                CRITICAL: mlResult.is_phishing ? 1 : 0,
                HIGH: mlResult.is_phishing ? 1 : 0,
                MEDIUM: 0,
                LOW: 1,
                INFO: 2,
              },
            },
            reasons: mlResult.reasons || [
              {
                icon: mlResult.is_phishing ? "⚠️" : "✅",
                text: `ML Model Detection: ${
                  mlResult.is_phishing ? "Phishing detected" : "Safe site"
                }`,
                risk_level: mlResult.is_phishing ? "HIGH" : "INFO",
                importance: 0.9,
              },
            ],
            recommendations: mlResult.is_phishing
              ? [
                  {
                    icon: "🛑",
                    text: "Do not enter any personal information on this site",
                    priority: "CRITICAL",
                  },
                  {
                    icon: "🔒",
                    text: "Leave this site immediately and report it",
                    priority: "HIGH",
                  },
                ]
              : [
                  {
                    icon: "✅",
                    text: "This site appears safe, but always verify URLs before entering sensitive data",
                    priority: "INFO",
                  },
                ],
          };

          console.log("Converted ML result to explanation:", explanation);
          showExplanation(explanation);
        } else if (response && response.error) {
          // Show error message
          console.error("Backend error:", response.error);
          alert(
            `Analysis Error: ${response.error}\n\nPlease check that all services are running:\n1. Redis (port 6379)\n2. Python ML (port 8000)\n3. Rust API (port 8080)`
          );
        } else {
          // No response from background script
          console.error("No response from background script");
          alert(
            "Extension Error: Background script not responding.\n\nPlease try:\n1. Reload the extension\n2. Check browser console for errors"
          );
        }
      }
    );
  } catch (error) {
    console.error("Error in Send URL handler:", error);
    sendUrlBtn.innerHTML = "<span>Send URL</span>";
    sendUrlBtn.disabled = false;
    alert("Error: " + error.message);
  }
});

// More Data Button Handler
const moreDataBtn = document.getElementById("more-data-btn");
moreDataBtn.addEventListener("click", function () {
  // Open the index (1).html file from the extension
  const dashboardUrl = chrome.runtime.getURL("index (1).html");
  chrome.tabs.create({ url: dashboardUrl });
});

// Add hover effects for buttons
document
  .querySelectorAll(".control-button, .footer-button")
  .forEach((button) => {
    button.addEventListener("mouseover", function () {
      this.style.background = "rgba(255, 255, 255, 0.1)";
    });

    button.addEventListener("mouseout", function () {
      this.style.background = button.classList.contains("control-button")
        ? "rgba(255, 255, 255, 0.05)"
        : "transparent";
    });
  });
