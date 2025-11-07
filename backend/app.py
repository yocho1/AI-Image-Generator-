import os
import time
import hashlib
import random
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Simple configuration - completely disable CSRF
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'fallback-jwt-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_CSRF_IN_COOKIES'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    images = db.relationship('GeneratedImage', backref='user', lazy=True)

# Generated Image Model
class GeneratedImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_prompt = db.Column(db.Text, nullable=False)
    improved_prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    ai_enhanced = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Configure Gemini API
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = False
RATE_LIMIT_RESET = 0
LAST_REQUEST_TIME = 0
REQUEST_COOLDOWN = 60

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        available_models = genai.list_models()
        working_model = None
        
        for model in available_models:
            if 'generateContent' in model.supported_generation_methods:
                working_model = model.name
                break
        
        if working_model:
            GEMINI_AVAILABLE = True
            print(f"SUCCESS: Gemini API configured with model: {working_model}")
        else:
            print("ERROR: No available Gemini models found")
            
    except Exception as e:
        print(f"WARNING: Gemini API configuration failed: {e}")
        GEMINI_AVAILABLE = False
else:
    print("WARNING: GEMINI_API_KEY not found in .env")

# Create tables
with app.app_context():
    db.create_all()

# Custom JWT decorator that bypasses CSRF
def jwt_required_custom(fn):
    from functools import wraps
    
    @wraps(fn)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            # If there's a CSRF error, try to extract user ID from token anyway
            if "CSRF" in str(e) or "csrf" in str(e).lower():
                try:
                    auth_header = request.headers.get('Authorization', '')
                    if auth_header.startswith('Bearer '):
                        token = auth_header[7:]
                        from flask_jwt_extended.utils import decode_token
                        decoded_token = decode_token(token)
                        user_id = decoded_token['sub']
                        print(f"DEBUG: CSRF error for user {user_id}, but proceeding anyway")
                        # Manually set the user identity
                        from flask import g
                        g.get_jwt_identity = lambda: user_id
                        return fn(*args, **kwargs)
                except:
                    pass
            # Re-raise the original error
            raise e
    return decorated_function

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not username or not email or not password:
            return jsonify({'error': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Create access token - convert user ID to string for JWT subject
        access_token = create_access_token(
            identity=str(user.id),  # Convert to string
            additional_claims={"csrf": False}
        )

        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        email = data.get('email', '').strip().lower()
        password = data.get('password', '').strip()

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            # Create access token - convert user ID to string for JWT subject
            access_token = create_access_token(
                identity=str(user.id),  # Convert to string
                additional_claims={"csrf": False}
            )
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })
        else:
            return jsonify({'error': 'Invalid email or password'}), 401

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

# Profile route
@app.route('/api/profile', methods=['GET'])
@jwt_required_custom
def get_profile():
    try:
        user_id_str = get_jwt_identity()  # This returns string
        user_id = int(user_id_str)  # Convert back to int for database query
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            }
        })
    except Exception as e:
        print(f"Profile error: {e}")
        return jsonify({'error': 'Failed to get profile'}), 500

# Generate Endpoint with custom JWT handling
@app.route("/api/generate", methods=["POST"])
@jwt_required_custom
def generate_image():
    try:
        user_id_str = get_jwt_identity()  # This returns string
        user_id = int(user_id_str)  # Convert back to int for database query
        print(f"DEBUG: User {user_id} is generating image")
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        prompt = data.get("prompt", "").strip()

        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        # Step 1: Improve the prompt
        improved_prompt = prompt
        ai_enhanced = False
        gemini_used = False
        
        if GEMINI_AVAILABLE and can_make_gemini_request():
            improved_prompt = improve_prompt_with_gemini(prompt)
            ai_enhanced = True
            gemini_used = True
        else:
            improved_prompt = improve_prompt_fallback(prompt)
            if not GEMINI_AVAILABLE:
                print(f"Using fallback (Gemini unavailable): '{prompt}' -> '{improved_prompt}'")
            else:
                print(f"Using fallback (in cooldown): '{prompt}' -> '{improved_prompt}'")

        # Step 2: Generate image URL
        image_url = get_reliable_image_url(improved_prompt)

        # Step 3: Save to user's history
        generated_image = GeneratedImage(
            user_id=user_id,
            original_prompt=prompt,
            improved_prompt=improved_prompt,
            image_url=image_url,
            ai_enhanced=ai_enhanced
        )
        db.session.add(generated_image)
        db.session.commit()

        return jsonify({
            "success": True,
            "original_prompt": prompt,
            "improved_prompt": improved_prompt,
            "image_url": image_url,
            "ai_enhanced": ai_enhanced,
            "gemini_used": gemini_used,
            "gemini_available": GEMINI_AVAILABLE,
            "image_id": generated_image.id,
            "message": "Image generated with AI-enhanced prompt" if ai_enhanced else "Image generated with basic enhancement"
        })

    except Exception as e:
        print(f"GENERATION ERROR: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# User's Image History
@app.route('/api/images', methods=['GET'])
@jwt_required_custom
def get_user_images():
    try:
        user_id_str = get_jwt_identity()  # This returns string
        user_id = int(user_id_str)  # Convert back to int for database query
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        images = GeneratedImage.query.filter_by(user_id=user_id)\
            .order_by(GeneratedImage.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'images': [{
                'id': img.id,
                'original_prompt': img.original_prompt,
                'improved_prompt': img.improved_prompt,
                'image_url': img.image_url,
                'ai_enhanced': img.ai_enhanced,
                'created_at': img.created_at.isoformat()
            } for img in images.items],
            'total': images.total,
            'pages': images.pages,
            'current_page': page
        })
    except Exception as e:
        print(f"Images error: {e}")
        return jsonify({'error': 'Failed to get images'}), 500

# Public routes
@app.route("/")
def home():
    return jsonify({"message": "AI Image Generator Backend with User System is running!"})

@app.route("/api/health")
def health():
    global LAST_REQUEST_TIME, RATE_LIMIT_RESET
    cooldown_remaining = max(0, REQUEST_COOLDOWN - (time.time() - LAST_REQUEST_TIME))
    rate_limit_remaining = max(0, RATE_LIMIT_RESET - time.time())
    
    return jsonify({
        "status": "healthy", 
        "gemini_available": GEMINI_AVAILABLE,
        "cooldown_remaining_seconds": round(cooldown_remaining, 1),
        "rate_limit_remaining_seconds": round(rate_limit_remaining, 1),
        "requests_per_minute_limit": f"~{60//REQUEST_COOLDOWN}",
        "message": "Optimized for free tier usage"
    })

# Helper functions (keep the same as before)
def get_working_model():
    try:
        available_models = genai.list_models()
        for model in available_models:
            model_name = model.name
            if 'generateContent' in model.supported_generation_methods:
                return model_name
    except:
        pass
    return "gemini-1.0-pro"

def can_make_gemini_request():
    global LAST_REQUEST_TIME, RATE_LIMIT_RESET
    current_time = time.time()
    
    if current_time < RATE_LIMIT_RESET:
        return False
    
    if current_time - LAST_REQUEST_TIME >= REQUEST_COOLDOWN:
        LAST_REQUEST_TIME = current_time
        return True
    return False

def improve_prompt_with_gemini(prompt):
    global RATE_LIMIT_RESET
    
    try:
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        
        prompt_instruction = f"Improve this image description in 5-8 words: {prompt}"
        
        response = model.generate_content(
            prompt_instruction,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=30,
                temperature=0.3,
            ),
            request_options={"timeout": 15}
        )
        
        improved_prompt = response.text.strip() if response.text else prompt
        improved_prompt = improved_prompt.replace('"', '').replace("**", "")
        print(f"Gemini improved: '{prompt}' -> '{improved_prompt}'")
        return improved_prompt
        
    except Exception as e:
        error_str = str(e)
        print(f"Gemini API error: {error_str}")
        
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            global GEMINI_AVAILABLE
            GEMINI_AVAILABLE = False
            RATE_LIMIT_RESET = time.time() + 120
            print("Gemini disabled due to rate limits. Retry in 2 minutes.")
        elif "503" in error_str or "unavailable" in error_str.lower():
            RATE_LIMIT_RESET = time.time() + 30
            print("Service unavailable. Retry in 30 seconds.")
        
        return prompt

def improve_prompt_fallback(prompt):
    descriptive_words = {
        "cute": ["adorable", "charming", "sweet"],
        "baby": ["infant", "newborn", "little one"],
        "cat": ["feline", "kitten", "cat"],
        "dog": ["puppy", "canine", "dog"],
        "photo": ["professional photography", "high-quality image", "crystal clear"],
        "drawing": ["artistic illustration", "detailed artwork", "digital painting"],
        "landscape": ["breathtaking landscape", "scenic view", "natural beauty"],
        "portrait": ["professional portrait", "character study", "expressive face"],
        "panda": ["giant panda", "panda bear", "black and white bear"]
    }
    
    improved = prompt
    
    for basic_word, enhanced_options in descriptive_words.items():
        if basic_word in improved.lower():
            replacement = random.choice(enhanced_options)
            improved = improved.replace(basic_word, replacement)
            break
    
    quality_terms = ["high resolution", "detailed", "sharp focus", "well-lit", "professional"]
    if not any(term in improved.lower() for term in quality_terms):
        improved += f", {random.choice(quality_terms)}"
    
    return improved

def get_reliable_image_url(prompt):
    prompt_lower = prompt.lower()
    
    if any(word in prompt_lower for word in ['cat', 'kitten', 'feline']):
        cat_ids = [237, 219, 222, 257, 96]
        return f"https://picsum.photos/id/{random.choice(cat_ids)}/512/512"
    elif any(word in prompt_lower for word in ['dog', 'puppy', 'canine']):
        dog_ids = [1062, 1074, 1080, 1081, 1084]
        return f"https://picsum.photos/id/{random.choice(dog_ids)}/512/512"
    elif any(word in prompt_lower for word in ['baby', 'child', 'infant']):
        people_ids = [1005, 1011, 1012, 1018, 1025]
        return f"https://picsum.photos/id/{random.choice(people_ids)}/512/512"
    elif any(word in prompt_lower for word in ['panda', 'bear']):
        animal_ids = [1024, 1031, 1035, 1036, 1039]
        return f"https://picsum.photos/id/{random.choice(animal_ids)}/512/512"
    elif any(word in prompt_lower for word in ['landscape', 'mountain', 'nature']):
        nature_ids = [1015, 1016, 1018, 1020, 1021, 1022, 1023, 1028]
        return f"https://picsum.photos/id/{random.choice(nature_ids)}/512/512"
    elif any(word in prompt_lower for word in ['portrait', 'person', 'face']):
        portrait_ids = [1005, 1009, 1011, 1012, 1019, 1027]
        return f"https://picsum.photos/id/{random.choice(portrait_ids)}/512/512"
    else:
        seed = hashlib.md5(prompt.encode()).hexdigest()[:10]
        return f"https://picsum.photos/seed/{seed}/512/512"

# Background task
def check_gemini_availability():
    global GEMINI_AVAILABLE, RATE_LIMIT_RESET
    if not GEMINI_AVAILABLE and GEMINI_KEY and time.time() >= RATE_LIMIT_RESET:
        try:
            model_name = get_working_model()
            model = genai.GenerativeModel(model_name)
            test_response = model.generate_content("test", 
                generation_config=genai.types.GenerationConfig(max_output_tokens=5),
                request_options={"timeout": 5}
            )
            GEMINI_AVAILABLE = True
            print("Gemini API is available again!")
        except Exception as e:
            print(f"Gemini still unavailable: {e}")

import threading
def periodic_availability_check():
    while True:
        time.sleep(60)
        check_gemini_availability()

if GEMINI_KEY:
    availability_thread = threading.Thread(target=periodic_availability_check, daemon=True)
    availability_thread.start()

if __name__ == "__main__":
    print("STARTING: AI Image Generator Backend with User System...")
    print(f"GEMINI AVAILABLE: {GEMINI_AVAILABLE}")
    print(f"REQUEST COOLDOWN: {REQUEST_COOLDOWN} seconds")
    print(f"MAX REQUESTS/MINUTE: {60//REQUEST_COOLDOWN}")
    app.run(debug=True, host="127.0.0.1", port=5002)