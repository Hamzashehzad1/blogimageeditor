import logging
import json
import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models import WordPressConnection, BlogPost, ProcessedImage
from wordpress_client import WordPressClient
from gemini_client import GeminiClient
from pexels_client import PexelsClient
from image_processor import ImageProcessor
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
main = Blueprint("main", __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/connect', methods=['POST'])
def connect_wordpress():
    try:
        site_url = request.form.get('site_url', '').strip()
        username = request.form.get('username', '').strip()
        app_password = request.form.get('app_password', '').strip()

        if not all([site_url, username, app_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('main.index'))

        parsed_url = urlparse(site_url)
        if not parsed_url.scheme or not parsed_url.netloc:
            flash('Please enter a valid URL', 'error')
            return redirect(url_for('main.index'))

        wp_client = WordPressClient(site_url, username, app_password)
        if not wp_client.test_connection():
            flash('Failed to connect to WordPress. Please check your credentials.', 'error')
            return redirect(url_for('main.index'))

        wp_conn = WordPressConnection(
            site_url=site_url,
            username=username,
            app_password=app_password
        )
        from app import db
        db.session.add(wp_conn)
        db.session.commit()

        session['wp_connection_id'] = wp_conn.id
        flash('Successfully connected to WordPress!', 'success')
        return redirect(url_for('main.posts'))

    except Exception as e:
        logger.error(f"Error connecting to WordPress: {e}")
        flash('An error occurred while connecting to WordPress', 'error')
        return redirect(url_for('main.index'))

@main.route('/posts')
def posts():
    try:
        wp_connection_id = session.get('wp_connection_id')
        if not wp_connection_id:
            flash('Please connect to WordPress first', 'error')
            return redirect(url_for('main.index'))

        wp_conn = WordPressConnection.query.get_or_404(wp_connection_id)
        wp_client = WordPressClient(wp_conn.site_url, wp_conn.username, wp_conn.app_password)

        status_filter = request.args.get('status', 'all')
        page = int(request.args.get('page', 1))
        per_page = 10

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
        return redirect(url_for('main.index'))

# ... include all other route functions here like /edit, /api/suggest-images, etc., just replace @app.route with @main.route

def register_routes(app):
    app.register_blueprint(main)
