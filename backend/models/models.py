from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    images = db.relationship('GeneratedImage', backref='user', lazy=True, cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='user', lazy=True, cascade='all, delete-orphan')
    collections = db.relationship('Collection', backref='user', lazy=True, cascade='all, delete-orphan')

class GeneratedImage(db.Model):
    __tablename__ = 'generated_images'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_prompt = db.Column(db.Text, nullable=False)
    improved_prompt = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    ai_enhanced = db.Column(db.Boolean, default=False)
    style = db.Column(db.String(100), default='realistic')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    favorites = db.relationship('Favorite', backref='image', lazy=True, cascade='all, delete-orphan')

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('generated_images.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'image_id', name='unique_user_favorite'),)

class Collection(db.Model):
    __tablename__ = 'collections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CollectionItem(db.Model):
    __tablename__ = 'collection_items'
    
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.Integer, db.ForeignKey('collections.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('generated_images.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('collection_id', 'image_id', name='unique_collection_image'),)