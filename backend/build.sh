#!/bin/bash

echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "Building frontend..."
cd ../frontend
npm install
npm run build