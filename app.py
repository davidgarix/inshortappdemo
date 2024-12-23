from flask import Flask, request, jsonify
from inshorts import getNews, get_categories
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import traceback
import sys
from flask_socketio import SocketIO
import time

# Load environment variables
load_dotenv()

# Configure default limits
DEFAULT_NEWS_LIMIT = int(os.getenv('DEFAULT_NEWS_LIMIT', 30))
MAX_NEWS_LIMIT = int(os.getenv('MAX_NEWS_LIMIT', 100))

# Configure logging
def setup_logging():
    """
    Configures rotating file logging system with separate files for:
    - app.log: All application logs (10MB max, 10 backups)
    - error.log: Error-specific logs
    """
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=10485760,
        backupCount=10
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    return root_logger

logger = setup_logging()

# Custom error classes
class NewsAPIError(Exception):
    """
    Base exception for API-specific errors
    Provides consistent error response structure with status codes
    """
    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class CategoryNotFoundError(NewsAPIError):
    """Raised when category is missing or invalid"""
    def __init__(self, message="Category parameter is required or is invalid"):
        super().__init__(message, status_code=404)

# Error handler decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NewsAPIError as e:
            logger.error(f"API Error: {str(e)}")
            return jsonify({
                "error": str(e),
                "status": "error"
            }), e.status_code
        except Exception as e:
            # Log the full traceback for unexpected errors
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return jsonify({
                "error": "An unexpected error occurred",
                "status": "error"
            }), 500
    return decorated_function

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
CORS(app)

# Request logging middleware
@app.before_request
def log_request_info():
    logger.info(f'Request: {request.method} {request.url}')
    logger.debug(f'Headers: {dict(request.headers)}')
    logger.debug(f'Body: {request.get_data()}')

@app.after_request
def log_response_info(response):
    logger.info(f'Response: {response.status}')
    return response

@app.route('/')
@handle_errors
def home():
    return 'News API is UP!<br><br>A part of <a href="https://t.me/sjprojects">Sj Projects</a>'

@app.route('/news')
@handle_errors
def news():
    """
    Main endpoint to fetch news articles
    GET params:
        - category: News category (required)
        - limit: Number of articles (optional, default=30, max=100)
    Returns JSON with news articles or error message
    """
    if request.method == 'GET':
        category = request.args.get("category")
        
        # Get limit from query params with default value
        try:
            limit = int(request.args.get("limit", DEFAULT_NEWS_LIMIT))
            if limit < 1:
                limit = 1
            elif limit > MAX_NEWS_LIMIT:
                limit = MAX_NEWS_LIMIT
        except ValueError:
            limit = DEFAULT_NEWS_LIMIT
            
        if not category:
            raise CategoryNotFoundError()
        
        try:
            news_data = getNews(category, limit)
            logger.info(f"Successfully fetched news for category: {category} with limit: {limit}")
            return jsonify(news_data), 200
        except Exception as e:
            logger.error(f"Error fetching news for category {category}: {str(e)}")
            raise NewsAPIError(f"Failed to fetch news for category: {category}")

@app.route('/categories')
@handle_errors
def get_available_categories():
    """
    Returns list of all available news categories
    Falls back to predefined categories if dynamic fetch fails
    """
    try:
        categories_data = get_categories()
        
        if categories_data['success']:
            logger.info("Successfully fetched dynamic categories")
        else:
            logger.warning("Using fallback categories")
            
        return jsonify({
            "status": "success",
            "data": categories_data['categories']
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise NewsAPIError("Failed to fetch categories")

# Error handlers for common HTTP errors
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {request.url}")
    return jsonify({
        "error": "Resource not found",
        "status": "error"
    }), 404

@app.errorhandler(405)
def method_not_allowed_error(error):
    logger.error(f"405 Error: {request.method} {request.url}")
    return jsonify({
        "error": "Method not allowed",
        "status": "error"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}\n{traceback.format_exc()}")
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500

socketio = SocketIO(app)

@app.route('/start-task')
def start_task():
    def background_task():
        for i in range(100):
            time.sleep(0.1)
            socketio.emit('progress', {'progress': i})
    
    socketio.start_background_task(background_task)
    return jsonify({'message': 'Task started'})

if __name__ == '__main__':
    debug = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=debug)
