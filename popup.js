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

    // TODO: Send URL to backend API for phishing detection
    console.log("Checking URL:", currentUrl);

    // Placeholder: Show alert (replace with actual API call)
    alert(`Checking URL: ${currentUrl}\n\n(Backend integration pending)`);

    // Example API call structure:
    // const response = await fetch('YOUR_BACKEND_API/check-url', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ url: currentUrl })
    // });
    // const result = await response.json();
  } catch (error) {
    console.error("Error getting current tab:", error);
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
