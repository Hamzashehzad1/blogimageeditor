import requests
import logging
import os

logger = logging.getLogger(__name__)

class PexelsClient:
    def __init__(self):
        self.api_key = os.environ.get("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {
            'Authorization': self.api_key
        }
    
    def search_images(self, query, per_page=20, page=1, orientation='landscape'):
        """Search for images on Pexels"""
        try:
            params = {
                'query': query,
                'per_page': per_page,
                'page': page,
                'orientation': orientation,
                'size': 'medium'
            }
            
            response = requests.get(f"{self.base_url}/search", 
                                  headers=self.headers,
                                  params=params,
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                images = []
                
                for photo in data.get('photos', []):
                    images.append({
                        'id': photo['id'],
                        'url': photo['src']['large'],
                        'medium_url': photo['src']['medium'],
                        'small_url': photo['src']['small'],
                        'photographer': photo['photographer'],
                        'photographer_url': photo['photographer_url'],
                        'alt': photo.get('alt', ''),
                        'width': photo['width'],
                        'height': photo['height']
                    })
                
                logger.info(f"Found {len(images)} images for query: {query}")
                return images
            else:
                logger.error(f"Pexels API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching Pexels: {e}")
            return []
    
    def get_photo(self, photo_id):
        """Get specific photo details"""
        try:
            response = requests.get(f"{self.base_url}/photos/{photo_id}", 
                                  headers=self.headers,
                                  timeout=10)
            
            if response.status_code == 200:
                photo = response.json()
                return {
                    'id': photo['id'],
                    'url': photo['src']['large'],
                    'photographer': photo['photographer'],
                    'photographer_url': photo['photographer_url'],
                    'alt': photo.get('alt', ''),
                    'width': photo['width'],
                    'height': photo['height']
                }
            else:
                logger.error(f"Failed to get photo: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting photo: {e}")
            return None
