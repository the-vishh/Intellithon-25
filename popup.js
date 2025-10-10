// DOM Elements
const toggleSwitch = document.getElementById("toggle-switch");
const toggleStatus = document.getElementById("toggle-status");
const phishingCount = document.getElementById("phishing-count");
const mainToggleTitle = document.querySelector(".toggle-title");

// Placeholder data (to be replaced with actual data from backend)
let blockedCount = 0;
phishingCount.textContent = blockedCount;

// Handle toggle switch changes
toggleSwitch.addEventListener("change", function () {
  updateToggleState();
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
sendUrlBtn.addEventListener("click", async function () {
  // Get current tab URL
  try {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true,
    });
    const currentUrl = tab.url;

    console.log("Checking URL:", currentUrl);

    // Show loading state
    sendUrlBtn.textContent = "Analyzing...";
    sendUrlBtn.disabled = true;

    // Send message to background script for analysis
    chrome.runtime.sendMessage(
      {
        action: "analyzeUrl",
        url: currentUrl,
      },
      (response) => {
        // Reset button
        sendUrlBtn.innerHTML = "<span>Send URL</span>";
        sendUrlBtn.disabled = false;

        if (response && response.explanation) {
          // Show explanation
          showExplanation(response.explanation);
        } else if (response && response.error) {
          // Show error
          alert(`Error: ${response.error}`);
        } else {
          // Mock explanation for testing (remove in production)
          const mockExplanation = {
            verdict: {
              message:
                "✅ This site appears to be legitimate based on our analysis",
              severity: "SAFE",
              confidence: 0.92,
              icon: "✅",
              action: "ALLOW",
            },
            risk_breakdown: {
              score: 15,
              breakdown: {
                CRITICAL: 0,
                HIGH: 0,
                MEDIUM: 1,
                LOW: 2,
                INFO: 3,
              },
            },
            reasons: [
              {
                icon: "🔒",
                text: "Valid SSL certificate present",
                risk_level: "INFO",
                importance: 0.25,
              },
              {
                icon: "📅",
                text: "Established domain (1547 days old)",
                risk_level: "INFO",
                importance: 0.22,
              },
              {
                icon: "🔐",
                text: "Site uses encrypted HTTPS",
                risk_level: "INFO",
                importance: 0.18,
              },
            ],
            recommendations: [
              {
                icon: "✅",
                text: "This site appears safe, but always verify URLs before entering sensitive data",
                priority: "INFO",
              },
              {
                icon: "🔒",
                text: "Check for the padlock icon to ensure secure connection",
                priority: "INFO",
              },
            ],
          };
          showExplanation(mockExplanation);
        }
      }
    );
  } catch (error) {
    console.error("Error getting current tab:", error);
    sendUrlBtn.innerHTML = "<span>Send URL</span>";
    sendUrlBtn.disabled = false;
    alert("Error: Unable to get current URL");
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
