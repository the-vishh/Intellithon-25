/**
 * 🛡️ PHISHGUARD AI - BACKGROUND SERVICE WORKER
 * ============================================
 *
 * Central hub for extension logic and network monitoring
 *
 * Features:
 * - Network request interception (webRequest API)
 * - C&C server blacklist management
 * - Data exfiltration tracking
 * - Threat intelligence integration
 * - Real-time blocking capabilities
 * - Statistics tracking

 *
 * @author PhishGuard AI Team
 * @version 2.0.0
 * @date October 10, 2025
 */

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
  // ML API endpoint (update with your server)
  ML_API_URL: "http://localhost:5000/predict",

  // Data exfiltration thresholds
  LARGE_POST_THRESHOLD: 100 * 1024, // 100 KB
  CRITICAL_POST_THRESHOLD: 1024 * 1024, // 1 MB

  // C&C server patterns
  CC_SERVER_PATTERNS: [
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+/, // IP:PORT
    /\.onion($|\/)/, // Tor
    /\.i2p($|\/)/, // I2P
    /[a-z0-9]{20,}\.com/, // DGA domains
    /pastebin\.com\/raw/,
    /discord\.com\/api\/webhooks/,
    /bit\.ly|tinyurl\.com|goo\.gl/,
  ],

  // Suspicious ports
  SUSPICIOUS_PORTS: [
    4444, 5555, 6666, 7777, 8888, 9999, 1337, 31337, 6667, 6668, 6669,
  ],

  // Whitelisted domains
  WHITELIST: [
    "google.com",
    "googleapis.com",
    "gstatic.com",
    "microsoft.com",
    "amazon.com",
    "facebook.com",
    "twitter.com",
    "linkedin.com",
    "github.com",
  ],

  // Auto-blocking
  AUTO_BLOCK_CC_SERVERS: true,
  AUTO_BLOCK_LARGE_EXFILTRATION: true,

  DEBUG: true,
};

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const state = {
  // Protection status
  protectionEnabled: true,

  // Statistics
  totalRequests: 0,
  blockedRequests: 0,
  phishingSitesBlocked: 0,

  // Blacklists
  ccServerBlacklist: new Set(),
  domainBlacklist: new Set(),

  // Network monitoring
  suspiciousActivity: [],
  dataExfiltrationEvents: [],

  // Fingerprinting
  fingerprintingDetections: [],

  // Behavioral
  behavioralAlerts: [],

  // Last scan
  lastScanTime: null,
  lastThreatDetected: null,
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function debug(message, data = null) {
  if (CONFIG.DEBUG) {
    console.log(`[PhishGuard BG] ${message}`, data || "");
  }
}

function extractDomain(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hostname;
  } catch (e) {
    return null;
  }
}

function extractPort(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.port || (urlObj.protocol === "https:" ? 443 : 80);
  } catch (e) {
    return null;
  }
}

function isWhitelisted(domain) {
  return CONFIG.WHITELIST.some((whitelisted) => domain.includes(whitelisted));
}

function isBlacklisted(domain) {
  return (
    state.domainBlacklist.has(domain) || state.ccServerBlacklist.has(domain)
  );
}

function addToBlacklist(domain, reason = "Suspicious activity") {
  state.domainBlacklist.add(domain);
  debug(`🚫 Blacklisted: ${domain} (${reason})`);

  // Persist to storage
  chrome.storage.local.set({
    domainBlacklist: Array.from(state.domainBlacklist),
  });
}

// ============================================================================
// NETWORK REQUEST MONITORING
// ============================================================================

/**
 * Monitor all outgoing requests for suspicious activity
 */
chrome.webRequest.onBeforeRequest.addListener(
  function (details) {
    if (!state.protectionEnabled) return {};

    state.totalRequests++;

    const url = details.url;
    const domain = extractDomain(url);

    if (!domain) return {};

    debug(`Request: ${details.method} ${url}`);

    // Check whitelist
    if (isWhitelisted(domain)) {
      return {};
    }

    // Check blacklist
    if (isBlacklisted(domain)) {
      state.blockedRequests++;
      debug(`🚫 BLOCKED (blacklisted): ${url}`);
      return { cancel: true };
    }

    // Check for C&C server patterns
    const ccDetection = detectCCServer(url, domain);
    if (ccDetection.isCC) {
      state.blockedRequests++;
      state.ccServerBlacklist.add(domain);

      showNotification(
        "C&C Server Blocked",
        `Blocked connection to suspicious server: ${domain}\nReason: ${ccDetection.reason}`
      );

      if (CONFIG.AUTO_BLOCK_CC_SERVERS) {
        return { cancel: true };
      }
    }

    // Check for data exfiltration (POST/PUT with large body)
    if (
      (details.method === "POST" || details.method === "PUT") &&
      details.requestBody
    ) {
      const bodySize = estimateRequestBodySize(details.requestBody);

      if (bodySize > CONFIG.LARGE_POST_THRESHOLD) {
        state.dataExfiltrationEvents.push({
          url: url,
          domain: domain,
          size: bodySize,
          timestamp: Date.now(),
        });

        debug(
          `📤 Large POST detected: ${domain} - ${(bodySize / 1024).toFixed(
            2
          )} KB`
        );

        if (
          bodySize > CONFIG.CRITICAL_POST_THRESHOLD &&
          CONFIG.AUTO_BLOCK_LARGE_EXFILTRATION
        ) {
          state.blockedRequests++;
          showNotification(
            "Data Exfiltration Blocked",
            `Blocked large data upload to: ${domain}\nSize: ${(
              bodySize /
              1024 /
              1024
            ).toFixed(2)} MB`
          );
          return { cancel: true };
        }
      }
    }

    return {};
  },
  { urls: ["<all_urls>"] },
  ["requestBody", "blocking"]
);

/**
 * Monitor request headers for suspicious patterns
 */
chrome.webRequest.onBeforeSendHeaders.addListener(
  function (details) {
    if (!state.protectionEnabled) return {};

    const headers = details.requestHeaders || [];

    // Check for suspicious headers
    const suspiciousHeaders = [
      "x-forwarded-for",
      "x-originating-ip",
      "x-real-ip",
    ];

    for (const header of headers) {
      if (suspiciousHeaders.includes(header.name.toLowerCase())) {
        debug(`⚠️ Suspicious header: ${header.name} = ${header.value}`);
      }
    }

    return {};
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders", "blocking"]
);

// ============================================================================
// C&C SERVER DETECTION
// ============================================================================

function detectCCServer(url, domain) {
  // Check URL patterns
  for (const pattern of CONFIG.CC_SERVER_PATTERNS) {
    if (pattern.test(url)) {
      return {
        isCC: true,
        reason: `URL matches known C&C pattern: ${pattern.toString()}`,
      };
    }
  }

  // Check suspicious ports
  const port = extractPort(url);
  if (port && CONFIG.SUSPICIOUS_PORTS.includes(parseInt(port))) {
    return {
      isCC: true,
      reason: `Connection to suspicious port: ${port}`,
    };
  }

  // Check for direct IP connections
  const ipPattern = /^https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;
  if (ipPattern.test(url)) {
    return {
      isCC: true,
      reason: "Direct IP connection (no domain name)",
    };
  }

  return { isCC: false };
}

// ============================================================================
// DATA EXFILTRATION HELPERS
// ============================================================================

function estimateRequestBodySize(requestBody) {
  let size = 0;

  if (requestBody.raw) {
    requestBody.raw.forEach((part) => {
      if (part.bytes) {
        size += part.bytes.byteLength;
      }
    });
  } else if (requestBody.formData) {
    Object.values(requestBody.formData).forEach((values) => {
      values.forEach((value) => {
        size += (value.length || 0) * 2; // UTF-16
      });
    });
  }

  return size;
}

// ============================================================================
// NOTIFICATION SYSTEM
// ============================================================================

function showNotification(title, message) {
  chrome.notifications.create({
    type: "basic",
    iconUrl: "icon128.svg",
    title: title,
    message: message,
    priority: 2,
  });
}

// ============================================================================
// MESSAGE HANDLERS (from content scripts)
// ============================================================================

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  debug(`Message received: ${request.action}`);

  switch (request.action) {
    case "networkThreatDetected":
      handleNetworkThreat(request.report, sender);
      sendResponse({ success: true });
      break;

    case "fingerprintingDetected":
      handleFingerprintingDetection(request.data, sender);
      sendResponse({ success: true });
      break;

    case "behavioralThreatDetected":
      handleBehavioralThreat(request.data, sender);
      sendResponse({ success: true });
      break;

    case "blockConnection":
      blockConnection(request.data);
      sendResponse({ success: true });
      break;

    case "getStatistics":
      sendResponse({ statistics: state });
      break;

    case "toggleProtection":
      state.protectionEnabled = request.enabled;
      debug(`Protection ${state.protectionEnabled ? "ENABLED" : "DISABLED"}`);
      sendResponse({ success: true });
      break;

    case "checkURL":
      checkURLWithML(request.url).then((result) => {
        sendResponse({ result: result });
      });
      return true; // Keep channel open for async response

    default:
      debug(`Unknown action: ${request.action}`);
      sendResponse({ success: false, error: "Unknown action" });
  }

  return true;
});

// ============================================================================
// THREAT HANDLERS
// ============================================================================

function handleNetworkThreat(report, sender) {
  debug(`🚨 Network Threat: ${report.type}`, report);

  state.suspiciousActivity.push({
    type: report.type,
    data: report.data,
    severity: report.severity,
    url: sender.url,
    timestamp: Date.now(),
  });

  state.lastThreatDetected = Date.now();

  // Auto-block if critical
  if (report.severity === "CRITICAL") {
    const domain = extractDomain(report.data.url || sender.url);
    if (domain) {
      addToBlacklist(domain, report.type);
    }
  }
}

function handleFingerprintingDetection(data, sender) {
  debug(`🔬 Fingerprinting: ${data.type}`, data);

  state.fingerprintingDetections.push({
    type: data.type,
    data: data.data,
    severity: data.severity,
    url: sender.url,
    timestamp: Date.now(),
  });
}

function handleBehavioralThreat(data, sender) {
  debug(`🎯 Behavioral Threat: ${data.threat}`, data);

  state.behavioralAlerts.push({
    threat: data.threat,
    details: data.details,
    riskLevel: data.riskLevel,
    url: sender.url,
    timestamp: Date.now(),
  });

  // Block site if HIGH or CRITICAL risk
  if (data.riskLevel === "HIGH" || data.riskLevel === "CRITICAL") {
    const domain = extractDomain(sender.url);
    if (domain) {
      addToBlacklist(domain, `Behavioral threat: ${data.threat}`);

      showNotification(
        "Phishing Site Blocked",
        `Blocked phishing attempt: ${domain}\nThreat: ${data.threat}`
      );

      state.phishingSitesBlocked++;
    }
  }
}

function blockConnection(data) {
  const domain = extractDomain(data.url);
  if (domain) {
    addToBlacklist(domain, "User blocked connection");
    debug(`🚫 User blocked: ${domain}`);
  }
}

// ============================================================================
// ML INTEGRATION
// ============================================================================

async function checkURLWithML(url) {
  try {
    const response = await fetch(CONFIG.ML_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url }),
    });

    if (!response.ok) {
      throw new Error(`ML API error: ${response.status}`);
    }

    const result = await response.json();

    debug(`ML Prediction for ${url}:`, result);

    if (result.is_phishing) {
      state.phishingSitesBlocked++;
      const domain = extractDomain(url);
      if (domain) {
        addToBlacklist(domain, "ML detected phishing");
      }
    }

    return result;
  } catch (error) {
    console.error("ML API error:", error);
    return { error: error.message };
  }
}

// ============================================================================
// STORAGE SYNC
// ============================================================================

// Load state from storage on startup
chrome.storage.local.get(
  ["domainBlacklist", "ccServerBlacklist", "protectionEnabled"],
  (result) => {
    if (result.domainBlacklist) {
      state.domainBlacklist = new Set(result.domainBlacklist);
      debug(`Loaded ${state.domainBlacklist.size} blacklisted domains`);
    }

    if (result.ccServerBlacklist) {
      state.ccServerBlacklist = new Set(result.ccServerBlacklist);
      debug(`Loaded ${state.ccServerBlacklist.size} C&C servers`);
    }

    if (result.protectionEnabled !== undefined) {
      state.protectionEnabled = result.protectionEnabled;
    }

    debug("State loaded from storage");
  }
);

// Periodic save to storage
setInterval(() => {
  chrome.storage.local.set({
    domainBlacklist: Array.from(state.domainBlacklist),
    ccServerBlacklist: Array.from(state.ccServerBlacklist),
    protectionEnabled: state.protectionEnabled,
    statistics: {
      totalRequests: state.totalRequests,
      blockedRequests: state.blockedRequests,
      phishingSitesBlocked: state.phishingSitesBlocked,
    },
  });
}, 60000); // Every minute

// ============================================================================
// INITIALIZATION
// ============================================================================

debug("🛡️ PhishGuard Background Service Worker initialized");
debug("Protection:", state.protectionEnabled ? "ENABLED ✅" : "DISABLED ❌");
debug("Config:", CONFIG);

// Export for debugging
globalThis.PhishGuardBackground = {
  state: state,
  config: CONFIG,
  addToBlacklist: addToBlacklist,
  checkURLWithML: checkURLWithML,
};
