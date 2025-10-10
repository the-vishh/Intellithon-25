/**
 * 🛡️ PHISHGUARD AI - CONTENT SCRIPT
 * ==================================
 *
 * Real-time behavioral monitoring and phishing detection
 *
 * Features:
 * - Immediate password request detection
 * - Rapid redirect monitoring
 * - Form submission analysis
 * - Cross-origin form detection
 * - Suspicious timing analysis
 * - User interaction profiling

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
    // Timing thresholds (milliseconds)
    IMMEDIATE_PASSWORD_THRESHOLD: 2000, // < 2 seconds = suspicious
    RAPID_REDIRECT_THRESHOLD: 1000, // < 1 second between redirects
    RAPID_REDIRECT_COUNT: 3, // 3+ rapid redirects = very suspicious

    // Form analysis
    CROSS_ORIGIN_FORMS_ALLOWED: false, // Block cross-origin credential forms
    SUSPICIOUS_PARAM_KEYWORDS: [
      "redirect",
      "return",
      "next",
      "continue",
      "goto",
      "url",
      "link",
    ],

    // Input focus tracking
    TRACK_INPUT_FOCUS: true,
    SUSPICIOUS_FOCUS_PATTERNS: ["password", "credit-card", "cvv"],

    // Clipboard monitoring
    TRACK_CLIPBOARD_ACCESS: true,

    // Debug mode
    DEBUG: true,
  };

  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const state = {
    pageLoadTime: performance.now(),
    firstPasswordPrompt: null,
    redirectCount: 0,
    lastRedirectTime: Date.now(),
    formSubmissions: [],
    inputFocusEvents: [],
    clipboardAccessCount: 0,
    suspiciousActivities: [],
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  /**
   * Log debug messages
   */
  function debug(message, data = null) {
    if (CONFIG.DEBUG) {
      console.log(`[PhishGuard Content] ${message}`, data || "");
    }
  }

  /**
   * Send message to background script
   */
  function reportToBackground(action, data) {
    chrome.runtime.sendMessage(
      {
        action: action,
        data: data,
        url: window.location.href,
        timestamp: Date.now(),
      },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error("Message sending failed:", chrome.runtime.lastError);
        } else {
          debug(`Reported ${action}:`, response);
        }
      }
    );
  }

  /**
   * Report suspicious activity
   */
  function reportSuspiciousActivity(type, data, riskLevel = "MEDIUM") {
    const activity = {
      type: type,
      data: data,
      riskLevel: riskLevel,
      url: window.location.href,
      timestamp: Date.now(),
    };

    state.suspiciousActivities.push(activity);

    debug(`🚨 Suspicious Activity: ${type}`, activity);

    reportToBackground("suspiciousActivity", activity);

    // Show warning for HIGH/CRITICAL risks
    if (riskLevel === "HIGH" || riskLevel === "CRITICAL") {
      showInPageWarning(type, data);
    }
  }

  /**
   * Show in-page warning overlay
   */
  function showInPageWarning(type, data) {
    // Prevent multiple overlays
    if (document.getElementById("phishguard-warning-overlay")) {
      return;
    }

    const warningMessages = {
      IMMEDIATE_PASSWORD_REQUEST: {
        title: "⚠️ Immediate Password Request Detected",
        message:
          "This page is asking for your password unusually quickly. This is a common phishing technique.",
        recommendation:
          "Verify the website URL carefully before entering any credentials.",
      },
      RAPID_REDIRECTS: {
        title: "🔄 Rapid Redirects Detected",
        message: `This page has redirected ${data.count} times in rapid succession. This is suspicious behavior.`,
        recommendation:
          "Close this tab and avoid entering any personal information.",
      },
      EXTERNAL_FORM_SUBMIT: {
        title: "🚫 Cross-Origin Form Submission",
        message: `This form is submitting your data to a different website: ${data.formOrigin}`,
        recommendation:
          "This is highly suspicious. Do not submit credentials to external sites.",
      },
      CLIPBOARD_ABUSE: {
        title: "📋 Excessive Clipboard Access",
        message: "This page is trying to access your clipboard repeatedly.",
        recommendation:
          "Your clipboard may contain sensitive information. Be cautious.",
      },
    };

    const warningInfo = warningMessages[type] || {
      title: "⚠️ Suspicious Activity Detected",
      message: "This page is exhibiting suspicious behavior.",
      recommendation: "Proceed with caution.",
    };

    const overlay = document.createElement("div");
    overlay.id = "phishguard-warning-overlay";
    overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85);
            z-index: 999999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            animation: fadeIn 0.3s ease-in;
        `;

    overlay.innerHTML = `
            <style>
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideIn {
                    from { transform: translateY(-20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
                #phishguard-warning-box {
                    animation: slideIn 0.4s ease-out;
                }
            </style>
            <div id="phishguard-warning-box" style="
                background: white;
                padding: 40px;
                border-radius: 16px;
                max-width: 600px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            ">
                <div style="text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 64px; margin-bottom: 10px;">${
                      warningInfo.title.split(" ")[0]
                    }</div>
                    <h2 style="margin: 0; color: #dc2626; font-size: 24px;">${warningInfo.title.substring(
                      2
                    )}</h2>
                </div>

                <div style="background: #fef2f2; border-left: 4px solid #dc2626; padding: 16px; margin-bottom: 20px; border-radius: 4px;">
                    <p style="margin: 0; color: #991b1b; font-size: 16px; line-height: 1.5;">
                        ${warningInfo.message}
                    </p>
                </div>

                <div style="background: #f0fdf4; border-left: 4px solid #16a34a; padding: 16px; margin-bottom: 30px; border-radius: 4px;">
                    <p style="margin: 0; color: #166534; font-size: 14px; line-height: 1.5;">
                        <strong>💡 Recommendation:</strong> ${
                          warningInfo.recommendation
                        }
                    </p>
                </div>

                <div style="display: flex; gap: 12px; justify-content: center;">
                    <button id="phishguard-go-back" style="
                        padding: 12px 24px;
                        background: #dc2626;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='#b91c1c'" onmouseout="this.style.background='#dc2626'">
                        🛡️ Go Back (Recommended)
                    </button>
                    <button id="phishguard-continue" style="
                        padding: 12px 24px;
                        background: #6b7280;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: background 0.2s;
                    " onmouseover="this.style.background='#4b5563'" onmouseout="this.style.background='#6b7280'">
                        Continue Anyway
                    </button>
                </div>

                <div style="margin-top: 20px; text-align: center; font-size: 12px; color: #6b7280;">
                    Protected by PhishGuard AI
                </div>
            </div>
        `;

    document.body.appendChild(overlay);

    // Button handlers
    document.getElementById("phishguard-go-back").onclick = () => {
      overlay.remove();
      reportToBackground("userAction", {
        action: "went_back",
        alertType: type,
      });
      window.history.back();
    };

    document.getElementById("phishguard-continue").onclick = () => {
      overlay.remove();
      reportToBackground("userAction", {
        action: "continued_anyway",
        alertType: type,
      });
    };
  }

  // ============================================================================
  // 1. PASSWORD REQUEST TIMING ANALYSIS
  // ============================================================================

  /**
   * Monitor for immediate password requests (< 2 seconds after page load)
   * Phishing sites often rush users to enter credentials
   */
  function monitorPasswordRequests() {
    // Check on DOM ready
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", checkPasswordInputs);
    } else {
      checkPasswordInputs();
    }

    // Also observe DOM changes (dynamically added forms)
    const observer = new MutationObserver((mutations) => {
      for (const mutation of mutations) {
        if (mutation.addedNodes.length > 0) {
          checkPasswordInputs();
        }
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  function checkPasswordInputs() {
    const passwordInputs = document.querySelectorAll('input[type="password"]');

    if (passwordInputs.length > 0 && state.firstPasswordPrompt === null) {
      state.firstPasswordPrompt = performance.now();
      const timeDelta = state.firstPasswordPrompt - state.pageLoadTime;

      debug(`Password input detected after ${timeDelta}ms`);

      if (timeDelta < CONFIG.IMMEDIATE_PASSWORD_THRESHOLD) {
        reportSuspiciousActivity(
          "IMMEDIATE_PASSWORD_REQUEST",
          {
            timeDelta: timeDelta,
            passwordFieldCount: passwordInputs.length,
            pageUrl: window.location.href,
          },
          "HIGH"
        );
      }
    }
  }

  // ============================================================================
  // 2. RAPID REDIRECT DETECTION
  // ============================================================================

  /**
   * Monitor for rapid redirects (common phishing technique to confuse users)
   */
  function monitorRedirects() {
    window.addEventListener("beforeunload", () => {
      const currentTime = Date.now();
      const timeSinceLastRedirect = currentTime - state.lastRedirectTime;

      if (timeSinceLastRedirect < CONFIG.RAPID_REDIRECT_THRESHOLD) {
        state.redirectCount++;

        debug(`Rapid redirect detected: ${state.redirectCount} redirects`);

        if (state.redirectCount >= CONFIG.RAPID_REDIRECT_COUNT) {
          reportSuspiciousActivity(
            "RAPID_REDIRECTS",
            {
              count: state.redirectCount,
              avgTime: timeSinceLastRedirect,
              pattern: "rapid_succession",
            },
            "CRITICAL"
          );
        }
      } else {
        // Reset counter if redirects are spaced out
        state.redirectCount = 1;
      }

      state.lastRedirectTime = currentTime;
    });

    // Also monitor popstate (back/forward navigation)
    window.addEventListener("popstate", () => {
      debug("Navigation event detected (popstate)");
    });
  }

  // ============================================================================
  // 3. FORM SUBMISSION ANALYSIS
  // ============================================================================

  /**
   * Analyze form submissions for credential harvesting attempts
   */
  function monitorFormSubmissions() {
    document.addEventListener(
      "submit",
      (e) => {
        const form = e.target;

        if (!(form instanceof HTMLFormElement)) {
          return;
        }

        analyzeForm(form, e);
      },
      true
    ); // Use capture phase to intercept before default action
  }

  function analyzeForm(form, event) {
    const inputs = Array.from(form.querySelectorAll("input"));

    // Check for credential inputs
    const hasPassword = inputs.some((i) => i.type === "password");
    const hasEmail = inputs.some(
      (i) => i.type === "email" || i.name.toLowerCase().includes("email")
    );
    const hasUsername = inputs.some(
      (i) =>
        i.name.toLowerCase().includes("user") ||
        i.name.toLowerCase().includes("login")
    );
    const hasCreditCard = inputs.some(
      (i) =>
        i.name.toLowerCase().includes("card") ||
        i.name.toLowerCase().includes("cc") ||
        i.autocomplete === "cc-number"
    );

    const formData = {
      action: form.action || window.location.href,
      method: form.method || "get",
      hasPassword: hasPassword,
      hasEmail: hasEmail,
      hasUsername: hasUsername,
      hasCreditCard: hasCreditCard,
      inputCount: inputs.length,
      timestamp: Date.now(),
    };

    debug("Form submission detected:", formData);

    // Check for cross-origin form submission
    try {
      const formOrigin = new URL(formData.action).origin;
      const pageOrigin = window.location.origin;

      if (
        formOrigin !== pageOrigin &&
        (hasPassword || hasEmail || hasCreditCard)
      ) {
        // CRITICAL: Credentials being sent to different domain
        event.preventDefault();

        reportSuspiciousActivity(
          "EXTERNAL_FORM_SUBMIT",
          {
            formAction: formData.action,
            pageOrigin: pageOrigin,
            formOrigin: formOrigin,
            hasCredentials: true,
            credentialTypes: {
              password: hasPassword,
              email: hasEmail,
              creditCard: hasCreditCard,
            },
          },
          "CRITICAL"
        );

        return false; // Block submission
      }
    } catch (error) {
      debug("Form action URL parsing error:", error);
    }

    // Check for suspicious parameters in form action
    if (formData.action) {
      const suspiciousParams = CONFIG.SUSPICIOUS_PARAM_KEYWORDS.filter(
        (keyword) => formData.action.toLowerCase().includes(keyword)
      );

      if (suspiciousParams.length > 0 && hasPassword) {
        reportSuspiciousActivity(
          "SUSPICIOUS_FORM_PARAMS",
          {
            formAction: formData.action,
            suspiciousParams: suspiciousParams,
            hasCredentials: hasPassword || hasEmail,
          },
          "MEDIUM"
        );
      }
    }

    // Track form submission
    state.formSubmissions.push(formData);
  }

  // ============================================================================
  // 4. INPUT FOCUS TRACKING
  // ============================================================================

  /**
   * Track input field focus patterns (unusual focus = suspicious)
   */
  function monitorInputFocus() {
    if (!CONFIG.TRACK_INPUT_FOCUS) return;

    document.addEventListener(
      "focus",
      (e) => {
        if (e.target instanceof HTMLInputElement) {
          const input = e.target;

          const focusEvent = {
            type: input.type,
            name: input.name || input.id || "unnamed",
            timestamp: Date.now(),
            timeFromPageLoad: performance.now() - state.pageLoadTime,
          };

          state.inputFocusEvents.push(focusEvent);

          // Check for suspicious immediate focus on sensitive fields
          if (focusEvent.timeFromPageLoad < 1000) {
            const isSensitive = CONFIG.SUSPICIOUS_FOCUS_PATTERNS.some(
              (pattern) =>
                focusEvent.type.includes(pattern) ||
                focusEvent.name.toLowerCase().includes(pattern)
            );

            if (isSensitive) {
              reportSuspiciousActivity(
                "IMMEDIATE_SENSITIVE_FOCUS",
                {
                  inputType: focusEvent.type,
                  inputName: focusEvent.name,
                  timeDelta: focusEvent.timeFromPageLoad,
                },
                "MEDIUM"
              );
            }
          }
        }
      },
      true
    );
  }

  // ============================================================================
  // 5. CLIPBOARD ACCESS MONITORING
  // ============================================================================

  /**
   * Monitor clipboard access (some phishing sites steal clipboard content)
   */
  function monitorClipboardAccess() {
    if (!CONFIG.TRACK_CLIPBOARD_ACCESS) return;

    // Monitor clipboard read
    document.addEventListener("copy", () => {
      debug("Clipboard copy event");
    });

    document.addEventListener("cut", () => {
      debug("Clipboard cut event");
    });

    document.addEventListener("paste", () => {
      state.clipboardAccessCount++;
      debug(`Clipboard paste event (count: ${state.clipboardAccessCount})`);

      if (state.clipboardAccessCount > 10) {
        reportSuspiciousActivity(
          "CLIPBOARD_ABUSE",
          {
            accessCount: state.clipboardAccessCount,
          },
          "MEDIUM"
        );
      }
    });

    // Intercept navigator.clipboard API
    if (navigator.clipboard) {
      const originalRead = navigator.clipboard.read;
      const originalReadText = navigator.clipboard.readText;

      navigator.clipboard.read = function () {
        state.clipboardAccessCount++;
        debug("Clipboard API: read() called");
        return originalRead.apply(this, arguments);
      };

      navigator.clipboard.readText = function () {
        state.clipboardAccessCount++;
        debug("Clipboard API: readText() called");
        return originalReadText.apply(this, arguments);
      };
    }
  }

  // ============================================================================
  // 6. PAGE VISIBILITY MONITORING
  // ============================================================================

  /**
   * Track page visibility changes (phishing in background tabs)
   */
  function monitorPageVisibility() {
    document.addEventListener("visibilitychange", () => {
      debug(
        `Page visibility changed: ${document.hidden ? "hidden" : "visible"}`
      );

      reportToBackground("visibilityChange", {
        hidden: document.hidden,
        visibilityState: document.visibilityState,
      });
    });
  }

  // ============================================================================
  // 7. SUSPICIOUS POPUP DETECTION
  // ============================================================================

  /**
   * Monitor for popup attempts (phishing often uses popups)
   */
  function monitorPopups() {
    const originalOpen = window.open;
    let popupCount = 0;

    window.open = function () {
      popupCount++;
      debug(`Popup detected (count: ${popupCount})`);

      if (popupCount > 3) {
        reportSuspiciousActivity(
          "EXCESSIVE_POPUPS",
          {
            count: popupCount,
          },
          "MEDIUM"
        );
      }

      reportToBackground("popupAttempt", {
        url: arguments[0],
        count: popupCount,
      });

      return originalOpen.apply(this, arguments);
    };
  }

  // ============================================================================
  // 8. AUTO-SUBMIT DETECTION
  // ============================================================================

  /**
   * Detect forms that auto-submit (phishing trick)
   */
  function detectAutoSubmit() {
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
      // Check if form has auto-submit script
      const scripts = form.querySelectorAll("script");
      const hasAutoSubmit = Array.from(scripts).some(
        (script) =>
          script.textContent.includes("submit()") ||
          script.textContent.includes(".submit")
      );

      if (hasAutoSubmit) {
        reportSuspiciousActivity(
          "AUTO_SUBMIT_FORM",
          {
            formAction: form.action,
            formId: form.id || "unknown",
          },
          "HIGH"
        );
      }
    });
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  /**
   * Initialize all monitors
   */
  function initialize() {
    debug("🛡️ PhishGuard Content Script initialized");
    debug("URL:", window.location.href);
    debug("Config:", CONFIG);

    try {
      // Start all monitoring systems
      monitorPasswordRequests();
      monitorRedirects();
      monitorFormSubmissions();
      monitorInputFocus();
      monitorClipboardAccess();
      monitorPageVisibility();
      monitorPopups();

      // Delayed checks
      setTimeout(() => {
        detectAutoSubmit();
      }, 2000);

      // Periodic status report
      setInterval(() => {
        if (state.suspiciousActivities.length > 0) {
          reportToBackground("statusReport", {
            suspiciousActivities: state.suspiciousActivities.length,
            formSubmissions: state.formSubmissions.length,
            inputFocusEvents: state.inputFocusEvents.length,
            clipboardAccess: state.clipboardAccessCount,
          });
        }
      }, 30000); // Every 30 seconds

      debug("✅ All monitors active");
    } catch (error) {
      console.error("[PhishGuard] Initialization error:", error);
    }
  }

  // Start when DOM is ready
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize);
  } else {
    initialize();
  }

  // ============================================================================
  // MESSAGE HANDLER (from background script)
  // ============================================================================

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    debug("Message received from background:", request);

    if (request.action === "getState") {
      sendResponse({ state: state });
    } else if (request.action === "reset") {
      // Reset state
      state.suspiciousActivities = [];
      state.formSubmissions = [];
      state.inputFocusEvents = [];
      state.clipboardAccessCount = 0;
      sendResponse({ success: true });
    }

    return true; // Keep message channel open
  });

  // ============================================================================
  // EXPORT (for testing)
  // ============================================================================

  window.PhishGuardContentScript = {
    state: state,
    config: CONFIG,
    reportSuspiciousActivity: reportSuspiciousActivity,
  };
})();
