#!/bin/bash

echo "Installing backend dependencies with optimized settings..."

cd backend

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install with specific flags to use precompiled wheels
pip install --use-pep517 --only-binary=:all: --no-cache-dir -r requirements.txt

# If the above fails, try without --only-binary for grpcio
if [ $? -ne 0 ]; then
    echo "Retrying with source compilation for grpcio..."
    pip install --use-pep517 --no-cache-dir -r requirements.txt
fi

echo "Installation complete!"