#!/bin/bash

set -e

echo "📦 Building Docker image: kivy-attendance-app"
docker build -t kivy-attendance-app .

echo "🚀 Running Docker container to build APK..."
docker run -it --rm -v "$PWD":/app kivy-attendance-app
