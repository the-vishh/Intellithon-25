/**
 * 🔬 PHISHGUARD AI - FINGERPRINTING DETECTION
 * ============================================
 *
 * Advanced browser fingerprinting detection and prevention
 *
 * Features:
 * - Canvas fingerprinting detection
 * - WebGL fingerprinting detection
 * - Audio fingerprinting detection
 * - Font fingerprinting detection
 * - localStorage/sessionStorage abuse monitoring
 * - Navigator properties tracking
 * - Battery API abuse detection
 * - Screen/Display fingerprinting

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
    // Threshold limits
    CANVAS_THRESHOLD: 3, // > 3 canvas operations = suspicious
    WEBGL_THRESHOLD: 20, // > 20 WebGL calls = suspicious
    LOCALSTORAGE_THRESHOLD: 50, // > 50 writes = data exfiltration
    NAVIGATOR_ACCESS_THRESHOLD: 10, // > 10 accesses to same property = fingerprinting
    AUDIO_CONTEXT_THRESHOLD: 2, // > 2 AudioContext creations = suspicious
    FONT_DETECTION_THRESHOLD: 50, // > 50 font checks = fingerprinting

    // Monitoring toggles
    MONITOR_CANVAS: true,
    MONITOR_WEBGL: true,
    MONITOR_AUDIO: true,
    MONITOR_FONTS: true,
    MONITOR_STORAGE: true,
    MONITOR_NAVIGATOR: true,
    MONITOR_SCREEN: true,
    MONITOR_BATTERY: true,

    // Noise injection (optional - adds privacy)
    INJECT_CANVAS_NOISE: false, // Add noise to canvas fingerprint
    INJECT_AUDIO_NOISE: false, // Add noise to audio fingerprint

    // Debug mode
    DEBUG: true,
  };

  // ============================================================================
  // STATE MANAGEMENT
  // ============================================================================

  const fingerprintingState = {
    // Canvas tracking
    canvasOperations: 0,
    canvasToDataURL: 0,
    canvasGetImageData: 0,
    canvasMeasureText: 0,

    // WebGL tracking
    webglCalls: 0,
    webglParameters: [],

    // Audio tracking
    audioContextCount: 0,
    audioOscillatorCount: 0,

    // Font tracking
    fontChecks: 0,
    fontsChecked: new Set(),

    // Storage tracking
    localStorageWrites: 0,
    sessionStorageWrites: 0,
    localStorageReads: 0,

    // Navigator tracking
    navigatorAccess: {},

    // Screen tracking
    screenPropertyAccess: 0,

    // Battery API tracking
    batteryAPIAccess: 0,

    // Timestamps
    firstDetection: null,
    lastDetection: null,

    // Overall fingerprinting score (0-100)
    fingerprintingScore: 0,
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  function debug(message, data = null) {
    if (CONFIG.DEBUG) {
      console.log(`[PhishGuard Fingerprint] ${message}`, data || "");
    }
  }

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
        }
      }
    );
  }

  function reportFingerprinting(type, data, severity = "MEDIUM") {
    if (!fingerprintingState.firstDetection) {
      fingerprintingState.firstDetection = Date.now();
    }
    fingerprintingState.lastDetection = Date.now();

    // Calculate fingerprinting score
    updateFingerprintingScore();

    const report = {
      type: type,
      data: data,
      severity: severity,
      fingerprintingScore: fingerprintingState.fingerprintingScore,
      url: window.location.href,
      timestamp: Date.now(),
    };

    debug(`🔬 Fingerprinting Detected: ${type}`, report);
    reportToBackground("fingerprintingDetected", report);

    // Show warning for high-severity fingerprinting
    if (severity === "HIGH" && fingerprintingState.fingerprintingScore > 70) {
      showFingerprintingWarning(type, data);
    }
  }

  function updateFingerprintingScore() {
    let score = 0;

    // Canvas fingerprinting (0-20 points)
    if (fingerprintingState.canvasOperations > CONFIG.CANVAS_THRESHOLD) {
      score += Math.min(20, fingerprintingState.canvasOperations * 2);
    }

    // WebGL fingerprinting (0-20 points)
    if (fingerprintingState.webglCalls > CONFIG.WEBGL_THRESHOLD) {
      score += Math.min(20, fingerprintingState.webglCalls);
    }

    // Audio fingerprinting (0-15 points)
    if (
      fingerprintingState.audioContextCount > CONFIG.AUDIO_CONTEXT_THRESHOLD
    ) {
      score += 15;
    }

    // Font fingerprinting (0-15 points)
    if (fingerprintingState.fontChecks > CONFIG.FONT_DETECTION_THRESHOLD) {
      score += 15;
    }

    // Storage abuse (0-15 points)
    if (
      fingerprintingState.localStorageWrites > CONFIG.LOCALSTORAGE_THRESHOLD
    ) {
      score += 15;
    }

    // Navigator tracking (0-15 points)
    const navigatorAccessCount = Object.values(
      fingerprintingState.navigatorAccess
    ).reduce((a, b) => a + b, 0);
    if (navigatorAccessCount > CONFIG.NAVIGATOR_ACCESS_THRESHOLD * 3) {
      score += 15;
    }

    fingerprintingState.fingerprintingScore = Math.min(100, score);
  }

  function showFingerprintingWarning(type, data) {
    if (document.getElementById("phishguard-fingerprint-warning")) {
      return;
    }

    const banner = document.createElement("div");
    banner.id = "phishguard-fingerprint-warning";
    banner.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
            color: white;
            padding: 16px 24px;
            z-index: 999998;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            animation: slideDown 0.3s ease-out;
        `;

    banner.innerHTML = `
            <style>
                @keyframes slideDown {
                    from { transform: translateY(-100%); }
                    to { transform: translateY(0); }
                }
            </style>
            <div style="max-width: 1200px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="font-size: 32px;">🔬</div>
                    <div>
                        <div style="font-weight: 700; font-size: 16px; margin-bottom: 4px;">
                            Browser Fingerprinting Detected
                        </div>
                        <div style="font-size: 13px; opacity: 0.9;">
                            This site is collecting your browser's unique characteristics. Fingerprinting Score: ${fingerprintingState.fingerprintingScore}/100
                        </div>
                    </div>
                </div>
                <button id="phishguard-fingerprint-close" style="
                    background: rgba(255,255,255,0.2);
                    border: none;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    cursor: pointer;
                    font-weight: 600;
                    transition: background 0.2s;
                " onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                    Dismiss
                </button>
            </div>
        `;

    document.body.appendChild(banner);

    document.getElementById("phishguard-fingerprint-close").onclick = () => {
      banner.remove();
    };

    // Auto-dismiss after 10 seconds
    setTimeout(() => {
      if (banner.parentNode) {
        banner.remove();
      }
    }, 10000);
  }

  // ============================================================================
  // 1. CANVAS FINGERPRINTING DETECTION
  // ============================================================================

  function monitorCanvasFingerprinting() {
    if (!CONFIG.MONITOR_CANVAS) return;

    // Hook toDataURL (most common canvas fingerprinting method)
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function () {
      fingerprintingState.canvasToDataURL++;
      fingerprintingState.canvasOperations++;

      debug(
        `Canvas toDataURL called (count: ${fingerprintingState.canvasToDataURL})`
      );

      if (fingerprintingState.canvasOperations > CONFIG.CANVAS_THRESHOLD) {
        reportFingerprinting(
          "CANVAS_FINGERPRINTING",
          {
            method: "toDataURL",
            count: fingerprintingState.canvasToDataURL,
            totalOperations: fingerprintingState.canvasOperations,
          },
          "HIGH"
        );
      }

      // Optional: Inject noise
      if (CONFIG.INJECT_CANVAS_NOISE) {
        const context = this.getContext("2d");
        if (context) {
          const imageData = context.getImageData(0, 0, this.width, this.height);
          for (let i = 0; i < imageData.data.length; i += 4) {
            imageData.data[i] += Math.floor(Math.random() * 3) - 1; // Add ±1 noise
          }
          context.putImageData(imageData, 0, 0);
        }
      }

      return originalToDataURL.apply(this, arguments);
    };

    // Hook getImageData
    const originalGetImageData =
      CanvasRenderingContext2D.prototype.getImageData;
    CanvasRenderingContext2D.prototype.getImageData = function () {
      fingerprintingState.canvasGetImageData++;
      fingerprintingState.canvasOperations++;

      debug(
        `Canvas getImageData called (count: ${fingerprintingState.canvasGetImageData})`
      );

      if (fingerprintingState.canvasOperations > CONFIG.CANVAS_THRESHOLD) {
        reportFingerprinting(
          "CANVAS_FINGERPRINTING",
          {
            method: "getImageData",
            count: fingerprintingState.canvasGetImageData,
          },
          "HIGH"
        );
      }

      return originalGetImageData.apply(this, arguments);
    };

    // Hook measureText (text rendering fingerprinting)
    const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
    CanvasRenderingContext2D.prototype.measureText = function () {
      fingerprintingState.canvasMeasureText++;
      fingerprintingState.canvasOperations++;

      if (fingerprintingState.canvasMeasureText > 20) {
        reportFingerprinting(
          "CANVAS_TEXT_FINGERPRINTING",
          {
            count: fingerprintingState.canvasMeasureText,
            text: arguments[0],
          },
          "MEDIUM"
        );
      }

      return originalMeasureText.apply(this, arguments);
    };

    debug("✅ Canvas fingerprinting monitor active");
  }

  // ============================================================================
  // 2. WEBGL FINGERPRINTING DETECTION
  // ============================================================================

  function monitorWebGLFingerprinting() {
    if (!CONFIG.MONITOR_WEBGL) return;

    // Hook WebGL getParameter (used to get GPU info)
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function (parameter) {
      fingerprintingState.webglCalls++;

      // Track which parameters are accessed
      fingerprintingState.webglParameters.push({
        parameter: parameter,
        timestamp: Date.now(),
      });

      debug(
        `WebGL getParameter called (count: ${fingerprintingState.webglCalls})`
      );

      // Sensitive GPU parameters
      const sensitiveParams = [
        0x1f00, // GL_VENDOR
        0x1f01, // GL_RENDERER
        0x1f02, // GL_VERSION
        0x9245, // UNMASKED_VENDOR_WEBGL
        0x9246, // UNMASKED_RENDERER_WEBGL
      ];

      if (sensitiveParams.includes(parameter)) {
        reportFingerprinting(
          "WEBGL_GPU_FINGERPRINTING",
          {
            parameter: parameter,
            count: fingerprintingState.webglCalls,
          },
          "HIGH"
        );
      }

      if (fingerprintingState.webglCalls > CONFIG.WEBGL_THRESHOLD) {
        reportFingerprinting(
          "WEBGL_FINGERPRINTING",
          {
            totalCalls: fingerprintingState.webglCalls,
            uniqueParameters: new Set(
              fingerprintingState.webglParameters.map((p) => p.parameter)
            ).size,
          },
          "HIGH"
        );
      }

      return originalGetParameter.apply(this, arguments);
    };

    // Also hook WebGL2
    if (typeof WebGL2RenderingContext !== "undefined") {
      const originalGetParameter2 =
        WebGL2RenderingContext.prototype.getParameter;
      WebGL2RenderingContext.prototype.getParameter = function (parameter) {
        fingerprintingState.webglCalls++;
        return originalGetParameter2.apply(this, arguments);
      };
    }

    debug("✅ WebGL fingerprinting monitor active");
  }

  // ============================================================================
  // 3. AUDIO FINGERPRINTING DETECTION
  // ============================================================================

  function monitorAudioFingerprinting() {
    if (!CONFIG.MONITOR_AUDIO) return;

    // Hook AudioContext creation
    const OriginalAudioContext =
      window.AudioContext || window.webkitAudioContext;
    if (OriginalAudioContext) {
      window.AudioContext = function () {
        fingerprintingState.audioContextCount++;

        debug(
          `AudioContext created (count: ${fingerprintingState.audioContextCount})`
        );

        if (
          fingerprintingState.audioContextCount > CONFIG.AUDIO_CONTEXT_THRESHOLD
        ) {
          reportFingerprinting(
            "AUDIO_FINGERPRINTING",
            {
              audioContextCount: fingerprintingState.audioContextCount,
            },
            "HIGH"
          );
        }

        return new OriginalAudioContext(...arguments);
      };

      window.AudioContext.prototype = OriginalAudioContext.prototype;

      // Hook OscillatorNode (commonly used in audio fingerprinting)
      const originalCreateOscillator =
        AudioContext.prototype.createOscillator ||
        OriginalAudioContext.prototype.createOscillator;

      if (originalCreateOscillator) {
        const hookCreateOscillator = function () {
          fingerprintingState.audioOscillatorCount++;

          if (fingerprintingState.audioOscillatorCount > 3) {
            reportFingerprinting(
              "AUDIO_OSCILLATOR_FINGERPRINTING",
              {
                oscillatorCount: fingerprintingState.audioOscillatorCount,
              },
              "MEDIUM"
            );
          }

          return originalCreateOscillator.apply(this, arguments);
        };

        AudioContext.prototype.createOscillator = hookCreateOscillator;
        if (window.webkitAudioContext) {
          window.webkitAudioContext.prototype.createOscillator =
            hookCreateOscillator;
        }
      }
    }

    debug("✅ Audio fingerprinting monitor active");
  }

  // ============================================================================
  // 4. FONT FINGERPRINTING DETECTION
  // ============================================================================

  function monitorFontFingerprinting() {
    if (!CONFIG.MONITOR_FONTS) return;

    // Monitor canvas measureText for font detection
    const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
    CanvasRenderingContext2D.prototype.measureText = function (text) {
      // Check if this is font detection (typically uses specific test strings)
      const fontDetectionPatterns = [
        "mmmmmmmmmmlli",
        "abcdefghijklmnopqrstuvwxyz0123456789",
        "The quick brown fox jumps over the lazy dog",
      ];

      if (fontDetectionPatterns.some((pattern) => text.includes(pattern))) {
        fingerprintingState.fontChecks++;

        // Extract font from context
        const font = this.font || "unknown";
        fingerprintingState.fontsChecked.add(font);

        debug(
          `Font detection attempt (count: ${fingerprintingState.fontChecks})`
        );

        if (fingerprintingState.fontChecks > CONFIG.FONT_DETECTION_THRESHOLD) {
          reportFingerprinting(
            "FONT_FINGERPRINTING",
            {
              checksCount: fingerprintingState.fontChecks,
              uniqueFonts: fingerprintingState.fontsChecked.size,
              fonts: Array.from(fingerprintingState.fontsChecked),
            },
            "MEDIUM"
          );
        }
      }

      return originalMeasureText.apply(this, arguments);
    };

    debug("✅ Font fingerprinting monitor active");
  }

  // ============================================================================
  // 5. LOCALSTORAGE/SESSIONSTORAGE ABUSE DETECTION
  // ============================================================================

  function monitorStorageAbuse() {
    if (!CONFIG.MONITOR_STORAGE) return;

    // Hook localStorage.setItem
    const originalLocalStorageSetItem = Storage.prototype.setItem;
    Storage.prototype.setItem = function (key, value) {
      if (this === window.localStorage) {
        fingerprintingState.localStorageWrites++;

        debug(
          `localStorage.setItem (count: ${fingerprintingState.localStorageWrites})`
        );

        if (
          fingerprintingState.localStorageWrites > CONFIG.LOCALSTORAGE_THRESHOLD
        ) {
          reportFingerprinting(
            "LOCALSTORAGE_ABUSE",
            {
              writes: fingerprintingState.localStorageWrites,
              suspectedExfiltration: true,
            },
            "HIGH"
          );
        }
      } else if (this === window.sessionStorage) {
        fingerprintingState.sessionStorageWrites++;
      }

      return originalLocalStorageSetItem.apply(this, arguments);
    };

    // Hook localStorage.getItem (excessive reads can indicate fingerprinting)
    const originalLocalStorageGetItem = Storage.prototype.getItem;
    Storage.prototype.getItem = function (key) {
      if (this === window.localStorage) {
        fingerprintingState.localStorageReads++;

        if (fingerprintingState.localStorageReads > 100) {
          reportFingerprinting(
            "LOCALSTORAGE_EXCESSIVE_READS",
            {
              reads: fingerprintingState.localStorageReads,
            },
            "MEDIUM"
          );
        }
      }

      return originalLocalStorageGetItem.apply(this, arguments);
    };

    debug("✅ Storage abuse monitor active");
  }

  // ============================================================================
  // 6. NAVIGATOR PROPERTIES TRACKING
  // ============================================================================

  function monitorNavigatorAccess() {
    if (!CONFIG.MONITOR_NAVIGATOR) return;

    const navigatorProps = [
      "userAgent",
      "platform",
      "language",
      "languages",
      "hardwareConcurrency",
      "deviceMemory",
      "vendor",
      "cookieEnabled",
      "doNotTrack",
      "maxTouchPoints",
      "product",
      "productSub",
      "appName",
      "appVersion",
    ];

    navigatorProps.forEach((prop) => {
      if (prop in Navigator.prototype) {
        const originalDescriptor = Object.getOwnPropertyDescriptor(
          Navigator.prototype,
          prop
        );

        if (originalDescriptor && originalDescriptor.get) {
          Object.defineProperty(Navigator.prototype, prop, {
            get: function () {
              if (!fingerprintingState.navigatorAccess[prop]) {
                fingerprintingState.navigatorAccess[prop] = 0;
              }
              fingerprintingState.navigatorAccess[prop]++;

              debug(
                `Navigator.${prop} accessed (count: ${fingerprintingState.navigatorAccess[prop]})`
              );

              if (
                fingerprintingState.navigatorAccess[prop] >
                CONFIG.NAVIGATOR_ACCESS_THRESHOLD
              ) {
                reportFingerprinting(
                  "NAVIGATOR_FINGERPRINTING",
                  {
                    property: prop,
                    accessCount: fingerprintingState.navigatorAccess[prop],
                    totalAccesses: Object.values(
                      fingerprintingState.navigatorAccess
                    ).reduce((a, b) => a + b, 0),
                  },
                  "MEDIUM"
                );
              }

              return originalDescriptor.get.call(this);
            },
            configurable: true,
          });
        }
      }
    });

    debug("✅ Navigator properties monitor active");
  }

  // ============================================================================
  // 7. SCREEN/DISPLAY FINGERPRINTING DETECTION
  // ============================================================================

  function monitorScreenFingerprinting() {
    if (!CONFIG.MONITOR_SCREEN) return;

    const screenProps = [
      "width",
      "height",
      "availWidth",
      "availHeight",
      "colorDepth",
      "pixelDepth",
    ];

    screenProps.forEach((prop) => {
      const originalDescriptor = Object.getOwnPropertyDescriptor(
        Screen.prototype,
        prop
      );

      if (originalDescriptor && originalDescriptor.get) {
        Object.defineProperty(Screen.prototype, prop, {
          get: function () {
            fingerprintingState.screenPropertyAccess++;

            if (fingerprintingState.screenPropertyAccess > 20) {
              reportFingerprinting(
                "SCREEN_FINGERPRINTING",
                {
                  accessCount: fingerprintingState.screenPropertyAccess,
                },
                "LOW"
              );
            }

            return originalDescriptor.get.call(this);
          },
          configurable: true,
        });
      }
    });

    debug("✅ Screen fingerprinting monitor active");
  }

  // ============================================================================
  // 8. BATTERY API ABUSE DETECTION
  // ============================================================================

  function monitorBatteryAPI() {
    if (!CONFIG.MONITOR_BATTERY) return;

    if ("getBattery" in navigator) {
      const originalGetBattery = navigator.getBattery;
      navigator.getBattery = function () {
        fingerprintingState.batteryAPIAccess++;

        debug(
          `Battery API accessed (count: ${fingerprintingState.batteryAPIAccess})`
        );

        if (fingerprintingState.batteryAPIAccess > 2) {
          reportFingerprinting(
            "BATTERY_API_FINGERPRINTING",
            {
              accessCount: fingerprintingState.batteryAPIAccess,
            },
            "LOW"
          );
        }

        return originalGetBattery.apply(this, arguments);
      };
    }

    debug("✅ Battery API monitor active");
  }

  // ============================================================================
  // PERIODIC REPORTING
  // ============================================================================

  function startPeriodicReporting() {
    setInterval(() => {
      if (fingerprintingState.fingerprintingScore > 0) {
        updateFingerprintingScore();

        reportToBackground("fingerprintingSummary", {
          score: fingerprintingState.fingerprintingScore,
          state: fingerprintingState,
          duration:
            fingerprintingState.lastDetection -
            fingerprintingState.firstDetection,
        });

        debug(
          `📊 Fingerprinting Summary - Score: ${fingerprintingState.fingerprintingScore}/100`
        );
      }
    }, 30000); // Every 30 seconds
  }

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  function initialize() {
    debug("🔬 PhishGuard Fingerprinting Detection initialized");
    debug("Config:", CONFIG);

    try {
      monitorCanvasFingerprinting();
      monitorWebGLFingerprinting();
      monitorAudioFingerprinting();
      monitorFontFingerprinting();
      monitorStorageAbuse();
      monitorNavigatorAccess();
      monitorScreenFingerprinting();
      monitorBatteryAPI();
      startPeriodicReporting();

      debug("✅ All fingerprinting monitors active");
    } catch (error) {
      console.error("[PhishGuard Fingerprint] Initialization error:", error);
    }
  }

  // Start immediately
  initialize();

  // ============================================================================
  // MESSAGE HANDLER
  // ============================================================================

  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getFingerprintingState") {
      sendResponse({ state: fingerprintingState });
    } else if (request.action === "resetFingerprintingState") {
      Object.keys(fingerprintingState).forEach((key) => {
        if (typeof fingerprintingState[key] === "number") {
          fingerprintingState[key] = 0;
        } else if (fingerprintingState[key] instanceof Set) {
          fingerprintingState[key].clear();
        } else if (Array.isArray(fingerprintingState[key])) {
          fingerprintingState[key] = [];
        } else if (typeof fingerprintingState[key] === "object") {
          fingerprintingState[key] = {};
        }
      });
      sendResponse({ success: true });
    }

    return true;
  });

  // ============================================================================
  // EXPORT (for testing)
  // ============================================================================

  window.PhishGuardFingerprintDetection = {
    state: fingerprintingState,
    config: CONFIG,
  };
})();
