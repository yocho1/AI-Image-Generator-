AI Image Generator 🎨🤖
A full-stack AI-powered image generator that transforms your text descriptions into stunning visual concepts. Built with React frontend and Flask backend, powered by Google Gemini AI for intelligent prompt enhancement.

https://img.shields.io/badge/AI-Powered-blue https://img.shields.io/badge/React-18.2.0-blue https://img.shields.io/badge/Flask-2.3.3-green https://img.shields.io/badge/Tailwind-CSS-38B2AC

✨ Features
AI-Powered Prompt Enhancement: Uses Google Gemini AI to transform basic descriptions into vivid, detailed image prompts

Beautiful Modern UI: Responsive React interface with Tailwind CSS styling

Smart Rate Limiting: Optimized for free tier API usage with automatic cooldowns

Category-Based Images: Generates relevant placeholder images based on prompt content

Real-time Feedback: Live status updates and loading indicators

Prompt Evolution: Compare original and AI-enhanced prompts side by side

🛠️ Tech Stack
Frontend
React 18 - Modern user interface

Tailwind CSS v3 - Utility-first CSS framework

Lucide React - Beautiful icons

Backend
Flask - Python web framework

Google Gemini AI - Advanced prompt enhancement

Flask-CORS - Cross-origin resource sharing

python-dotenv - Environment management

🚀 Quick Start
Prerequisites
Node.js (v16 or higher)

Python (v3.8 or higher)

Google Gemini API key

Installation
Clone the repository

git clone https://github.com/YOUR_USERNAME/AI-Image-Generator.git
cd AI-Image-Generator
Backend Setup

cd backend
pip install -r requirements.txt
Frontend Setup

cd ../frontend
npm install
Environment Configuration

# Backend - Create .env file in backend directory

echo "GEMINI_API_KEY=your_gemini_api_key_here" > backend/.env

# Frontend - Create .env file in frontend directory

echo "PORT=3001" > frontend/.env

Running the Application
Start the Backend Server

cd backend
python app.py
Backend runs on http://127.0.0.1:5002

Start the Frontend Development Server

cd frontend
npm start
Frontend runs on http://localhost:3001
