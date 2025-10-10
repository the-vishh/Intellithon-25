/**
 * 🌐 PHISHGUARD AI - NETWORK TRAFFIC ANALYSIS
 * ===========================================
 *
 * Advanced network monitoring and threat detection
 *
 * Features:
 * - C&C (Command & Control) server detection
 * - Data exfiltration monitoring (POST size analysis)
 * - WebSocket connection tracking
 * - DNS over HTTPS (DoH) detection
 * - Cross-origin request monitoring
 * - Suspicious header analysis
 * - Network-based phishing detection
 * - Real-time blocking capabilities

 *
 * @author PhishGuard AI Team
 * @version 2.0.0
 * @date October 10, 2025
 */

(function () {
  "use strict";

  // ============================================================================
  // CONFIGURATION
  // ============================================================================

  const CONFIG = {
    // Data exfiltration thresholds
    LARGE_POST_THRESHOLD: 100 * 1024, // 100 KB (suspicious data upload)
    CRITICAL_POST_THRESHOLD: 1024 * 1024, // 1 MB (highly suspicious)
    MAX_REQUESTS_PER_MINUTE: 100, // Rate limit per domain

    // C&C server indicators
    CC_SERVER_PATTERNS: [
      /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+/, // IP:PORT (e.g., 192.168.1.1:8080)
      /\.onion($|\/)/, // Tor hidden services
      /\.i2p($|\/)/, // I2P network
      /[a-z0-9]{20,}\.com/, // Random domain names (DGA)
      /pastebin\.com\/raw/, // Common C&C host
      /discord\.com\/api\/webhooks/, // Discord webhooks (often abused)
      /bit\.ly|tinyurl\.com|goo\.gl/, // URL shorteners (hide destination)
    ],

    // Suspicious ports (common C&C)
    SUSPICIOUS_PORTS: [
      4444,
      5555,
      6666,
      7777,
      8888,
      9999, // Common backdoor ports
      1337,
      31337, // Leet speak ports
      6667,
      6668,
      6669, // IRC ports
      8080,
      8443,
      8888, // Alternative HTTP(S)
    ],

    // DoH providers (can bypass DNS monitoring)
    DOH_PROVIDERS: [
      "dns.google",
      "cloudflare-dns.com",
      "1.1.1.1",
      "8.8.8.8",
      "dns.quad9.net",
      "doh.opendns.com",
    ],

    // WebSocket monitoring
    WEBSOCKET_THRESHOLD: 10, // > 10 WebSocket connections = suspicious

    // Suspicious headers
    SUSPICIOUS_HEADERS: [
      "x-forwarded-for", // IP spoofing
      "x-originating-ip",
      "x-real-ip",
      "x-requested-with: xmlhttprequest", // AJAX (often for credential theft)
    ],

    // Whitelisted domains (don't monitor)
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

    // Monitoring toggles
    MONITOR_POST_SIZE: true,
    MONITOR_CC_SERVERS: true,
    MONITOR_WEBSOCKETS: true,
    MONITOR_DOH: true,
    MONITOR_HEADERS: true,
    MONITOR_CROSS_ORIGIN: true,
    BLOCK_SUSPICIOUS: false, // Set true for auto-blocking

    // Debug mode
    DEBUG: true,
  };

  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const networkState = {
    // Request tracking
    requestCount: {}, // domain -> count
    lastRequestTime: {}, // domain -> timestamp

    // Data exfiltration
    largePostCount: 0,
    totalBytesExfiltrated: 0,
    suspiciousUploads: [],

    // C&C detection
    ccServerDetections: [],

    // WebSocket tracking
    webSocketConnections: 0,
    activeWebSockets: [],

    // DoH detection
    dohRequests: 0,

    // Cross-origin tracking
    crossOriginRequests: 0,
    crossOriginDomains: new Set(),

    // Suspicious activity score (0-100)
    networkThreatScore: 0,

    // Timestamps
    monitoringStartTime: Date.now(),
    lastThreatDetected: null,
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  function debug(message, data = null) {
    if (CONFIG.DEBUG) {
      console.log(`[PhishGuard Network] ${message}`, data || "");
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

  function updateThreatScore() {
    let score = 0;

    // Data exfiltration (0-30 points)
    if (networkState.largePostCount > 0) {
      score += Math.min(30, networkState.largePostCount * 10);
    }

    // C&C detections (0-30 points)
    if (networkState.ccServerDetections.length > 0) {
      score += Math.min(30, networkState.ccServerDetections.length * 15);
    }

    // WebSocket abuse (0-20 points)
    if (networkState.webSocketConnections > CONFIG.WEBSOCKET_THRESHOLD) {
      score += 20;
    }

    // DoH usage (0-10 points)
    if (networkState.dohRequests > 5) {
      score += 10;
    }

    // Cross-origin abuse (0-10 points)
    if (networkState.crossOriginRequests > 20) {
      score += 10;
    }

    networkState.networkThreatScore = Math.min(100, score);
  }

  function reportThreat(type, data, severity = "MEDIUM") {
    networkState.lastThreatDetected = Date.now();
    updateThreatScore();

    const report = {
      type: type,
      data: data,
      severity: severity,
      threatScore: networkState.networkThreatScore,
      timestamp: Date.now(),
    };

    debug(
      `🚨 Network Threat: ${type} (Score: ${networkState.networkThreatScore}/100)`,
      report
    );

    chrome.runtime.sendMessage(
      {
        action: "networkThreatDetected",
        report: report,
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Message send failed:", chrome.runtime.lastError);
        }
      }
    );

    // Show warning for critical threats
    if (severity === "CRITICAL" || networkState.networkThreatScore > 70) {
      showNetworkWarning(type, data);
    }
  }

  function showNetworkWarning(type, data) {
    if (document.getElementById("phishguard-network-warning")) {
      return;
    }

    const warningMessages = {
      CC_SERVER_DETECTED:
        "⚠️ Connection to suspicious Command & Control server detected!",
      DATA_EXFILTRATION: "📤 Large data upload detected - Possible data theft!",
      WEBSOCKET_ABUSE: "🔌 Excessive WebSocket connections detected!",
      DOH_USAGE: "🔒 Encrypted DNS detected - May bypass monitoring!",
      CROSS_ORIGIN_ABUSE: "🌐 Suspicious cross-origin requests detected!",
    };

    const message =
      warningMessages[type] || "⚠️ Suspicious network activity detected!";

    const banner = document.createElement("div");
    banner.id = "phishguard-network-warning";
    banner.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            padding: 16px 24px;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideDownNetwork 0.3s ease-out;
        `;

    banner.innerHTML = `
            <style>
                @keyframes slideDownNetwork {
                    from { transform: translateY(-100%); }
                    to { transform: translateY(0); }
                }
            </style>
            <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 32px;">🌐</div>
                    <div>
                        <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">
                            Network Threat Detected
                        </div>
                        <div style="font-size: 13px; opacity: 0.9;">
                            ${message} Threat Score: ${networkState.networkThreatScore}/100
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 12px;">
                    <button id="phishguard-network-block" style="
                        background: rgba(255,255,255,0.3);
                        border: none;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='rgba(255,255,255,0.4)'" onmouseout="this.style.background='rgba(255,255,255,0.3)'">
                        Block Connection
                    </button>
                    <button id="phishguard-network-dismiss" style="
                        background: rgba(255,255,255,0.15);
                        border: none;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='rgba(255,255,255,0.25)'" onmouseout="this.style.background='rgba(255,255,255,0.15)'">
                        Dismiss
                    </button>
                </div>
            </div>
        `;

    document.body.appendChild(banner);

    document.getElementById("phishguard-network-block").onclick = () => {
      // Block the connection
      chrome.runtime.sendMessage({
        action: "blockConnection",
        data: data,
      });
      banner.remove();
    };

    document.getElementById("phishguard-network-dismiss").onclick = () => {
      banner.remove();
    };

    // Auto-dismiss after 15 seconds
    setTimeout(() => {
      if (banner.parentNode) {
        banner.remove();
      }
    }, 15000);
  }

  // ============================================================================
  // 1. DATA EXFILTRATION MONITORING
  // ============================================================================

  function monitorDataExfiltration(details) {
    if (!CONFIG.MONITOR_POST_SIZE) return;

    // Only monitor POST/PUT requests
    if (details.method !== "POST" && details.method !== "PUT") {
      return;
    }

    const domain = extractDomain(details.url);
    if (!domain || isWhitelisted(domain)) return;

    // Estimate request body size
    let bodySize = 0;
    if (details.requestBody) {
      if (details.requestBody.raw) {
        details.requestBody.raw.forEach((part) => {
          if (part.bytes) {
            bodySize += part.bytes.byteLength;
          }
        });
      } else if (details.requestBody.formData) {
        // Estimate form data size
        Object.values(details.requestBody.formData).forEach((values) => {
          values.forEach((value) => {
            bodySize += (value.length || 0) * 2; // UTF-16
          });
        });
      }
    }

    debug(`POST request to ${domain}: ${bodySize} bytes`);

    if (bodySize > CONFIG.LARGE_POST_THRESHOLD) {
      networkState.largePostCount++;
      networkState.totalBytesExfiltrated += bodySize;

      networkState.suspiciousUploads.push({
        url: details.url,
        size: bodySize,
        timestamp: Date.now(),
      });

      const severity =
        bodySize > CONFIG.CRITICAL_POST_THRESHOLD ? "CRITICAL" : "HIGH";

      reportThreat(
        "DATA_EXFILTRATION",
        {
          url: details.url,
          domain: domain,
          size: bodySize,
          sizeFormatted: `${(bodySize / 1024).toFixed(2)} KB`,
          totalExfiltrated: `${(
            networkState.totalBytesExfiltrated /
            1024 /
            1024
          ).toFixed(2)} MB`,
        },
        severity
      );

      if (CONFIG.BLOCK_SUSPICIOUS && severity === "CRITICAL") {
        return { cancel: true };
      }
    }
  }

  // ============================================================================
  // 2. C&C SERVER DETECTION
  // ============================================================================

  function detectCCServer(details) {
    if (!CONFIG.MONITOR_CC_SERVERS) return;

    const url = details.url;
    const domain = extractDomain(url);
    const port = extractPort(url);

    if (!domain || isWhitelisted(domain)) return;

    // Check URL patterns
    for (const pattern of CONFIG.CC_SERVER_PATTERNS) {
      if (pattern.test(url)) {
        networkState.ccServerDetections.push({
          url: url,
          pattern: pattern.toString(),
          timestamp: Date.now(),
        });

        reportThreat(
          "CC_SERVER_DETECTED",
          {
            url: url,
            domain: domain,
            pattern: pattern.toString(),
            reason: "URL matches known C&C server pattern",
          },
          "CRITICAL"
        );

        if (CONFIG.BLOCK_SUSPICIOUS) {
          return { cancel: true };
        }
      }
    }

    // Check suspicious ports
    if (port && CONFIG.SUSPICIOUS_PORTS.includes(parseInt(port))) {
      reportThreat(
        "CC_SERVER_DETECTED",
        {
          url: url,
          domain: domain,
          port: port,
          reason: "Connection to suspicious port",
        },
        "HIGH"
      );

      if (CONFIG.BLOCK_SUSPICIOUS) {
        return { cancel: true };
      }
    }

    // Check for IP addresses (legitimate sites rarely use IPs)
    const ipPattern = /^https?:\/\/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/;
    if (ipPattern.test(url) && !isWhitelisted(domain)) {
      reportThreat(
        "CC_SERVER_DETECTED",
        {
          url: url,
          reason: "Direct IP connection (no domain name)",
        },
        "MEDIUM"
      );
    }
  }

  // ============================================================================
  // 3. DNS OVER HTTPS (DoH) DETECTION
  // ============================================================================

  function detectDoH(details) {
    if (!CONFIG.MONITOR_DOH) return;

    const domain = extractDomain(details.url);
    const url = details.url;

    if (!domain) return;

    // Check if request is to known DoH provider
    for (const provider of CONFIG.DOH_PROVIDERS) {
      if (domain.includes(provider) || url.includes("/dns-query")) {
        networkState.dohRequests++;

        if (networkState.dohRequests > 5) {
          reportThreat(
            "DOH_USAGE",
            {
              provider: provider,
              count: networkState.dohRequests,
              reason: "Encrypted DNS may bypass monitoring",
            },
            "MEDIUM"
          );
        }

        break;
      }
    }
  }

  // ============================================================================
  // 4. CROSS-ORIGIN REQUEST MONITORING
  // ============================================================================

  function monitorCrossOrigin(details) {
    if (!CONFIG.MONITOR_CROSS_ORIGIN) return;

    const initiator = details.initiator || details.documentUrl;
    if (!initiator) return;

    const requestDomain = extractDomain(details.url);
    const originDomain = extractDomain(initiator);

    if (!requestDomain || !originDomain) return;

    // Check if domains differ
    if (requestDomain !== originDomain && !isWhitelisted(requestDomain)) {
      networkState.crossOriginRequests++;
      networkState.crossOriginDomains.add(requestDomain);

      debug(`Cross-origin request: ${originDomain} → ${requestDomain}`);

      if (networkState.crossOriginRequests > 20) {
        reportThreat(
          "CROSS_ORIGIN_ABUSE",
          {
            originDomain: originDomain,
            requestDomain: requestDomain,
            totalRequests: networkState.crossOriginRequests,
            uniqueDomains: networkState.crossOriginDomains.size,
          },
          "MEDIUM"
        );
      }
    }
  }

  // ============================================================================
  // 5. SUSPICIOUS HEADER ANALYSIS
  // ============================================================================

  function analyzeSuspiciousHeaders(details) {
    if (!CONFIG.MONITOR_HEADERS) return;

    if (!details.requestHeaders) return;

    const headers = details.requestHeaders.map(
      (h) => `${h.name.toLowerCase()}: ${h.value.toLowerCase()}`
    );

    for (const suspiciousHeader of CONFIG.SUSPICIOUS_HEADERS) {
      if (headers.some((h) => h.includes(suspiciousHeader))) {
        reportThreat(
          "SUSPICIOUS_HEADER",
          {
            url: details.url,
            header: suspiciousHeader,
            reason: "Request contains suspicious header",
          },
          "LOW"
        );
      }
    }
  }

  // ============================================================================
  // 6. RATE LIMITING PER DOMAIN
  // ============================================================================

  function checkRateLimit(details) {
    const domain = extractDomain(details.url);
    if (!domain || isWhitelisted(domain)) return;

    const now = Date.now();
    const minute = 60 * 1000;

    // Initialize tracking
    if (!networkState.requestCount[domain]) {
      networkState.requestCount[domain] = 0;
      networkState.lastRequestTime[domain] = now;
    }

    // Reset counter every minute
    if (now - networkState.lastRequestTime[domain] > minute) {
      networkState.requestCount[domain] = 0;
      networkState.lastRequestTime[domain] = now;
    }

    networkState.requestCount[domain]++;

    if (networkState.requestCount[domain] > CONFIG.MAX_REQUESTS_PER_MINUTE) {
      reportThreat(
        "RATE_LIMIT_EXCEEDED",
        {
          domain: domain,
          requestCount: networkState.requestCount[domain],
          threshold: CONFIG.MAX_REQUESTS_PER_MINUTE,
          reason: "Excessive requests to single domain",
        },
        "MEDIUM"
      );
    }
  }

  // ============================================================================
  // 7. WEBSOCKET CONNECTION TRACKING
  // ============================================================================

  function monitorWebSockets() {
    if (!CONFIG.MONITOR_WEBSOCKETS) return;

    // Hook WebSocket constructor
    const OriginalWebSocket = window.WebSocket;

    window.WebSocket = function (url, protocols) {
      networkState.webSocketConnections++;
      networkState.activeWebSockets.push({
        url: url,
        timestamp: Date.now(),
      });

      debug(
        `WebSocket connection opened: ${url} (count: ${networkState.webSocketConnections})`
      );

      if (networkState.webSocketConnections > CONFIG.WEBSOCKET_THRESHOLD) {
        reportThreat(
          "WEBSOCKET_ABUSE",
          {
            url: url,
            totalConnections: networkState.webSocketConnections,
            threshold: CONFIG.WEBSOCKET_THRESHOLD,
          },
          "HIGH"
        );
      }

      const ws = new OriginalWebSocket(url, protocols);

      // Monitor messages
      const originalSend = ws.send;
      ws.send = function (data) {
        debug(`WebSocket send: ${data.length || 0} bytes`);

        // Check for large data sends
        if (data.length > CONFIG.LARGE_POST_THRESHOLD) {
          reportThreat(
            "WEBSOCKET_DATA_EXFILTRATION",
            {
              url: url,
              size: data.length,
            },
            "HIGH"
          );
        }

        return originalSend.apply(this, arguments);
      };

      return ws;
    };

    window.WebSocket.prototype = OriginalWebSocket.prototype;
  }

  // ============================================================================
  // WEBQUEST LISTENER (Background Script Integration)
  // ============================================================================

  // Note: This runs in the background script context
  function setupWebRequestListeners() {
    // Monitor all requests
    chrome.webRequest.onBeforeRequest.addListener(
      (details) => {
        debug(`Request: ${details.method} ${details.url}`);

        // Run all checks
        monitorDataExfiltration(details);
        detectCCServer(details);
        detectDoH(details);
        monitorCrossOrigin(details);
        checkRateLimit(details);

        return {}; // Allow request (unless BLOCK_SUSPICIOUS is true)
      },
      { urls: ["<all_urls>"] },
      ["requestBody", "blocking"]
    );

    // Monitor request headers
    chrome.webRequest.onBeforeSendHeaders.addListener(
      (details) => {
        analyzeSuspiciousHeaders(details);
        return {};
      },
      { urls: ["<all_urls>"] },
      ["requestHeaders", "blocking"]
    );
  }

  // ============================================================================
  // PERIODIC REPORTING
  // ============================================================================

  function startPeriodicReporting() {
    setInterval(() => {
      updateThreatScore();

      chrome.runtime.sendMessage({
        action: "networkSummary",
        state: networkState,
        uptime: Date.now() - networkState.monitoringStartTime,
      });

      debug(
        `📊 Network Summary - Threat Score: ${networkState.networkThreatScore}/100`
      );
    }, 30000); // Every 30 seconds
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  function initialize() {
    debug("🌐 PhishGuard Network Monitor initialized");
    debug("Config:", CONFIG);

    try {
      // WebSocket monitoring runs in content script
      monitorWebSockets();
      startPeriodicReporting();

      // WebRequest listeners run in background script
      // (Add setupWebRequestListeners() to background.js)

      debug("✅ Network monitoring active");
    } catch (error) {
      console.error("[PhishGuard Network] Initialization error:", error);
    }
  }

  // Start immediately
  initialize();

  // ============================================================================
  // MESSAGE HANDLER
  // ============================================================================

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getNetworkState") {
      sendResponse({ state: networkState });
    } else if (request.action === "resetNetworkState") {
      Object.keys(networkState).forEach((key) => {
        if (typeof networkState[key] === "number") {
          networkState[key] = 0;
        } else if (networkState[key] instanceof Set) {
          networkState[key].clear();
        } else if (Array.isArray(networkState[key])) {
          networkState[key] = [];
        } else if (typeof networkState[key] === "object") {
          networkState[key] = {};
        }
      });
      networkState.monitoringStartTime = Date.now();
      sendResponse({ success: true });
    }

    return true;
  });

  // ============================================================================
  // EXPORT (for testing)
  // ============================================================================

  window.PhishGuardNetworkMonitor = {
    state: networkState,
    config: CONFIG,
    setupWebRequestListeners: setupWebRequestListeners,
  };
})();
