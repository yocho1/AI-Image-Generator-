import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ai_image_generator.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-fallback-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
    JWT_COOKIE_CSRF_PROTECT = False
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    REQUEST_COOLDOWN = 60  # seconds between Gemini requests