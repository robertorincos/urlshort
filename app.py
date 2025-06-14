from flask import Flask, request, jsonify, redirect, render_template
from datetime import datetime
import random
import string
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import os
import logging
import re
from urllib.parse import urlparse

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'flask_database')

# Application configuration
APP_HOST = os.getenv('APP_HOST', 'localhost')
APP_PORT = int(os.getenv('APP_PORT', 5000))
APP_PROTOCOL = os.getenv('APP_PROTOCOL', 'http')
DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'

# Initialize MongoDB connection with error handling
try:
    client = MongoClient(MONGO_HOST, MONGO_PORT, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')  # Test connection
    db = client[MONGO_DB_NAME]
    url_database = db.url_database
    logger.info("MongoDB connection established successfully")
except ConnectionFailure as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise

def is_valid_url(url):
    """Validate URL format and ensure it's accessible"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except Exception:
        return False

def base62_encode(num):
    """Encode number to base62 string"""
    if num == 0:
        return "0"
    
    characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    base = len(characters)
    encoded = ""
    
    while num > 0:
        num, rem = divmod(num, base)  
        encoded = characters[rem] + encoded 
    
    return encoded

def generate_short_code():
    """Generate a unique short code for URL"""
    max_retries = 5
    for _ in range(max_retries):
        # Create more entropy
        now = datetime.now()
        ts = int(now.timestamp() * 1000)  # Use milliseconds for more uniqueness
        last_6 = ts % 1000000
        time62 = base62_encode(last_6)
        
        # Increase random string length
        length = 4
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        code = random_string + time62
        
        # Check if code already exists
        try:
            if not url_database.find_one({'short_code': code}):
                return code
        except PyMongoError as e:
            logger.error(f"Database error while checking code uniqueness: {e}")
            continue
    
    # Fallback to timestamp + longer random string
    ts = int(datetime.now().timestamp())
    return base62_encode(ts) + ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/shorten', methods=['POST'])
def shorten():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
            
        original_url = data['url'].strip()
        
        # Validate URL
        if not is_valid_url(original_url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Check if URL already exists
        existing_url = url_database.find_one({'original_url': original_url})
        if existing_url:
            code = existing_url['short_code']
            logger.info(f"URL already exists, returning existing short code: {code}")
        else:
            # Generate new short code
            code = generate_short_code()
            
            # Store in database
            url_doc = {
                'short_code': code, 
                'original_url': original_url,
                'created_at': datetime.utcnow(),
                'click_count': 0
            }
            url_database.insert_one(url_doc)
            logger.info(f"New URL shortened: {original_url} -> {code}")
        
        # Build short URL dynamically
        host = request.host
        protocol = 'https' if request.is_secure else 'http'
        
        # Use environment variables for production
        if not DEBUG_MODE:
            host = f"{APP_HOST}:{APP_PORT}" if APP_PORT != 80 and APP_PORT != 443 else APP_HOST
            protocol = APP_PROTOCOL
        
        short_url = f"{protocol}://{host}/{code}"
        
        return jsonify({
            'original_url': original_url,
            'short_code': code,
            'short_url': short_url
        })
        
    except PyMongoError as e:
        logger.error(f"Database error in shorten: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in shorten: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/<short_code>')
def redirect_to_url(short_code):
    try:
        # Validate short code format
        if not re.match(r'^[a-zA-Z0-9]+$', short_code) or len(short_code) > 20:
            return "Invalid short code format", 400
            
        url_doc = url_database.find_one({'short_code': short_code})
        
        if url_doc:
            # Increment click count
            url_database.update_one(
                {'short_code': short_code}, 
                {'$inc': {'click_count': 1}, '$set': {'last_accessed': datetime.utcnow()}}
            )
            logger.info(f"Redirecting {short_code} to {url_doc['original_url']}")
            return redirect(url_doc['original_url'])
        else:
            logger.warning(f"Short code not found: {short_code}")
            return render_template('404.html'), 404
            
    except PyMongoError as e:
        logger.error(f"Database error in redirect: {e}")
        return "Database error occurred", 500
    except Exception as e:
        logger.error(f"Unexpected error in redirect: {e}")
        return "Internal server error", 500

@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a short URL"""
    try:
        if not re.match(r'^[a-zA-Z0-9]+$', short_code) or len(short_code) > 20:
            return jsonify({'error': 'Invalid short code format'}), 400
            
        url_doc = url_database.find_one({'short_code': short_code})
        
        if url_doc:
            stats = {
                'short_code': short_code,
                'original_url': url_doc['original_url'],
                'created_at': url_doc.get('created_at', 'Unknown'),
                'click_count': url_doc.get('click_count', 0),
                'last_accessed': url_doc.get('last_accessed', 'Never')
            }
            return jsonify(stats)
        else:
            return jsonify({'error': 'Short code not found'}), 404
            
    except PyMongoError as e:
        logger.error(f"Database error in stats: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        logger.error(f"Unexpected error in stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        client.admin.command('ping')
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=APP_PORT, debug=DEBUG_MODE)