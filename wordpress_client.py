import requests
import logging
from base64 import b64encode
import json

logger = logging.getLogger(__name__)

class WordPressClient:
    def __init__(self, site_url, username, app_password):
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        
        # Create authentication header
        credentials = f"{username}:{app_password}"
        token = b64encode(credentials.encode()).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test WordPress connection"""
        try:
            response = requests.get(f"{self.api_base}/posts", 
                                  headers=self.headers, 
                                  params={'per_page': 1},
                                  timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def get_posts(self, status='all', page=1, per_page=10):
        """Get blog posts from WordPress"""
        try:
            params = {
                'page': page,
                'per_page': per_page,
                'orderby': 'date',
                'order': 'desc'
            }
            
            if status != 'all':
                params['status'] = status
            else:
                params['status'] = 'publish,draft'
            
            response = requests.get(f"{self.api_base}/posts", 
                                  headers=self.headers, 
                                  params=params,
                                  timeout=15)
            
            if response.status_code == 200:
                posts = response.json()
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                
                # Process posts
                processed_posts = []
                for post in posts:
                    processed_posts.append({
                        'id': post['id'],
                        'title': post['title']['rendered'],
                        'excerpt': post['excerpt']['rendered'],
                        'status': post['status'],
                        'date': post['date'],
                        'modified': post['modified'],
                        'link': post['link']
                    })
                
                return {
                    'posts': processed_posts,
                    'current_page': page,
                    'total_pages': total_pages
                }
            else:
                logger.error(f"Failed to fetch posts: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return None
    
    def get_post(self, post_id):
        """Get single blog post"""
        try:
            response = requests.get(f"{self.api_base}/posts/{post_id}", 
                                  headers=self.headers,
                                  timeout=10)
            
            if response.status_code == 200:
                post = response.json()
                return {
                    'id': post['id'],
                    'title': post['title']['rendered'],
                    'content': post['content']['rendered'],
                    'status': post['status'],
                    'date': post['date'],
                    'modified': post['modified'],
                    'featured_media': post.get('featured_media', 0)
                }
            else:
                logger.error(f"Failed to fetch post: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching post: {e}")
            return None
    
    def update_post(self, post_id, content, featured_image_id=None):
        """Update blog post"""
        try:
            data = {
                'content': content,
                'status': 'draft'
            }
            
            if featured_image_id:
                data['featured_media'] = featured_image_id
            
            response = requests.post(f"{self.api_base}/posts/{post_id}", 
                                   headers=self.headers,
                                   json=data,
                                   timeout=15)
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error updating post: {e}")
            return False
    
    def upload_media(self, file_path, filename):
        """Upload media file to WordPress"""
        try:
            with open(file_path, 'rb') as f:
                files = {
                    'file': (filename, f, 'image/webp')
                }
                
                headers = {
                    'Authorization': self.headers['Authorization']
                }
                
                response = requests.post(f"{self.api_base}/media", 
                                       headers=headers,
                                       files=files,
                                       timeout=30)
                
                if response.status_code == 201:
                    media = response.json()
                    return {
                        'id': media['id'],
                        'url': media['source_url']
                    }
                else:
                    logger.error(f"Failed to upload media: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading media: {e}")
            return None
