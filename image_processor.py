import requests
import os
import logging
from PIL import Image
import io
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.upload_dir = 'static/uploads'
        self.max_file_size = 100 * 1024  # 100KB
        self.ensure_upload_dir()
    
    def ensure_upload_dir(self):
        """Ensure upload directory exists"""
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)
    
    def process_image(self, image_url, author=None, alt_text=None):
        """Download, compress, and convert image to WebP"""
        try:
            # Download image
            response = requests.get(image_url, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to download image: {response.status_code}")
                return None
            
            # Open image with PIL
            img = Image.open(io.BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Generate filename
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{timestamp}_{url_hash}.webp"
            filepath = os.path.join(self.upload_dir, filename)
            
            # Compress and save as WebP
            quality = 85
            while quality > 10:
                # Save to bytes buffer first to check size
                buffer = io.BytesIO()
                img.save(buffer, format='WEBP', quality=quality, optimize=True)
                
                if buffer.tell() <= self.max_file_size:
                    # Size is acceptable, save to file
                    with open(filepath, 'wb') as f:
                        f.write(buffer.getvalue())
                    break
                
                # Reduce quality and try again
                quality -= 10
            
            if not os.path.exists(filepath):
                logger.error("Failed to compress image within size limit")
                return None
            
            file_size = os.path.getsize(filepath)
            relative_path = f"/static/uploads/{filename}"
            
            logger.info(f"Processed image: {relative_path} ({file_size} bytes)")
            
            return {
                'url': relative_path,
                'file_size': file_size,
                'author': author,
                'alt_text': alt_text
            }
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def resize_image(self, img, max_width=1200):
        """Resize image while maintaining aspect ratio"""
        width, height = img.size
        
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        return img
