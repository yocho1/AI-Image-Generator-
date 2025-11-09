import os
import base64
import time
import requests
from config import Config

class StabilityAIService:
    def __init__(self):
        self.available = False
        self.last_request_time = 0
        self.request_cooldown = 3
        self.api_key = os.getenv('STABILITY_API_KEY')
        self.api_host = 'https://api.stability.ai'
        
        if self.api_key:
            self._initialize_stability()
    
    def _initialize_stability(self):
        """Initialize Stability.ai connection"""
        try:
            # Test the API key
            response = requests.get(
                f"{self.api_host}/v1/engines/list",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                self.available = True
                engines = response.json()
                print("SUCCESS: Stability.ai service initialized!")
                print(f"Available engines: {[engine['id'] for engine in engines]}")
            else:
                print(f"Stability.ai connection failed: {response.status_code}")
                print(f"Response: {response.text}")
                self.available = False
                
        except Exception as e:
            print(f"Stability.ai initialization failed: {e}")
            self.available = False
    
    def can_make_request(self):
        """Basic rate limiting"""
        current_time = time.time()
        if current_time - self.last_request_time >= self.request_cooldown:
            self.last_request_time = current_time
            return True
        return False
    
    def generate_image(self, prompt, style='realistic'):
        """
        Generate real AI images using Stability.ai
        """
        if not self.available or not self.can_make_request():
            print("Stability.ai not available - using enhanced fallback")
            return self._get_enhanced_fallback_image(prompt, style)
        
        try:
            # Enhance prompt with style
            enhanced_prompt = self._enhance_prompt_for_style(prompt, style)
            print(f"Generating with Stability.ai: {enhanced_prompt}")
            
            # Generate the image
            image_url = self._generate_with_stability(enhanced_prompt)
            
            if image_url and image_url.startswith('data:image'):
                print("REAL AI image generated with Stability.ai!")
                return image_url
            else:
                print("Stability.ai returned no image data, using fallback")
                return self._get_enhanced_fallback_image(prompt, style)
                
        except Exception as e:
            print(f"Stability.ai generation error: {e}")
            return self._get_enhanced_fallback_image(prompt, style)
    
    def _enhance_prompt_for_style(self, prompt, style):
        """Enhance prompt based on selected style"""
        style_prompts = {
            'realistic': 'photorealistic, highly detailed, professional photography, 8K resolution, sharp focus',
            'anime': 'anime style, Japanese animation, vibrant colors, manga art style, cel shading',
            'painting': 'oil painting, artistic, brush strokes, masterpiece, gallery quality, textured',
            'cartoon': 'cartoon style, animated, bright colors, simple lines, family friendly, fun',
            'minimalist': 'minimalist, simple, clean lines, modern art, geometric, abstract'
        }
        
        style_desc = style_prompts.get(style, 'high quality, detailed')
        return f"{prompt}, {style_desc}"
    
    def _generate_with_stability(self, prompt):
        """
        Generate image using Stability.ai REST API with multiple engine fallbacks
        """
        try:
            # List of engines to try in order
            engines_to_try = [
                ("stable-diffusion-v1-6", 512, 512),  # SD 1.6 supports 512x512
                ("stable-diffusion-512-v2-1", 512, 512),  # Specifically for 512x512
                ("stable-diffusion-xl-1024-v1-0", 1024, 1024),  # SDXL requires 1024x1024
            ]
            
            for engine_id, width, height in engines_to_try:
                print(f"Trying engine: {engine_id} with {width}x{height}")
                
                response = requests.post(
                    f"{self.api_host}/v1/generation/{engine_id}/text-to-image",
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "text_prompts": [{"text": prompt}],
                        "cfg_scale": 7,
                        "height": height,
                        "width": width,
                        "samples": 1,
                        "steps": 30,
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"SUCCESS: Image generated with engine {engine_id}")
                    return self._process_stability_response(data)
                else:
                    print(f"Engine {engine_id} failed: {response.status_code}")
                    if response.status_code != 404:  # Don't print details for 404 (engine not found)
                        print(f"Error: {response.text}")
                    continue  # Try next engine
                    
            print("All engines failed or not available")
            return None
            
        except Exception as e:
            print(f"Stability.ai API call failed: {e}")
            return None
    
    def _process_stability_response(self, data):
        """Process Stability.ai response and return image URL"""
        try:
            for image in data["artifacts"]:
                image_binary = base64.b64decode(image["base64"])
                image_base64 = base64.b64encode(image_binary).decode('utf-8')
                image_url = f"data:image/png;base64,{image_base64}"
                return image_url
        except Exception as e:
            print(f"Error processing Stability.ai response: {e}")
        
        return None
    
    def _get_enhanced_fallback_image(self, prompt, style):
        """Enhanced fallback with better image matching"""
        import hashlib
        import random
        
        # Image database with categories
        image_database = {
            'cat': [237, 219, 222, 257, 96, 144, 145],
            'dog': [1062, 1074, 1080, 1081, 1084, 200, 201],
            'baby': [1005, 1011, 1012, 1018, 1025, 300, 301],
            'landscape': [1015, 1016, 1018, 1020, 1021, 1022, 1023, 1028],
            'portrait': [1005, 1009, 1011, 1012, 1019, 1027, 1000, 1001],
            'art': [100, 101, 102, 103, 104, 105, 106],
        }
        
        prompt_lower = prompt.lower()
        
        # Find best matching category
        for category, ids in image_database.items():
            if any(word in prompt_lower for word in [category] + self._get_synonyms(category)):
                selected_id = random.choice(ids)
                print(f"Using enhanced fallback for '{category}': image {selected_id}")
                return f"https://picsum.photos/id/{selected_id}/512/512"
        
        # Final fallback
        seed = hashlib.md5(f"{prompt}_{style}".encode()).hexdigest()[:10]
        return f"https://picsum.photos/seed/{seed}/512/512"
    
    def _get_synonyms(self, word):
        synonyms = {
            'cat': ['kitten', 'feline', 'kitty'],
            'dog': ['puppy', 'canine', 'doggy'],
            'baby': ['child', 'infant', 'toddler'],
            'landscape': ['mountain', 'nature', 'scenery'],
            'portrait': ['person', 'face', 'people'],
            'art': ['painting', 'drawing', 'sketch'],
        }
        return synonyms.get(word, [])