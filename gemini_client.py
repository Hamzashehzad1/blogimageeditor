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
            prompt = f"""You are helping me find an image for a blog post section.
Here is the blog post section:

H2/H3 Title: {heading_text}
Paragraph: {heading_content[:500]}

Your task:
1. Understand the visual context of this H2 or H3 section.
2. Return ONLY a short and specific Pexels search query (4–7 words max) that will show images highly relevant to this title and paragraph.

Make sure your query is suitable for a visual search engine like Pexels."""
            
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
