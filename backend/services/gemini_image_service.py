import os
import time
import base64
import google.generativeai as genai
from config import Config

class GeminiImageService:
    def __init__(self):
        self.available = False
        self.image_model_name = None
        self.text_model_name = "models/gemini-2.5-flash-latest"  # For prompt enhancement
        self.last_request_time = 0
        self.request_cooldown = 10  # Rate limiting
        
        if Config.GEMINI_API_KEY:
            self._initialize()
    
    def _initialize(self):
        """Initialize Gemini with image generation capabilities"""
        try:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            # Use the dedicated image generation models
            self.image_model_name = "models/gemini-2.5-flash-image-preview"
            self.available = True
            
            print(f"✅ Gemini Image Service initialized with: {self.image_model_name}")
            
        except Exception as e:
            print(f"❌ Gemini Image Service init failed: {e}")
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
        Generate REAL AI images using Gemini 2.5 Flash Image
        """
        if not self.available or not self.can_make_request():
            print("Gemini image service not available - using fallback")
            return self._get_fallback_image_url(prompt)
        
        try:
            # Step 1: Enhance the prompt with Gemini
            enhanced_prompt = self._enhance_prompt_with_style(prompt, style)
            print(f"🎨 Generating image with prompt: {enhanced_prompt}")
            
            # Step 2: Generate the actual image
            image_response = self._generate_image_with_gemini(enhanced_prompt)
            
            if image_response:
                return image_response
            else:
                return self._get_fallback_image_url(prompt)
                
        except Exception as e:
            print(f"❌ Image generation error: {e}")
            return self._get_fallback_image_url(prompt)
    
    def _enhance_prompt_with_style(self, prompt, style):
        """Use Gemini to enhance the prompt based on style"""
        try:
            model = genai.GenerativeModel(self.text_model_name)
            
            style_instructions = {
                'realistic': 'photorealistic, highly detailed, professional photography, 8K resolution',
                'anime': 'anime style, Japanese animation, vibrant colors, manga art style',
                'painting': 'oil painting, artistic, brush strokes, masterpiece, gallery quality',
                'cartoon': 'cartoon style, animated, bright colors, family friendly',
                'minimalist': 'minimalist, simple, clean lines, modern art, geometric'
            }
            
            style_desc = style_instructions.get(style, 'high quality, detailed')
            
            enhancement_prompt = f"""
            Improve this image description for AI image generation: "{prompt}"
            
            Style requirements: {style_desc}
            
            Make the description:
            - More visual and descriptive
            - Include specific details about lighting, colors, composition
            - 10-20 words maximum
            - Focus only on visual elements
            
            Return only the improved prompt, nothing else.
            """
            
            response = model.generate_content(
                enhancement_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=100,
                )
            )
            
            if response.text:
                enhanced = response.text.strip()
                print(f"📝 Enhanced prompt: {enhanced}")
                return enhanced
            else:
                return f"{prompt}, {style_desc}"
                
        except Exception as e:
            print(f"Prompt enhancement failed: {e}")
            return f"{prompt}, {style_desc}"
    
    def _generate_image_with_gemini(self, prompt):
        """
        Generate actual image using Gemini 2.5 Flash Image model
        """
        try:
            # Use the dedicated image generation model
            model = genai.GenerativeModel(self.image_model_name)
            
            print(f"🚀 Calling Gemini Image API with: {prompt}")
            
            # Generate the image
            response = model.generate_content(prompt)
            
            # Handle the image response
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content.parts:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data'):
                            # This is the generated image data
                            image_data = part.inline_data.data
                            image_mime_type = part.inline_data.mime_type
                            
                            # Convert to base64 data URL
                            image_base64 = base64.b64encode(image_data).decode('utf-8')
                            image_url = f"data:{image_mime_type};base64,{image_base64}"
                            
                            print("✅ Real AI image generated successfully!")
                            return image_url
            
            # If we get here, try alternative response format
            return self._handle_alternative_response(response, prompt)
            
        except Exception as e:
            print(f"❌ Gemini image generation failed: {e}")
            return None
    
    def _handle_alternative_response(self, response, prompt):
        """Handle different response formats from Gemini"""
        try:
            # Sometimes the image is in different parts of the response
            if hasattr(response, '_result'):
                result = response._result
                if hasattr(result, 'candidates'):
                    for candidate in result.candidates:
                        if hasattr(candidate, 'content'):
                            content = candidate.content
                            if hasattr(content, 'parts'):
                                for part in content.parts:
                                    if hasattr(part, 'inline_data'):
                                        image_data = part.inline_data.data
                                        mime_type = part.inline_data.mime_type
                                        image_base64 = base64.b64encode(image_data).decode('utf-8')
                                        return f"data:{mime_type};base64,{image_base64}"
            
            print("⚠️ Could not extract image from response")
            return None
            
        except Exception as e:
            print(f"Alternative response handling failed: {e}")
            return None
    
    def _get_fallback_image_url(self, prompt):
        """Fallback to Picsum if AI generation fails"""
        import hashlib
        import random
        
        # Better fallback with categories
        prompt_lower = prompt.lower()
        image_categories = {
            'cat': [237, 219, 222, 257, 96],
            'dog': [1062, 1074, 1080, 1081, 1084],
            'baby': [1005, 1011, 1012, 1018, 1025],
            'panda': [1024, 1031, 1035, 1036, 1039],
            'landscape': [1015, 1016, 1018, 1020, 1021, 1022, 1023, 1028],
            'portrait': [1005, 1009, 1011, 1012, 1019, 1027],
            'art': [100, 101, 102, 103, 104],
        }
        
        for category, ids in image_categories.items():
            if any(word in prompt_lower for word in [category] + self._get_synonyms(category)):
                return f"https://picsum.photos/id/{random.choice(ids)}/512/512"
        
        seed = hashlib.md5(prompt.encode()).hexdigest()[:10]
        return f"https://picsum.photos/seed/{seed}/512/512"
    
    def _get_synonyms(self, word):
        synonyms = {
            'cat': ['kitten', 'feline', 'kitty'],
            'dog': ['puppy', 'canine', 'doggy'],
            'baby': ['child', 'infant', 'toddler'],
            'panda': ['bear'],
            'landscape': ['mountain', 'nature', 'scenery', 'view'],
            'portrait': ['person', 'face', 'people', 'human'],
            'art': ['painting', 'drawing', 'sketch', 'artwork'],
        }
        return synonyms.get(word, [])