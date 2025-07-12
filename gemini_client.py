import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        api_key = os.environ.get("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
    
    def generate_image_search_query(self, blog_title, heading_text, heading_content):
        """Generate search query for Pexels based on blog context"""
        try:
            prompt = f"""
            Based on the following blog post information, generate a concise and effective search query for finding relevant stock photos on Pexels:

            Blog Title: {blog_title}
            Section Heading: {heading_text}
            Section Content (first 500 chars): {heading_content}

            Requirements:
            - Create a search query that captures the essence of this section
            - Focus on visual concepts, objects, or scenes that would complement the content
            - Keep it to 2-4 keywords maximum
            - Prefer general concepts over specific brand names or technical terms
            - Ensure the query would return horizontal/landscape images suitable for web articles

            Return only the search query, nothing else.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                # Clean up the response
                query = response.text.strip().replace('"', '').replace("'", '')
                logger.info(f"Generated search query: {query}")
                return query
            else:
                logger.error("Empty response from Gemini")
                return None
                
        except Exception as e:
            logger.error(f"Error generating search query: {e}")
            return None
    
    def generate_alt_text(self, image_url, context):
        """Generate alt text for an image based on context"""
        try:
            prompt = f"""
            Generate a descriptive alt text for a stock photo that will be used in a blog post.
            
            Context: {context}
            
            Requirements:
            - Keep it concise (under 125 characters)
            - Focus on what's visually in the image that's relevant to the context
            - Don't mention it's a stock photo
            - Be descriptive but not overly detailed
            
            Return only the alt text, nothing else.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            if response.text:
                alt_text = response.text.strip().replace('"', '').replace("'", '')
                return alt_text
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error generating alt text: {e}")
            return None
