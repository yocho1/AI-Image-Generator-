import os
from dotenv import load_dotenv
from services.stability_service_clean import StabilityAIService

load_dotenv()

def test_stability():
    """Test Stability.ai integration with multiple engines"""
    api_key = os.getenv('STABILITY_API_KEY')
    
    if not api_key:
        print("ERROR: No Stability.ai API key found")
        return
    
    print("Testing Stability.ai service with multiple engines...")
    
    service = StabilityAIService()
    
    if not service.available:
        print("ERROR: Stability.ai service not available")
        return
    
    print("SUCCESS: Stability.ai service is available!")
    
    # Test prompts
    test_prompts = [
        ("A cute cat playing with yarn", "realistic"),
        ("Beautiful mountain landscape", "painting"),
        ("Colorful abstract art", "minimalist")
    ]
    
    for prompt, style in test_prompts:
        print(f"\n=== Testing: '{prompt}' (Style: {style}) ===")
        
        image_url = service.generate_image(prompt, style)
        
        if image_url.startswith('data:image'):
            print("REAL AI IMAGE GENERATED SUCCESSFULLY!")
            print(f"Image data URL length: {len(image_url)} characters")
        else:
            print(f"Using fallback image: {image_url}")

if __name__ == "__main__":
    test_stability()