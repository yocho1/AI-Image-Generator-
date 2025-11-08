import time
import random
import hashlib
import google.generativeai as genai
from config import Config

class GeminiService:
    def __init__(self):
        self.available = False
        self.rate_limit_reset = 0
        self.last_request_time = 0
        self.request_cooldown = Config.REQUEST_COOLDOWN
        
        if Config.GEMINI_API_KEY:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            available_models = genai.list_models()
            
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    self.available = True
                    self.model_name = model.name
                    print(f"SUCCESS: Gemini API configured with model: {self.model_name}")
                    break
            else:
                print("ERROR: No available Gemini models found")
                
        except Exception as e:
            print(f"WARNING: Gemini API configuration failed: {e}")
            self.available = False
    
    def can_make_request(self):
        current_time = time.time()
        if current_time < self.rate_limit_reset:
            return False
        if current_time - self.last_request_time >= self.request_cooldown:
            self.last_request_time = current_time
            return True
        return False
    
    def improve_prompt(self, prompt):
        if not self.available or not self.can_make_request():
            return self._improve_prompt_fallback(prompt)
        
        try:
            model = genai.GenerativeModel(self.model_name)
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
            
            if "429" in error_str or "quota" in error_str.lower():
                self.available = False
                self.rate_limit_reset = time.time() + 120
                print("Gemini disabled due to rate limits. Retry in 2 minutes.")
            
            return self._improve_prompt_fallback(prompt)
    
    def _improve_prompt_fallback(self, prompt):
        descriptive_words = {
            "cute": ["adorable", "charming", "sweet"],
            "baby": ["infant", "newborn", "little one"],
            "cat": ["feline", "kitten", "cat"],
            "dog": ["puppy", "canine", "dog"],
            "photo": ["professional photography", "high-quality image", "crystal clear"],
            "drawing": ["artistic illustration", "detailed artwork", "digital painting"],
            "landscape": ["breathtaking landscape", "scenic view", "natural beauty"],
            "portrait": ["professional portrait", "character study", "expressive face"],
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
    
    def get_image_url(self, prompt):
        prompt_lower = prompt.lower()
        
        image_categories = {
            'cat': [237, 219, 222, 257, 96],
            'dog': [1062, 1074, 1080, 1081, 1084],
            'baby': [1005, 1011, 1012, 1018, 1025],
            'panda': [1024, 1031, 1035, 1036, 1039],
            'landscape': [1015, 1016, 1018, 1020, 1021, 1022, 1023, 1028],
            'portrait': [1005, 1009, 1011, 1012, 1019, 1027]
        }
        
        for category, ids in image_categories.items():
            if any(word in prompt_lower for word in [category] + self._get_synonyms(category)):
                return f"https://picsum.photos/id/{random.choice(ids)}/512/512"
        
        seed = hashlib.md5(prompt.encode()).hexdigest()[:10]
        return f"https://picsum.photos/seed/{seed}/512/512"
    
    def _get_synonyms(self, word):
        synonyms = {
            'cat': ['kitten', 'feline'],
            'dog': ['puppy', 'canine'],
            'baby': ['child', 'infant'],
            'panda': ['bear'],
            'landscape': ['mountain', 'nature', 'scenery'],
            'portrait': ['person', 'face', 'people']
        }
        return synonyms.get(word, [])