from functools import wraps
from flask import request, jsonify
from services.auth_service import auth_service
import time
from utils.config import Config
from datetime import datetime, timezone

def require_auth(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
            
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != 'bearer':
                return jsonify({"error": "Invalid authorization scheme"}), 401
                
            payload = auth_service.verify_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Check token expiration
            exp = payload.get('exp', 0)
            if exp < time.time():
                return jsonify({"error": "Token has expired"}), 401
                
            # Check if session is too old
            created_at = payload.get('created_at', 0)
            session_age = datetime.now(timezone.utc) - datetime.fromtimestamp(created_at, timezone.utc)
            if session_age > Config.SESSION_TIMEOUT:
                return jsonify({"error": "Session has expired"}), 401
                
            request.user = payload
            return await f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({"error": f"Authentication failed: {str(e)}"}), 401
            
    return decorated

def require_email_verified(f):
    @wraps(f)
    @require_auth
    async def decorated(*args, **kwargs):
        if not request.user.get('email_verified') and Config.REQUIRE_EMAIL_VERIFICATION:
            return jsonify({"error": "Email verification required"}), 403
        return await f(*args, **kwargs)
    return decorated