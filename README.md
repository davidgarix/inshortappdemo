# Inshorts News API

A robust Flask-based REST API that provides programmatic access to news articles from Inshorts. This unofficial API allows developers to fetch categorized news content with features like pagination, rate limiting, and real-time updates.

## Features

- **Category-based News Retrieval**: Access news from 13+ categories including technology, sports, business, etc.
- **Pagination Support**: Control the number of news items with customizable limits
- **Real-time Updates**: WebSocket integration for live progress tracking
- **Error Handling**: Comprehensive error handling with detailed logging
- **CORS Support**: Cross-Origin Resource Sharing enabled for web applications
- **Rate Limiting**: Built-in protection against API abuse
- **Deployment Ready**: Configured for Heroku, Vercel, and Deta platforms

## API Endpoints

### 1. Get News by Category

```
https://inshorts.deta.dev/news?category={category_name}&limit={number}
```

Parameters:
- `category` (required): News category (see categories list below)
- `limit` (optional): Number of news items (default: 30, max: 100)

Example:

```bash
curl https://inshorts.deta.dev/news?category=technology&limit=10
```

### 2. Get Available Categories

```http
GET /categories
```

### 3. WebSocket Progress Tracking

```http
GET /start-task
```
Emits real-time progress updates through WebSocket connection.

## Available Categories

1. all (aggregate news)
2. national (Indian news)
3. business
4. sports
5. world
6. politics
7. technology
8. startup
9. entertainment
10. miscellaneous
11. hatke (unusual news)
12. science
13. automobile

## Response Format

```json
{
  "category": "technology",
  "data": [
    {
      "id": "unique-uuid",
      "title": "News Title",
      "imageUrl": "https://image.url",
      "url": "https://news.url",
      "content": "News content text",
      "author": "Author Name",
      "date": "Monday, 16 March, 2024",
      "time": "07:00 am",
      "readMoreUrl": "https://source.url"
    }
  ],
  "success": true
}
```

## Setup and Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/inshorts-news-api.git
cd inshorts-news-api
```

2. Set up virtual environment:

```bash
./setup_venv.sh
```

3. Install dependencies:

```bash
./dependencies.sh
```

4. Configure environment variables:
Create a `.env` file with:

```env
FLASK_ENV=development
FLASK_PORT=5001
FLASK_SECRET_KEY=your-secret-key
DEFAULT_NEWS_LIMIT=30
MAX_NEWS_LIMIT=100
```

5. Run the application:

```bash
python app.py
```

## Deployment

### Heroku
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Vercel
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/import/project?template=https://github.com/yourusername/Inshorts-News-API)

## Error Handling

The API implements comprehensive error handling:

- 404: Resource not found
- 405: Method not allowed
- 500: Internal server error

All errors return JSON responses with error details:

```json
{
  "error": "Error message",
  "status": "error"
}
```

## Logging

The application implements rotating file logging:
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`

## Rate Limiting and Security

- Built-in rate limiting to prevent abuse
- CORS protection
- Request logging and monitoring
- Secure headers implementation

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Flask and Python 3.7+
- Powered by Inshorts content
- Special thanks to all contributors

---

Made with ❤️ by dinesh sundaram
reference - https://github.com/cyberboysumanjay/Inshorts-News-API 
