import datetime
import uuid
import requests
import pytz
import logging
import time
import os
import sys
from flask_socketio import SocketIO
from flask import Flask, request, jsonify

logger = logging.getLogger(__name__)

# Core service for fetching and processing news from Inshorts
# Handles API interactions, data transformation, and caching
CATEGORIES = [
    'all',
    'india',
    'national',
    'world',
    'business',
    'politics',
    'sports',
    'technology',
    'startups',
    'entertainment',
    'hatke',
    'international',
    'automobile',
    'science',
    'travel',
    'miscellaneous',
    'fashion',
    'education',
    'health & fitness'
]

headers = {
    'authority': 'inshorts.com',
    'accept': '*/*',
    'accept-language': 'en-GB,en;q=0.5',
    'content-type': 'application/json',
    'referer': 'https://inshorts.com/en/read',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Brave";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'user-agent': 'Mozilla/5.0'
}

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    return wrapper

def getNews(category, limit=30):
    """
    Fetches and processes news articles from Inshorts
    
    Args:
        category: News category to fetch
        limit: Maximum number of articles to return
    
    Returns:
        Dictionary containing:
        - success: Boolean indicating success/failure
        - category: Requested category
        - data: List of processed news articles
    """
    category = category.lower()
    if category != 'all' and category not in CATEGORIES:
        return {
            'success': False,
            'error': f'Invalid category. Must be one of: {", ".join(CATEGORIES)} or "all"'
        }
        
    newsDictionary = {
        'success': True,
        'category': category,
        'data': []
    }

    try:
        if category == 'all':
            # Original all news endpoint
            response = requests.get(
                'https://inshorts.com/api/en/news',
                params={
                    'category': 'all_news',
                    'max_limit': str(limit),
                    'include_card_data': 'true'
                }
            )
            
            news_data = response.json().get('data', {}).get('news_list', [])
            if not news_data:
                newsDictionary['success'] = False
                newsDictionary['error'] = 'No news found'
                return newsDictionary

            for entry in news_data[:limit]:
                try:
                    news = entry['news_obj']
                    newsObject = create_news_object(news)
                    newsDictionary['data'].append(newsObject)
                except Exception as e:
                    logger.error(f"Error processing news entry: {str(e)}")
                    continue
        else:
            # Category-specific news with pagination
            collected_news = []
            offset = 0
            batch_size = 10

            while len(collected_news) < limit:
                # Get trending topics first
                trending_response = requests.get(
                    'https://inshorts.com/api/en/trending_topics',
                    headers=headers
                )
                
                if trending_response.status_code != 200:
                    break

                response = requests.get(
                    f'https://inshorts.com/api/en/search/trending_topics/{category}',
                    headers=headers,
                    params={
                        'category': 'top_stories',
                        'max_limit': str(batch_size),
                        'include_card_data': 'true',
                        'news_offset': str(offset),
                        'size': str(batch_size)
                    }
                )

                if response.status_code != 200:
                    break

                news_data = response.json().get('data', {}).get('news_list', [])
                if not news_data:
                    break

                collected_news.extend(news_data)
                if len(collected_news) >= limit:
                    break

                offset += batch_size
                time.sleep(0.1)  # Small delay to prevent rate limiting

            # Process collected news
            for entry in collected_news[:limit]:
                try:
                    news = entry['news_obj']
                    newsObject = create_news_object(news)
                    newsDictionary['data'].append(newsObject)
                except Exception as e:
                    logger.error(f"Error processing news entry: {str(e)}")
                    continue

        return newsDictionary

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        newsDictionary['success'] = False
        newsDictionary['error'] = str(e)
        return newsDictionary

def create_news_object(news):
    """
    Transforms raw API response into standardized news format
    
    Handles:
    - Timezone conversion (UTC to IST)
    - Unique ID generation
    - Data structure normalization
    """
    timestamp = news['created_at'] / 1000
    dt_utc = datetime.datetime.utcfromtimestamp(timestamp)
    tz_utc = pytz.timezone('UTC')
    dt_utc = tz_utc.localize(dt_utc)
    tz_ist = pytz.timezone('Asia/Kolkata')
    dt_ist = dt_utc.astimezone(tz_ist)
    
    return {
        'id': uuid.uuid4().hex,
        'title': news['title'],
        'imageUrl': news['image_url'],
        'url': news['shortened_url'],
        'content': news['content'],
        'author': news['author_name'],
        'date': dt_ist.strftime('%A, %d %B, %Y'),
        'time': dt_ist.strftime('%I:%M %p').lower(),
        'readMoreUrl': news['source_url']
    }

def get_categories():
    """Get all available news categories"""
    try:
        return {
            'success': True,
            'categories': CATEGORIES
        }
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        return {
            'success': False,
            'categories': []
        }

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
@handle_errors
def home():
    return 'News API is UP!<br><br>A part of <a href="https://t.me/sjprojects">Sj Projects</a>'

@app.route('/start-task')
def start_task():
    """
    WebSocket endpoint for long-running tasks
    Emits progress events (0-100) to connected clients
    Handles task completion and error notifications
    """
    def background_task():
        try:
            for i in range(100):
                time.sleep(0.1)
                socketio.emit('progress', {'progress': i})
            socketio.emit('complete', {'status': 'success'})
        except Exception as e:
            logger.error(f"Background task error: {str(e)}")
            socketio.emit('error', {'message': 'Task failed'})
    
    socketio.start_background_task(background_task)
    return jsonify({'message': 'Task started', 'status': 'success'})

if __name__ == '__main__':
    try:
        debug = os.getenv('FLASK_ENV') == 'development'
        port = int(os.getenv('FLASK_PORT', 5001))
        
        if debug:
            logger.info(f"Starting server in DEBUG mode on port {port}")
        else:
            logger.info(f"Starting server in PRODUCTION mode on port {port}")
            
        socketio.run(app, host='0.0.0.0', port=port, debug=debug)
    except Exception as e:
        logger.critical(f"Failed to start server: {str(e)}")
        sys.exit(1)