from flask_bcrypt import Bcrypt
from models.models import db, User
from datetime import datetime  # ADD THIS IMPORT

bcrypt = Bcrypt()

class AuthService:
    @staticmethod
    def create_user(username, email, password):
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already exists')
        
        if User.query.filter_by(email=email).first():
            raise ValueError('Email already exists')
        
        if len(password) < 6:
            raise ValueError('Password must be at least 6 characters')
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            user.last_login = datetime.utcnow()  # FIXED THIS LINE
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)