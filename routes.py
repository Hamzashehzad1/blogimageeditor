import logging
import json
from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import WordPressConnection, BlogPost, ProcessedImage
from wordpress_client import WordPressClient
from gemini_client import GeminiClient
from pexels_client import PexelsClient
from image_processor import ImageProcessor
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Home page with WordPress connection form"""
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect_wordpress():
    """Connect to WordPress site"""
    try:
        site_url = request.form.get('site_url', '').strip()
        username = request.form.get('username', '').strip()
        app_password = request.form.get('app_password', '').strip()
        
        if not all([site_url, username, app_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('index'))
        
        # Validate URL
        parsed_url = urlparse(site_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            flash('Please enter a valid URL', 'error')
            return redirect(url_for('index'))
        
        # Test connection
        wp_client = WordPressClient(site_url, username, app_password)
        if not wp_client.test_connection():
            flash('Failed to connect to WordPress. Please check your credentials.', 'error')
            return redirect(url_for('index'))
        
        # Save connection
        wp_conn = WordPressConnection(
            site_url=site_url,
            username=username,
            app_password=app_password
        )
        db.session.add(wp_conn)
        db.session.commit()
        
        session['wp_connection_id'] = wp_conn.id
        flash('Successfully connected to WordPress!', 'success')
        return redirect(url_for('posts'))
        
    except Exception as e:
        logger.error(f"Error connecting to WordPress: {e}")
        flash('An error occurred while connecting to WordPress', 'error')
        return redirect(url_for('index'))

@app.route('/posts')
def posts():
    """Display blog posts with pagination"""
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            flash('Please connect to WordPress first', 'error')
            return redirect(url_for('index'))
        
        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        per_page = 10
        
        # Fetch posts from WordPress
        posts_data = wp_client.get_posts(status=status_filter, page=page, per_page=per_page)
        
        if posts_data is None:
            flash('Failed to fetch posts from WordPress', 'error')
            posts_data = {'posts': [], 'total_pages': 0, 'current_page': 1}
        
        return render_template('posts.html', 
                             posts=posts_data['posts'],
                             current_page=posts_data['current_page'],
                             total_pages=posts_data['total_pages'],
                             status_filter=status_filter,
                             wp_connection=wp_conn)
        
    except Exception as e:
        logger.error(f"Error fetching posts: {e}")
        flash('An error occurred while fetching posts', 'error')
        return redirect(url_for('index'))

@app.route('/edit/<int:post_id>')
def edit_post(post_id):
    """Edit blog post with AI image suggestions"""
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            flash('Please connect to WordPress first', 'error')
            return redirect(url_for('index'))
        
        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)
        
        # Get post from WordPress
        post = wp_client.get_post(post_id)
        if not post:
            flash('Post not found', 'error')
            return redirect(url_for('posts'))
        
        # Extract headings from content
        headings = extract_headings(post['content'])
        
        return render_template('edit_post.html', 
                             post=post, 
                             headings=headings,
                             wp_connection=wp_conn)
        
    except Exception as e:
        logger.error(f"Error loading post for editing: {e}")
        flash('An error occurred while loading the post', 'error')
        return redirect(url_for('posts'))

@app.route('/api/suggest-images/<int:post_id>/<heading_index>')
def suggest_images(post_id, heading_index):
    """Get AI-suggested images for a heading"""
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            return jsonify({'error': 'Not connected to WordPress'}), 401
        
        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)
        
        # Get post
        post = wp_client.get_post(post_id)
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Handle featured image request or specific heading
        if heading_index == 'featured':
            # Featured image - use blog title
            search_query_context = {
                'title': post['title'],
                'heading_text': post['title'],
                'heading_content': 'Featured image for blog post'
            }
        else:
            # Specific heading
            heading_index = int(heading_index)
            headings = extract_headings(post['content'])
            if heading_index >= len(headings):
                return jsonify({'error': 'Heading not found'}), 404
            
            heading = headings[heading_index]
            search_query_context = {
                'title': post['title'],
                'heading_text': heading['text'],
                'heading_content': heading['content']
            }
        
        # Generate search query using Gemini
        gemini_client = GeminiClient()
        search_query = gemini_client.generate_image_search_query(
            search_query_context['title'], 
            search_query_context['heading_text'], 
            search_query_context['heading_content']
        )
        
        if not search_query:
            return jsonify({'error': 'Failed to generate search query'}), 500
        
        # Get page parameter for pagination
        page = int(request.args.get('page', 1))
        per_page = 20
        
        # Search for images on Pexels
        pexels_client = PexelsClient()
        images = pexels_client.search_images(search_query, per_page=per_page, page=page, orientation='landscape')
        
        if not images:
            return jsonify({'error': 'No images found'}), 404
        
        return jsonify({
            'search_query': search_query,
            'images': images,
            'current_page': page,
            'has_more': len(images) == per_page  # If we got full page, there might be more
        })
        
    except Exception as e:
        logger.error(f"Error suggesting images: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/process-image', methods=['POST'])
def process_image():
    """Process and upload selected image to WordPress"""
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            return jsonify({'error': 'Not connected to WordPress'}), 401
        
        data = request.get_json()
        image_url = data.get('image_url')
        author = data.get('author')
        alt_text = data.get('alt_text')
        
        if not image_url:
            return jsonify({'error': 'Image URL is required'}), 400
        
        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)
        
        # Process image (download, compress, convert to WebP)
        image_processor = ImageProcessor()
        processed_image = image_processor.process_image(image_url, author, alt_text)
        
        if not processed_image:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Upload to WordPress media library
        media_response = wp_client.upload_media(processed_image['file_path'], processed_image['filename'])
        
        if not media_response:
            return jsonify({'error': 'Failed to upload image to WordPress'}), 500
        
        # Save to database
        processed_img = ProcessedImage(
            original_url=image_url,
            processed_url=media_response['url'],
            author=author,
            alt_text=alt_text,
            file_size=processed_image['file_size']
        )
        db.session.add(processed_img)
        db.session.commit()
        
        return jsonify({
            'processed_url': media_response['url'],
            'media_id': media_response['id'],
            'file_size': processed_image['file_size'],
            'attribution': f"Image by {author} from Pexels"
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/save-post', methods=['POST'])
def save_post():
    """Save updated blog post to WordPress"""
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            return jsonify({'error': 'Not connected to WordPress'}), 401
        
        data = request.get_json()
        post_id = data.get('post_id')
        content = data.get('content')
        featured_image_id = data.get('featured_image_id')
        
        if not all([post_id, content]):
            return jsonify({'error': 'Post ID and content are required'}), 400
        
        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)
        
        # Update post
        success = wp_client.update_post(post_id, content, featured_image_id)
        
        if success:
            return jsonify({'message': 'Post saved successfully'})
        else:
            return jsonify({'error': 'Failed to save post'}), 500
        
    except Exception as e:
        logger.error(f"Error saving post: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def extract_headings(content):
    """Extract H2 and H3 headings from HTML content"""
    headings = []
    
    # Find all H2 and H3 tags
    h2_pattern = r'<h2[^>]*>(.*?)</h2>'
    h3_pattern = r'<h3[^>]*>(.*?)</h3>'
    
    h2_matches = re.finditer(h2_pattern, content, re.IGNORECASE | re.DOTALL)
    h3_matches = re.finditer(h3_pattern, content, re.IGNORECASE | re.DOTALL)
    
    all_matches = []
    
    for match in h2_matches:
        all_matches.append({
            'type': 'h2',
            'text': re.sub(r'<[^>]+>', '', match.group(1)).strip(),
            'start': match.start(),
            'end': match.end()
        })
    
    for match in h3_matches:
        all_matches.append({
            'type': 'h3',
            'text': re.sub(r'<[^>]+>', '', match.group(1)).strip(),
            'start': match.start(),
            'end': match.end()
        })
    
    # Sort by position in content
    all_matches.sort(key=lambda x: x['start'])
    
    # Extract content after each heading
    for i, heading in enumerate(all_matches):
        next_heading_start = all_matches[i + 1]['start'] if i + 1 < len(all_matches) else len(content)
        heading_content = content[heading['end']:next_heading_start]
        
        # Clean up content (remove HTML tags for context)
        clean_content = re.sub(r'<[^>]+>', ' ', heading_content).strip()
        heading['content'] = clean_content[:500]  # Limit content length
        
        headings.append(heading)
    
    return headings

@app.route('/disconnect')
def disconnect():
    """Disconnect from WordPress"""
    session.pop('wp_connection_id', None)
    flash('Disconnected from WordPress', 'info')
    return redirect(url_for('index'))
