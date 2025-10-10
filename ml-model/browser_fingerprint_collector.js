
// PhishGuard Browser Fingerprinting
// Injected into every page for enhanced threat detection


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
        ctx.fillText('PhishGuard Security 🛡️', 2, 15);
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


// Listen for fingerprint requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'GET_FINGERPRINT') {
        const fp = collectFingerprint();
        sendResponse({fingerprint: fp});
    }
});

// Automatic fingerprint on page load
window.addEventListener('load', function() {
    collectFingerprint();
});
