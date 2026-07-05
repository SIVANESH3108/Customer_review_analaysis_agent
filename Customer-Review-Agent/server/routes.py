from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from gemini_service import analyze_reviews
from database import Database
import logging

api = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
    
    username = data['username']
    password = data['password']
    
    if Database.get_user_by_username(username):
        return jsonify({"error": "Username already exists"}), 409
        
    try:
        hashed_password = generate_password_hash(password)
        user_id = Database.create_user(username, hashed_password)
        return jsonify({"message": "User registered successfully", "user_id": user_id, "username": username}), 201
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "Missing username or password"}), 400
        
    username = data['username']
    password = data['password']
    
    try:
        user = Database.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Login successful", "user_id": user['id'], "username": username}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        return jsonify({"error": str(e)}), 500

def get_current_user_id():
    """Helper to extract user_id from Authorization header."""
    auth_header = request.headers.get('Authorization')
    if auth_header:
        # Expecting format "Bearer <user_id>" or just "<user_id>"
        parts = auth_header.split()
        if len(parts) == 2 and parts[0].lower() == 'bearer':
            return parts[1]
        return auth_header
    return None

@api.route('/api/analyze', methods=['POST'])
def analyze():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.json
    if not data or 'reviews' not in data:
        return jsonify({"error": "Missing 'reviews' in request body"}), 400
    
    reviews = data['reviews']
    if not reviews.strip():
        return jsonify({"error": "Reviews cannot be empty"}), 400
        
    try:
        analysis = analyze_reviews(reviews)
        inserted_id = Database.save_analysis(reviews, analysis, user_id)
        return jsonify({
            "message": "Analysis completed successfully",
            "id": inserted_id,
            "analysis": analysis
        }), 200
    except Exception as e:
        logger.error(f"Error in /api/analyze: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/history', methods=['GET'])
def history():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        records = Database.get_history(user_id)
        return jsonify({"history": records}), 200
    except Exception as e:
        logger.error(f"Error in /api/history: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/analysis/<int:id>', methods=['DELETE'])
def delete_analysis(id):
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        success = Database.delete_analysis(id, user_id)
        if success:
            return jsonify({"message": f"Analysis {id} deleted successfully"}), 200
        else:
            return jsonify({"error": "Analysis not found or unauthorized"}), 404
    except Exception as e:
        logger.error(f"Error in DELETE /analysis/{id}: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/analysis/all', methods=['DELETE'])
def delete_all_analysis():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        Database.delete_all_analysis(user_id)
        return jsonify({"message": "All analyses deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error in DELETE /analysis/all: {e}")
        return jsonify({"error": str(e)}), 500

@api.route('/api/stats', methods=['GET'])
def stats():
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        statistics = Database.get_stats(user_id)
        return jsonify({"stats": statistics}), 200
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({"error": str(e)}), 500
