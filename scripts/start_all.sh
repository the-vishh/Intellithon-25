#!/bin/bash

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 STARTING PHISHGUARD AI - ALL SERVICES"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "This will open 2 terminal windows:"
echo "  1. Rust API Gateway (port 8080)"
echo "  2. Python ML Service (port 8000)"
echo ""
echo "⚠️  DO NOT CLOSE THESE WINDOWS!"
echo "    The extension needs them to stay open."
echo ""
echo "Press any key to start..."
read -n 1 -s

echo ""
echo "🚀 Starting services..."
echo ""

# Start Rust API in new terminal
echo "📦 Starting Rust API Gateway..."
start bash -c "cd 'c:/Users/Sri Vishnu/Extension/backend' && echo '🦀 RUST API GATEWAY' && echo '==================' && echo '' && cargo run --release; read -p 'Press enter to close...'"

# Wait a moment
sleep 2

# Start Python ML in new terminal
echo "🐍 Starting Python ML Service..."
start bash -c "cd 'c:/Users/Sri Vishnu/Extension/ml-service' && echo '🐍 PYTHON ML SERVICE' && echo '====================' && echo '' && python3 -m uvicorn app:app --host 0.0.0.0 --port 8000; read -p 'Press enter to close...'"

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  ✅ SERVICES STARTING..."
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Wait 5-10 seconds for both services to fully start."
echo ""
echo "Then:"
echo "  1. Go to chrome://extensions"
echo "  2. Reload your extension (click 🔄)"
echo "  3. Click extension icon"
echo "  4. Try 'Check URL' - it should work!"
echo ""
echo "To check if services are running:"
echo "  ./check_services.sh"
echo ""
echo "════════════════════════════════════════════════════════════════"
