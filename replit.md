# WordPress AI Editor

## Overview

This is a Flask-based web application that connects to WordPress sites via the REST API and provides AI-powered image suggestions for blog posts. The system integrates with Google's Gemini AI for generating intelligent image search queries and Pexels for sourcing high-quality stock photos. It includes automatic image processing, compression, and WebP conversion for optimal web performance.

## User Preferences

- **Communication style**: Simple, everyday language
- **API Credentials**: User provided their own API keys for Gemini and Pexels
- **WordPress Connection**: Uses application password authentication
- **Image Processing**: Compress to WebP under 100KB, horizontal orientation preferred

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: SQLite for development (configurable via DATABASE_URL environment variable)
- **Authentication**: WordPress Application Password authentication
- **API Integration**: RESTful communication with WordPress REST API

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **JavaScript**: Vanilla JavaScript for dynamic interactions
- **Styling**: Bootstrap 5 with custom CSS enhancements
- **Icons**: Font Awesome integration

## Key Components

### Core Flask Application (`app.py`)
- Configures Flask app with SQLAlchemy database integration
- Handles environment-based configuration for database URL and session secrets
- Uses ProxyFix middleware for proper header handling in production
- Implements automatic table creation on startup

### Database Models (`models.py`)
- **WordPressConnection**: Stores WordPress site credentials and connection details
- **BlogPost**: Caches WordPress post data with sync timestamps
- **ProcessedImage**: Tracks original and processed image URLs with metadata

### WordPress Integration (`wordpress_client.py`)
- Handles WordPress REST API authentication using Basic Auth with Application Passwords
- Provides methods for testing connections and fetching blog posts
- Implements proper error handling and timeout management

### AI-Powered Image Search
- **Gemini Client** (`gemini_client.py`): Generates contextual search queries based on blog content
- **Pexels Client** (`pexels_client.py`): Searches for relevant stock photos using AI-generated queries
- **Image Processor** (`image_processor.py`): Downloads, compresses, and converts images to WebP format

### Route Handlers (`routes.py`)
- WordPress connection management with credential validation
- Blog post listing and editing interfaces
- AI-powered image suggestion workflows
- Session management for maintaining WordPress connections

## Data Flow

1. **Connection Setup**: User provides WordPress credentials, system validates connection
2. **Post Retrieval**: Fetch blog posts from WordPress via REST API
3. **AI Analysis**: When editing posts, Gemini analyzes content to generate image search queries
4. **Image Search**: Pexels API returns relevant stock photos based on AI-generated queries
5. **Image Processing**: Selected images are downloaded, compressed, and converted to WebP
6. **Content Integration**: Processed images are integrated into blog post content

## External Dependencies

### Required Services
- **Google Gemini AI**: For generating intelligent image search queries
- **Pexels API**: For sourcing high-quality stock photography
- **WordPress Site**: Target WordPress installation with REST API enabled

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini AI API key
- `PEXELS_API_KEY`: Pexels API key for image search
- `DATABASE_URL`: Database connection string (defaults to SQLite)
- `SESSION_SECRET`: Flask session secret key

### Python Dependencies
- Flask and Flask-SQLAlchemy for web framework and ORM
- Requests for HTTP API communication
- PIL (Pillow) for image processing and conversion
- Google GenAI client for Gemini integration

## Deployment Strategy

### Development Setup
- Uses SQLite database for local development
- Includes debug mode and detailed logging
- Runs on host 0.0.0.0:5000 for accessibility in containerized environments

### Production Considerations
- Environment variable configuration for sensitive data
- Database connection pooling with health checks
- ProxyFix middleware for proper header handling behind reverse proxies
- WebP image format for optimal web performance
- Automatic upload directory creation and management

### Static Assets
- Bootstrap 5 with dark theme from CDN
- Font Awesome icons from CDN
- Custom CSS for enhanced user experience
- Client-side JavaScript for dynamic interactions

The application follows a modular architecture with clear separation of concerns, making it maintainable and extensible for future enhancements.