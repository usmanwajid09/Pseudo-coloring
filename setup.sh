#!/bin/bash

echo "========================================"
echo " Image Colorization App - Setup Script"
echo "========================================"
echo ""

echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.7+ first"
    exit 1
fi

python3 --version
echo ""

echo "Installing required packages..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies!"
    echo "Try running: python3 -m pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "To run the application, type:"
echo "  python3 pseudo_color_app.py"
echo ""


