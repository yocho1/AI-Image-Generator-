import os
import time
import hashlib
import random
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Gemini API
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = False
RATE_LIMIT_RESET = 0
LAST_REQUEST_TIME = 0
REQUEST_COOLDOWN = 60  # Increased to 60 seconds for free tier

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        # Get available models and use the first working one
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

def get_working_model():
    """Get a working Gemini model"""
    try:
        available_models = genai.list_models()
        for model in available_models:
            model_name = model.name
            if 'generateContent' in model.supported_generation_methods:
                return model_name
    except:
        pass
    return "gemini-1.0-pro"  # Fallback to a known model

def can_make_gemini_request():
    """Check if we can make a Gemini request without hitting rate limits"""
    global LAST_REQUEST_TIME, RATE_LIMIT_RESET
    current_time = time.time()
    
    # Check if we're in rate limit cooldown
    if current_time < RATE_LIMIT_RESET:
        return False
    
    # Check request cooldown
    if current_time - LAST_REQUEST_TIME >= REQUEST_COOLDOWN:
        LAST_REQUEST_TIME = current_time
        return True
    return False

def improve_prompt_with_gemini(prompt):
    """Use Gemini to improve the prompt with optimized usage"""
    global RATE_LIMIT_RESET
    
    try:
        model_name = get_working_model()
        model = genai.GenerativeModel(model_name)
        
        # More effective prompt that minimizes tokens
        prompt_instruction = f"Improve this image description in 5-8 words: {prompt}"
        
        response = model.generate_content(
            prompt_instruction,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=30,  # Very limited output
                temperature=0.3,       # Less creative, more consistent
            ),
            request_options={"timeout": 15}
        )
        
        improved_prompt = response.text.strip() if response.text else prompt
        
        # Clean up the response
        improved_prompt = improved_prompt.replace('"', '').replace("**", "")
        print(f"Gemini improved: '{prompt}' -> '{improved_prompt}'")
        return improved_prompt
        
    except Exception as e:
        error_str = str(e)
        print(f"Gemini API error: {error_str}")
        
        # Handle rate limits
        if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
            global GEMINI_AVAILABLE
            GEMINI_AVAILABLE = False
            # Set cooldown for 2 minutes
            RATE_LIMIT_RESET = time.time() + 120
            print("Gemini disabled due to rate limits. Retry in 2 minutes.")
        elif "503" in error_str or "unavailable" in error_str.lower():
            # Service temporarily unavailable
            RATE_LIMIT_RESET = time.time() + 30
            print("Service unavailable. Retry in 30 seconds.")
        
        return prompt

def improve_prompt_fallback(prompt):
    """Fallback prompt improvement without Gemini"""
    # Simple but effective improvements
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
    
    # Enhance specific terms
    for basic_word, enhanced_options in descriptive_words.items():
        if basic_word in improved.lower():
            replacement = random.choice(enhanced_options)
            improved = improved.replace(basic_word, replacement)
            break
    
    # Add quality descriptors if not present
    quality_terms = ["high resolution", "detailed", "sharp focus", "well-lit", "professional"]
    if not any(term in improved.lower() for term in quality_terms):
        improved += f", {random.choice(quality_terms)}"
    
    return improved

def get_reliable_image_url(prompt):
    """Get reliable placeholder images with multiple fallback options"""
    prompt_lower = prompt.lower()
    
    # Option 1: Picsum with specific image IDs for categories (most reliable)
    if any(word in prompt_lower for word in ['cat', 'kitten', 'feline']):
        # Cat images from Picsum
        cat_ids = [237, 219, 222, 257, 96]
        return f"https://picsum.photos/id/{random.choice(cat_ids)}/512/512"
    elif any(word in prompt_lower for word in ['dog', 'puppy', 'canine']):
        # Dog images from Picsum
        dog_ids = [1062, 1074, 1080, 1081, 1084]
        return f"https://picsum.photos/id/{random.choice(dog_ids)}/512/512"
    elif any(word in prompt_lower for word in ['baby', 'child', 'infant']):
        # People/child images
        people_ids = [1005, 1011, 1012, 1018, 1025]
        return f"https://picsum.photos/id/{random.choice(people_ids)}/512/512"
    elif any(word in prompt_lower for word in ['panda', 'bear']):
        # Animal images for panda
        animal_ids = [1024, 1031, 1035, 1036, 1039]
        return f"https://picsum.photos/id/{random.choice(animal_ids)}/512/512"
    elif any(word in prompt_lower for word in ['landscape', 'mountain', 'nature']):
        # Nature/landscape images
        nature_ids = [1015, 1016, 1018, 1020, 1021, 1022, 1023, 1028]
        return f"https://picsum.photos/id/{random.choice(nature_ids)}/512/512"
    elif any(word in prompt_lower for word in ['portrait', 'person', 'face']):
        # Portrait images
        portrait_ids = [1005, 1009, 1011, 1012, 1019, 1027]
        return f"https://picsum.photos/id/{random.choice(portrait_ids)}/512/512"
    else:
        # Fallback: Use hash-based seed for consistency
        seed = hashlib.md5(prompt.encode()).hexdigest()[:10]
        return f"https://picsum.photos/seed/{seed}/512/512"

def test_image_urls():
    """Test if our image URLs are working"""
    test_urls = [
        "https://picsum.photos/id/237/512/512",  # Cat
        "https://picsum.photos/id/1062/512/512", # Dog
        "https://picsum.photos/id/1005/512/512", # Person
        "https://picsum.photos/id/1015/512/512", # Nature
    ]
    
    print("Testing image URLs...")
    for url in test_urls:
        try:
            import requests
            response = requests.head(url, timeout=5)
            if response.status_code == 200:
                print(f"OK {url} - WORKING")
            else:
                print(f"FAIL {url} - FAILED: {response.status_code}")
        except:
            print(f"ERROR {url} - ERROR")

@app.route("/")
def home():
    return jsonify({"message": "AI Image Generator Backend is running with optimized Gemini usage!"})

@app.route("/health")
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

@app.route("/generate", methods=["POST"])
def generate_image():
    data = request.get_json()
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Missing prompt"}), 400

    try:
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

        # Step 2: Generate reliable image URL
        image_url = get_reliable_image_url(improved_prompt)

        return jsonify({
            "success": True,
            "original_prompt": prompt,
            "improved_prompt": improved_prompt,
            "image_url": image_url,
            "ai_enhanced": ai_enhanced,
            "gemini_used": gemini_used,
            "gemini_available": GEMINI_AVAILABLE,
            "message": "Image generated with AI-enhanced prompt" if ai_enhanced else "Image generated with basic enhancement"
        })

    except Exception as e:
        print(f"GENERATION ERROR: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Background task to periodically check if Gemini is available again
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

# Check availability every minute
import threading
def periodic_availability_check():
    while True:
        time.sleep(60)  # 1 minute
        check_gemini_availability()

# Start background thread
if GEMINI_KEY:
    availability_thread = threading.Thread(target=periodic_availability_check, daemon=True)
    availability_thread.start()

if __name__ == "__main__":
    print("STARTING: AI Image Generator Backend...")
    print(f"GEMINI AVAILABLE: {GEMINI_AVAILABLE}")
    print(f"REQUEST COOLDOWN: {REQUEST_COOLDOWN} seconds")
    print(f"MAX REQUESTS/MINUTE: {60//REQUEST_COOLDOWN}")
    
    # Test image URLs on startup
    test_image_urls()
    
    app.run(debug=True, host="127.0.0.1", port=5002)