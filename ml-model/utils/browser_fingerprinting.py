"""
 BROWSER FINGERPRINTING SYSTEM
=================================

Advanced threat detection via device and browser identification
"""

import json
import hashlib
from datetime import datetime


class BrowserFingerprint:
    """
    Browser fingerprinting for enhanced threat detection

    Collects:
    - Browser/OS information
    - Screen resolution & color depth
    - Timezone & language
    - Installed plugins
    - Canvas/WebGL fingerprints
    - Audio context fingerprints
    - Hardware concurrency
    """

    def __init__(self):
        self.fingerprint_cache = {}

    def generate_javascript_collector(self):
        """
        Generate JavaScript code to collect browser fingerprint

        Returns:
            JavaScript code as string
        """
        js_code = """
// Browser Fingerprint Collector
(function() {
    const fingerprint = {};

    // Basic browser info
    fingerprint.userAgent = navigator.userAgent;
    fingerprint.platform = navigator.platform;
    fingerprint.language = navigator.language;
    fingerprint.languages = navigator.languages || [];
    fingerprint.cookieEnabled = navigator.cookieEnabled;
    fingerprint.doNotTrack = navigator.doNotTrack || 'unknown';

    // Screen information
    fingerprint.screenResolution = `${screen.width}x${screen.height}`;
    fingerprint.screenColorDepth = screen.colorDepth;
    fingerprint.screenPixelDepth = screen.pixelDepth;
    fingerprint.availableScreenResolution = `${screen.availWidth}x${screen.availHeight}`;

    // Timezone
    fingerprint.timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    fingerprint.timezoneOffset = new Date().getTimezoneOffset();

    // Hardware
    fingerprint.hardwareConcurrency = navigator.hardwareConcurrency || 'unknown';
    fingerprint.deviceMemory = navigator.deviceMemory || 'unknown';

    // Plugins (deprecated but some browsers still support)
    fingerprint.pluginsCount = navigator.plugins ? navigator.plugins.length : 0;

    // WebGL fingerprint
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (gl) {
            fingerprint.webglVendor = gl.getParameter(gl.VENDOR);
            fingerprint.webglRenderer = gl.getParameter(gl.RENDERER);
        }
    } catch(e) {
        fingerprint.webglVendor = 'unavailable';
        fingerprint.webglRenderer = 'unavailable';
    }

    // Canvas fingerprint
    try {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        ctx.textBaseline = 'top';
        ctx.font = '14px "Arial"';
        ctx.textBaseline = 'alphabetic';
        ctx.fillStyle = '#f60';
        ctx.fillRect(125, 1, 62, 20);
        ctx.fillStyle = '#069';
        ctx.fillText('PhishGuard Security ', 2, 15);
        ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
        ctx.fillText('Canvas Fingerprint', 4, 17);

        fingerprint.canvasFingerprint = canvas.toDataURL();
    } catch(e) {
        fingerprint.canvasFingerprint = 'unavailable';
    }

    // Audio context fingerprint
    try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) {
            const audioContext = new AudioContext();
            const oscillator = audioContext.createOscillator();
            const analyser = audioContext.createAnalyser();
            const gainNode = audioContext.createGain();
            const scriptProcessor = audioContext.createScriptProcessor(4096, 1, 1);

            gainNode.gain.value = 0;
            oscillator.connect(analyser);
            analyser.connect(scriptProcessor);
            scriptProcessor.connect(gainNode);
            gainNode.connect(audioContext.destination);

            oscillator.start(0);

            fingerprint.audioContextSampleRate = audioContext.sampleRate;
            fingerprint.audioContextState = audioContext.state;
        }
    } catch(e) {
        fingerprint.audioContextSampleRate = 'unavailable';
    }

    // Touch support
    fingerprint.touchSupport = 'ontouchstart' in window;
    fingerprint.maxTouchPoints = navigator.maxTouchPoints || 0;

    // Battery API (if available)
    if (navigator.getBattery) {
        navigator.getBattery().then(function(battery) {
            fingerprint.batteryLevel = battery.level;
            fingerprint.batteryCharging = battery.charging;
        });
    }

    // Connection info
    if (navigator.connection) {
        fingerprint.connectionType = navigator.connection.effectiveType;
        fingerprint.connectionDownlink = navigator.connection.downlink;
    }

    // Calculate fingerprint hash
    const fingerprintString = JSON.stringify(fingerprint);
    crypto.subtle.digest('SHA-256', new TextEncoder().encode(fingerprintString))
        .then(hashBuffer => {
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            fingerprint.fingerprintHash = hashHex;

            // Send to extension backend
            chrome.runtime.sendMessage({
                type: 'BROWSER_FINGERPRINT',
                data: fingerprint
            });
        });

    return fingerprint;
})();
"""
        return js_code

    def process_fingerprint(self, fingerprint_data):
        """
        Process collected fingerprint data

        Args:
            fingerprint_data: Dictionary with browser fingerprint

        Returns:
            Processed fingerprint with risk scores
        """
        processed = {
            "raw": fingerprint_data,
            "timestamp": datetime.now().isoformat(),
            "risk_indicators": self._analyze_risk(fingerprint_data),
            "fingerprint_id": fingerprint_data.get("fingerprintHash", "unknown"),
        }

        return processed

    def _analyze_risk(self, fingerprint):
        """
        Analyze fingerprint for suspicious patterns

        Returns:
            Dictionary with risk indicators
        """
        risks = {
            "overall_risk": 0.0,
            "suspicious_indicators": [],
            "trust_score": 100.0,
        }

        # Check for automation/bot indicators
        if fingerprint.get("webglVendor") == "Brian Paul":  # SwiftShader (headless)
            risks["suspicious_indicators"].append("Headless browser detected")
            risks["overall_risk"] += 0.3

        if (
            fingerprint.get("pluginsCount", 0) == 0
            and fingerprint.get("platform") != "Linux"
        ):
            risks["suspicious_indicators"].append("No plugins (possible automation)")
            risks["overall_risk"] += 0.1

        # Check for inconsistencies
        if fingerprint.get("platform") == "Win32" and "Linux" in fingerprint.get(
            "userAgent", ""
        ):
            risks["suspicious_indicators"].append("Platform/UserAgent mismatch")
            risks["overall_risk"] += 0.4

        # Check for privacy tools
        if fingerprint.get("doNotTrack") == "1":
            risks["suspicious_indicators"].append(
                "DoNotTrack enabled (privacy conscious)"
            )
            # Not necessarily malicious, but good to note

        # Unusual screen resolution
        screen_res = fingerprint.get("screenResolution", "1920x1080")
        if screen_res in ["800x600", "1024x768"]:  # Very old or emulated
            risks["suspicious_indicators"].append("Unusual screen resolution")
            risks["overall_risk"] += 0.1

        # Hardware concurrency check
        hw_concurrency = fingerprint.get("hardwareConcurrency", 4)
        if isinstance(hw_concurrency, int) and hw_concurrency > 64:
            risks["suspicious_indicators"].append("Unusually high CPU cores")
            risks["overall_risk"] += 0.2

        # Calculate trust score
        risks["trust_score"] = max(0, 100 - (risks["overall_risk"] * 100))

        return risks

    def compare_fingerprints(self, fingerprint1_id, fingerprint2_id):
        """
        Compare two fingerprints to detect suspicious behavior

        Returns:
            Similarity score (0-1)
        """
        # In production, this would compare actual fingerprints
        # For now, simple hash comparison
        return 1.0 if fingerprint1_id == fingerprint2_id else 0.0

    def detect_fingerprint_spoofing(self, fingerprint):
        """
        Detect if fingerprint appears to be spoofed

        Returns:
            Boolean indicating if spoofing detected
        """
        risks = self._analyze_risk(fingerprint)
        return risks["overall_risk"] > 0.5

    def generate_content_script(self):
        """
        Generate complete content script for Chrome extension

        Returns:
            JavaScript code as string
        """
        content_script = f"""
// PhishGuard Browser Fingerprinting
// Injected into every page for enhanced threat detection

{self.generate_javascript_collector()}

// Listen for fingerprint requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {{
    if (request.type === 'GET_FINGERPRINT') {{
        const fp = collectFingerprint();
        sendResponse({{fingerprint: fp}});
    }}
}});

// Automatic fingerprint on page load
window.addEventListener('load', function() {{
    collectFingerprint();
}});
"""
        return content_script


def demo_fingerprinting():
    """Demonstrate browser fingerprinting"""
    print("=" * 80)
    print(" BROWSER FINGERPRINTING SYSTEM DEMO")
    print("=" * 80)

    fp = BrowserFingerprint()

    # Generate JavaScript collector
    print("\n1⃣ Generating JavaScript fingerprint collector...")
    js_code = fp.generate_javascript_collector()
    print(f"    Generated {len(js_code)} bytes of JavaScript code")

    # Simulate fingerprint data
    print("\n2⃣ Processing sample fingerprint...")
    sample_fingerprint = {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "platform": "Win32",
        "language": "en-US",
        "screenResolution": "1920x1080",
        "screenColorDepth": 24,
        "timezone": "America/New_York",
        "timezoneOffset": 300,
        "hardwareConcurrency": 8,
        "deviceMemory": 16,
        "webglVendor": "Google Inc.",
        "webglRenderer": "ANGLE (NVIDIA)",
        "cookieEnabled": True,
        "doNotTrack": "unspecified",
        "pluginsCount": 3,
        "touchSupport": False,
        "fingerprintHash": "abc123def456...",
    }

    processed = fp.process_fingerprint(sample_fingerprint)

    print(f"\n    Fingerprint Analysis:")
    print(f"      Fingerprint ID: {processed['fingerprint_id']}")
    print(f"      Overall Risk: {processed['risk_indicators']['overall_risk']:.2f}")
    print(f"      Trust Score: {processed['risk_indicators']['trust_score']:.1f}/100")

    if processed["risk_indicators"]["suspicious_indicators"]:
        print(f"\n       Suspicious Indicators:")
        for indicator in processed["risk_indicators"]["suspicious_indicators"]:
            print(f"         - {indicator}")
    else:
        print(f"\n       No suspicious indicators detected")

    # Test suspicious fingerprint
    print("\n3⃣ Testing suspicious fingerprint (headless browser)...")
    suspicious_fingerprint = {
        **sample_fingerprint,
        "webglVendor": "Brian Paul",  # SwiftShader - headless
        "pluginsCount": 0,
        "platform": "Win32",
        "userAgent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",  # Mismatch
        "fingerprintHash": "suspicious123...",
    }

    suspicious_processed = fp.process_fingerprint(suspicious_fingerprint)

    print(f"\n    Suspicious Fingerprint Analysis:")
    print(
        f"      Overall Risk: {suspicious_processed['risk_indicators']['overall_risk']:.2f}"
    )
    print(
        f"      Trust Score: {suspicious_processed['risk_indicators']['trust_score']:.1f}/100"
    )
    print(f"\n       Suspicious Indicators:")
    for indicator in suspicious_processed["risk_indicators"]["suspicious_indicators"]:
        print(f"         - {indicator}")

    is_spoofed = fp.detect_fingerprint_spoofing(suspicious_fingerprint)
    print(f"\n       Spoofing Detected: {is_spoofed}")

    # Generate content script
    print("\n4⃣ Generating Chrome extension content script...")
    content_script = fp.generate_content_script()
    print(f"    Generated {len(content_script)} bytes of content script")

    # Save content script
    output_file = "browser_fingerprint_collector.js"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content_script)
    print(f"    Saved to: {output_file}")

    print("\n" + "=" * 80)
    print(" BROWSER FINGERPRINTING READY")
    print("=" * 80)
    print("\n Features:")
    print("    Browser/OS detection")
    print("    Screen & hardware profiling")
    print("    Canvas & WebGL fingerprints")
    print("    Audio context fingerprints")
    print("    Bot/automation detection")
    print("    Spoofing detection")
    print("    Privacy tool detection")
    print("\n Use Cases:")
    print("   • Detect headless browsers (bots)")
    print("   • Identify fingerprint spoofing")
    print("   • Track suspicious device patterns")
    print("   • Enhance threat scoring")
    print("=" * 80)


if __name__ == "__main__":
    demo_fingerprinting()
