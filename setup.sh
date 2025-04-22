#!/bin/bash
# Setup script for Invoice Processor application

# Create necessary directories
mkdir -p backend/uploads
mkdir -p backend/outputs

# Install Python dependencies
pip install fastapi uvicorn openpyxl python-multipart

# Install frontend dependencies and build (if npm is available)
if command -v npm &> /dev/null; then
    echo "Building React frontend..."
    cd frontend
    npm install
    npm run build
    cd ..
    echo "Frontend build complete!"
else
    echo "npm not found. Cannot build frontend."
    echo "Please build the frontend manually with:"
    echo "  cd frontend && npm install && npm run build"
fi

echo "Setup complete!"
echo "Run the application with: cd backend && python main.py"