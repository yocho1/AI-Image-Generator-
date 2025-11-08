from functools import wraps
from flask import request, jsonify, g  # ADDED jsonify IMPORT
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

def jwt_required_custom(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            g.user_id = int(user_id)
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid or expired token'}), 401  # FIXED THIS LINE
    return decorated_function

def validate_json(f):  # FIXED THIS FUNCTION
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Request must be JSON'}), 400
        return f(*args, **kwargs)
    return decorated_function