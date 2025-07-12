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
            You are an expert at creating search queries for stock photo websites. Analyze the blog context and create the most relevant search query.

            BLOG CONTEXT:
            - Blog Title: "{blog_title}"
            - Section Heading: "{heading_text}"
            - Section Content: "{heading_content[:300]}..."

            ANALYSIS STEPS:
            1. First understand the main theme of the blog title
            2. Then analyze what this specific heading is about within that theme
            3. Consider what visual elements would best represent this section
            4. Think about what emotions or concepts should be conveyed

            SEARCH QUERY REQUIREMENTS:
            - Create 2-4 highly relevant keywords
            - Focus on visual concepts that photographers would capture
            - Avoid brand names, technical jargon, or abstract concepts
            - Ensure the query returns professional, horizontal stock photos
            - Make it specific enough to be relevant but broad enough to get results

            Return ONLY the search query, no explanation or quotes.
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
