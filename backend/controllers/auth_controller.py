from flask import request, jsonify
from flask_jwt_extended import create_access_token
from services.auth_service import AuthService
from utils.decorators import validate_json

class AuthController:
    @staticmethod
    @validate_json
    def register():
        try:
            data = request.get_json()
            username = data.get('username', '').strip()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()

            if not all([username, email, password]):
                return jsonify({'error': 'All fields are required'}), 400

            user = AuthService.create_user(username, email, password)
            
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"csrf": False}
            )

            return jsonify({
                'message': 'User created successfully',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 201

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"Registration error: {e}")
            return jsonify({'error': 'Registration failed'}), 500

    @staticmethod
    @validate_json
    def login():
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '').strip()

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            user = AuthService.authenticate_user(email, password)
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401

            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"csrf": False}
            )
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            })

        except Exception as e:
            print(f"Login error: {e}")
            return jsonify({'error': 'Login failed'}), 500

    @staticmethod
    def get_profile(user_id):
        try:
            user = AuthService.get_user_by_id(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404

            return jsonify({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            })
        except Exception as e:
            print(f"Profile error: {e}")
            return jsonify({'error': 'Failed to get profile'}), 500