from models.models import db, GeneratedImage, Favorite, Collection, CollectionItem
from sqlalchemy import desc
from datetime import datetime  # ADD THIS IMPORT

class ImageService:
    @staticmethod
    def create_image(user_id, original_prompt, improved_prompt, image_url, ai_enhanced=False, style='realistic'):
        image = GeneratedImage(
            user_id=user_id,
            original_prompt=original_prompt,
            improved_prompt=improved_prompt,
            image_url=image_url,
            ai_enhanced=ai_enhanced,
            style=style
        )
        db.session.add(image)
        db.session.commit()
        return image
    
    @staticmethod
    def get_user_images(user_id, page=1, per_page=10):
        return GeneratedImage.query.filter_by(user_id=user_id)\
            .order_by(desc(GeneratedImage.created_at))\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def add_favorite(user_id, image_id):
        # Check if image exists and belongs to user
        image = GeneratedImage.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            raise ValueError('Image not found')
        
        # Check if already favorited
        existing = Favorite.query.filter_by(user_id=user_id, image_id=image_id).first()
        if existing:
            raise ValueError('Image already in favorites')
        
        favorite = Favorite(user_id=user_id, image_id=image_id)
        db.session.add(favorite)
        db.session.commit()
        return favorite
    
    @staticmethod
    def remove_favorite(user_id, image_id):
        favorite = Favorite.query.filter_by(user_id=user_id, image_id=image_id).first()
        if not favorite:
            raise ValueError('Favorite not found')
        
        db.session.delete(favorite)
        db.session.commit()
        return True
    
    @staticmethod
    def get_favorites(user_id, page=1, per_page=10):
        return Favorite.query.filter_by(user_id=user_id)\
            .join(GeneratedImage)\
            .order_by(desc(Favorite.created_at))\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def create_collection(user_id, name, description='', is_public=False):
        existing = Collection.query.filter_by(user_id=user_id, name=name).first()
        if existing:
            raise ValueError('Collection with this name already exists')
        
        collection = Collection(
            user_id=user_id,
            name=name,
            description=description,
            is_public=is_public
        )
        db.session.add(collection)
        db.session.commit()
        return collection
    
    @staticmethod
    def add_to_collection(collection_id, image_id, user_id):
        # Verify collection belongs to user
        collection = Collection.query.filter_by(id=collection_id, user_id=user_id).first()
        if not collection:
            raise ValueError('Collection not found')
        
        # Verify image belongs to user
        image = GeneratedImage.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            raise ValueError('Image not found')
        
        # Check if already in collection
        existing = CollectionItem.query.filter_by(collection_id=collection_id, image_id=image_id).first()
        if existing:
            raise ValueError('Image already in collection')
        
        item = CollectionItem(collection_id=collection_id, image_id=image_id)
        db.session.add(item)
        collection.updated_at = datetime.utcnow()  # FIXED THIS LINE
        db.session.commit()
        return item
    
    @staticmethod
    def get_user_stats(user_id):
        total_images = GeneratedImage.query.filter_by(user_id=user_id).count()
        total_favorites = Favorite.query.filter_by(user_id=user_id).count()
        total_collections = Collection.query.filter_by(user_id=user_id).count()
        
        return {
            'total_images': total_images,
            'total_favorites': total_favorites,
            'total_collections': total_collections
        }