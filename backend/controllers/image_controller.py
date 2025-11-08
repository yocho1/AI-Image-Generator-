from flask import request, jsonify
from services.image_service import ImageService
from services.gemini_service import GeminiService
from utils.decorators import validate_json, jwt_required_custom

gemini_service = GeminiService()

class ImageController:
    @staticmethod
    @jwt_required_custom
    @validate_json
    def generate_image(user_id):
        try:
            data = request.get_json()
            prompt = data.get('prompt', '').strip()
            style = data.get('style', 'realistic')

            if not prompt:
                return jsonify({'error': 'Missing prompt'}), 400

            # Improve prompt
            improved_prompt = gemini_service.improve_prompt(prompt)
            ai_enhanced = gemini_service.available and gemini_service.can_make_request()
            
            # Add style to prompt
            if style and style != 'realistic':
                improved_prompt = f"{improved_prompt}, {style} style"

            # Generate image URL
            image_url = gemini_service.get_image_url(improved_prompt)

            # Save to database
            image = ImageService.create_image(
                user_id=user_id,
                original_prompt=prompt,
                improved_prompt=improved_prompt,
                image_url=image_url,
                ai_enhanced=ai_enhanced,
                style=style
            )

            return jsonify({
                'success': True,
                'original_prompt': prompt,
                'improved_prompt': improved_prompt,
                'image_url': image_url,
                'ai_enhanced': ai_enhanced,
                'style': style,
                'gemini_used': ai_enhanced,
                'image_id': image.id
            })

        except Exception as e:
            print(f"Generation error: {e}")
            return jsonify({'error': str(e)}), 500

    @staticmethod
    @jwt_required_custom
    def get_user_images(user_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            images = ImageService.get_user_images(user_id, page, per_page)
            
            return jsonify({
                'images': [{
                    'id': img.id,
                    'original_prompt': img.original_prompt,
                    'improved_prompt': img.improved_prompt,
                    'image_url': img.image_url,
                    'ai_enhanced': img.ai_enhanced,
                    'style': img.style,
                    'created_at': img.created_at.isoformat()
                } for img in images.items],
                'total': images.total,
                'pages': images.pages,
                'current_page': page
            })
        except Exception as e:
            print(f"Get images error: {e}")
            return jsonify({'error': 'Failed to get images'}), 500

    @staticmethod
    @jwt_required_custom
    @validate_json
    def add_favorite(user_id):
        try:
            data = request.get_json()
            image_id = data.get('image_id')
            
            if not image_id:
                return jsonify({'error': 'Image ID is required'}), 400
            
            favorite = ImageService.add_favorite(user_id, image_id)
            
            return jsonify({
                'message': 'Added to favorites',
                'favorite_id': favorite.id
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"Favorite error: {e}")
            return jsonify({'error': 'Failed to add favorite'}), 500

    @staticmethod
    @jwt_required_custom
    def remove_favorite(user_id, image_id):
        try:
            ImageService.remove_favorite(user_id, image_id)
            return jsonify({'message': 'Removed from favorites'})
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            print(f"Remove favorite error: {e}")
            return jsonify({'error': 'Failed to remove favorite'}), 500

    @staticmethod
    @jwt_required_custom
    def get_favorites(user_id):
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            
            favorites = ImageService.get_favorites(user_id, page, per_page)
            
            return jsonify({
                'favorites': [{
                    'id': fav.id,
                    'image': {
                        'id': fav.image.id,
                        'original_prompt': fav.image.original_prompt,
                        'improved_prompt': fav.image.improved_prompt,
                        'image_url': fav.image.image_url,
                        'ai_enhanced': fav.image.ai_enhanced,
                        'style': fav.image.style,
                        'created_at': fav.image.created_at.isoformat()
                    },
                    'added_at': fav.created_at.isoformat()
                } for fav in favorites.items],
                'total': favorites.total,
                'pages': favorites.pages,
                'current_page': page
            })
        except Exception as e:
            print(f"Get favorites error: {e}")
            return jsonify({'error': 'Failed to get favorites'}), 500

    @staticmethod
    @jwt_required_custom
    def get_stats(user_id):
        try:
            stats = ImageService.get_user_stats(user_id)
            return jsonify({'stats': stats})
        except Exception as e:
            print(f"Stats error: {e}")
            return jsonify({'error': 'Failed to get statistics'}), 500