import os
import time
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
LAST_REQUEST_TIME = 0
REQUEST_COOLDOWN = 30  # 30 seconds between requests to stay within limits

if GEMINI_KEY:
    try:
        genai.configure(api_key=GEMINI_KEY)
        GEMINI_AVAILABLE = True
        print("SUCCESS: Gemini API configured (working within free tier limits)")
    except Exception as e:
        print(f"WARNING: Gemini API configuration failed: {e}")
else:
    print("WARNING: GEMINI_API_KEY not found in .env")

def can_make_gemini_request():
    """Check if we can make a Gemini request without hitting rate limits"""
    global LAST_REQUEST_TIME
    current_time = time.time()
    
    if current_time - LAST_REQUEST_TIME >= REQUEST_COOLDOWN:
        LAST_REQUEST_TIME = current_time
        return True
    return False

def improve_prompt_with_gemini(prompt):
    """Use Gemini to improve the prompt with optimized usage"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        
        # Very concise prompt to minimize token usage
        prompt_instruction = f"Make this image prompt more vivid: {prompt}. Max 10 words."
        
        response = model.generate_content(
            prompt_instruction,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=50,  # Limit output to save tokens
                temperature=0.7
            ),
            request_options={"timeout": 10}
        )
        
        improved_prompt = response.text.strip() if response.text else prompt
        print(f"Gemini improved: '{prompt}' -> '{improved_prompt}'")
        return improved_prompt
        
    except Exception as e:
        error_str = str(e)
        print(f"Gemini API error: {error_str}")
        
        # If it's a quota error, disable Gemini for a while
        if "429" in error_str or "quota" in error_str.lower():
            global GEMINI_AVAILABLE
            GEMINI_AVAILABLE = False
            print("Gemini disabled due to rate limits. Will retry later.")
        
        return prompt

def improve_prompt_fallback(prompt):
    """Fallback prompt improvement without Gemini"""
    # Simple but effective improvements
    descriptive_words = {
        "cute": ["adorable", "charming", "sweet"],
        "baby": ["infant", "newborn", "little one"],
        "photo": ["professional photography", "high-quality image", "crystal clear"],
        "drawing": ["artistic illustration", "detailed artwork", "digital painting"],
        "landscape": ["breathtaking landscape", "scenic view", "natural beauty"],
        "portrait": ["professional portrait", "character study", "expressive face"]
    }
    
    improved = prompt
    
    # Add quality descriptors
    quality_terms = ["high resolution", "detailed", "sharp focus", "well-lit"]
    if not any(term in improved.lower() for term in quality_terms):
        improved += f", {quality_terms[0]}"
    
    # Enhance specific terms
    for basic_word, enhanced_options in descriptive_words.items():
        if basic_word in improved.lower():
            # Replace with a random enhanced option
            import random
            replacement = random.choice(enhanced_options)
            improved = improved.replace(basic_word, replacement)
            break
    
    return improved

@app.route("/")
def home():
    return jsonify({"message": "AI Image Generator Backend is running with optimized Gemini usage!"})

@app.route("/health")
def health():
    global LAST_REQUEST_TIME
    cooldown_remaining = max(0, REQUEST_COOLDOWN - (time.time() - LAST_REQUEST_TIME))
    
    return jsonify({
        "status": "healthy", 
        "gemini_available": GEMINI_AVAILABLE,
        "cooldown_remaining_seconds": round(cooldown_remaining, 1),
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
        # Step 1: Improve the prompt (use Gemini if available and not in cooldown)
        improved_prompt = prompt
        ai_enhanced = False
        
        if GEMINI_AVAILABLE and can_make_gemini_request():
            improved_prompt = improve_prompt_with_gemini(prompt)
            ai_enhanced = True
        else:
            improved_prompt = improve_prompt_fallback(prompt)
            if not GEMINI_AVAILABLE:
                print(f"Using fallback (Gemini unavailable): '{prompt}' -> '{improved_prompt}'")
            else:
                print(f"Using fallback (in cooldown): '{prompt}' -> '{improved_prompt}'")

        # Step 2: Generate image URL (placeholder - you can integrate real image APIs later)
        image_url = f"https://picsum.photos/seed/{hash(improved_prompt) % 10000}/512/512"

        return jsonify({
            "success": True,
            "original_prompt": prompt,
            "improved_prompt": improved_prompt,
            "image_url": image_url,
            "ai_enhanced": ai_enhanced,
            "gemini_available": GEMINI_AVAILABLE,
            "message": "Ready for real image API integration"
        })

    except Exception as e:
        print(f"GENERATION ERROR: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Background task to periodically check if Gemini is available again
def check_gemini_availability():
    global GEMINI_AVAILABLE
    if not GEMINI_AVAILABLE and GEMINI_KEY:
        try:
            # Simple test to see if API is working again
            model = genai.GenerativeModel("gemini-pro")
            test_response = model.generate_content("test", request_options={"timeout": 5})
            GEMINI_AVAILABLE = True
            print("Gemini API is available again!")
        except:
            pass

# Check availability every 5 minutes
import threading
def periodic_availability_check():
    while True:
        time.sleep(300)  # 5 minutes
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
    app.run(debug=True, host="127.0.0.1", port=5002)