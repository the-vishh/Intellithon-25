#!/bin/bash
# Start ML Service

echo "Starting Python ML Service..."
echo "Working directory: $(pwd)"
echo "Python version: $(python3 --version)"

python3 app.py
