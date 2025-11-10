import os
import time
import threading
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models.models import db
from services.gemini_service import GeminiService
from controllers.auth_controller import AuthController
from controllers.image_controller import ImageController
from utils.decorators import jwt_required_custom


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Flexible CORS for production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    if os.getenv('RAILWAY_STATIC_URL'):  # Railway provides this
        CORS_ORIGINS.append(os.getenv('RAILWAY_STATIC_URL'))
    
    CORS(app, resources={r"/api/*": {"origins": CORS_ORIGINS}})
    
    # Initialize services
    gemini_service = GeminiService()
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Health check endpoint
    @app.route('/')
    def home():
        return jsonify({"message": "AI Image Generator Backend is running!"})
    
    @app.route('/api/health')
    def health():
        cooldown_remaining = max(0, gemini_service.request_cooldown - (time.time() - gemini_service.last_request_time))
        rate_limit_remaining = max(0, gemini_service.rate_limit_reset - time.time())
        
        return jsonify({
            "status": "healthy", 
            "gemini_available": gemini_service.available,
            "cooldown_remaining_seconds": round(cooldown_remaining, 1),
            "rate_limit_remaining_seconds": round(rate_limit_remaining, 1),
            "requests_per_minute_limit": f"~{60//gemini_service.request_cooldown}",
            "message": "Optimized for free tier usage"
        })
    
    # Authentication routes
    @app.route('/api/register', methods=['POST'])
    def register():
        return AuthController.register()
    
    @app.route('/api/login', methods=['POST'])
    def login():
        return AuthController.login()
    
    @app.route('/api/profile', methods=['GET'])
    @jwt_required_custom
    def profile():
        return AuthController.get_profile(g.user_id)
    
    # Image routes
    @app.route('/api/generate', methods=['POST'])
    @jwt_required_custom
    def generate():
        return ImageController.generate_image(g.user_id)
    
    @app.route('/api/images', methods=['GET'])
    @jwt_required_custom
    def get_images():
        return ImageController.get_user_images(g.user_id)
    
    # Favorite routes
    @app.route('/api/favorites', methods=['POST'])
    @jwt_required_custom
    def add_favorite():
        return ImageController.add_favorite(g.user_id)
    
    @app.route('/api/favorites/<int:image_id>', methods=['DELETE'])
    @jwt_required_custom
    def remove_favorite(image_id):
        return ImageController.remove_favorite(g.user_id, image_id)
    
    @app.route('/api/favorites', methods=['GET'])
    @jwt_required_custom
    def get_favorites():
        return ImageController.get_favorites(g.user_id)
    
    # Stats route
    @app.route('/api/stats', methods=['GET'])
    @jwt_required_custom
    def get_stats():
        return ImageController.get_stats(g.user_id)
    
    # Background task for Gemini availability check
    def periodic_availability_check():
        while True:
            time.sleep(60)
            if not gemini_service.available and gemini_service.rate_limit_reset <= time.time():
                gemini_service._initialize_gemini()
    
    if Config.GEMINI_API_KEY:
        availability_thread = threading.Thread(target=periodic_availability_check, daemon=True)
        availability_thread.start()
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("STARTING: AI Image Generator Backend with MVC Architecture...")
    print(f"GEMINI AVAILABLE: {GeminiService().available}")
    app.run(debug=True, host="127.0.0.1", port=5002)