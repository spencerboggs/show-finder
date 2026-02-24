"""
Main processor that combines scraping, parsing, and OCR to extract show information.
"""
from typing import List, Dict, Optional
from datetime import datetime
from instagram_scraper import InstagramScraper
from text_parser import ShowTextParser
from ocr_extractor import OCRExtractor
import os


class ShowProcessor:
    """Processes Instagram posts to extract show information."""
    
    def __init__(self, instagram_username: Optional[str] = None, instagram_password: Optional[str] = None):
        self.scraper = InstagramScraper(instagram_username, instagram_password)
        self.text_parser = ShowTextParser()
        self.ocr_extractor = OCRExtractor()
    
    def update_credentials(self, username: Optional[str] = None, password: Optional[str] = None):
        """Update Instagram credentials and reinitialize scraper."""
        self.scraper = InstagramScraper(username, password)
    
    def process_posts(self, usernames: List[str], max_posts_per_profile: int = 50, days_back: int = None, nickname_map: Dict[str, str] = None) -> List[Dict]:
        """
        Process posts from multiple Instagram accounts to extract show information.
        
        Args:
            usernames: List of Instagram usernames to scrape
            max_posts_per_profile: Maximum posts to fetch per profile
            days_back: Only fetch posts from the last N days (None = no limit)
            nickname_map: Dictionary mapping usernames to nicknames
            
        Returns:
            List of show dictionaries with all extracted information
        """
        # Fetch posts
        posts = self.scraper.get_multiple_profiles_posts(usernames, max_posts_per_profile, days_back)
        
        shows = []
        
        for post in posts:
            # First, try to extract info from caption
            caption_info = self.text_parser.parse_show_info(
                post['caption'],
                post['timestamp']
            )
            
            # Only process if it's identified as a show post
            if not caption_info['is_show']:
                continue
            
            # Get nickname if available
            display_name = post['username']
            if nickname_map and post['username'] in nickname_map:
                display_name = nickname_map[post['username']]
            
            show_info = {
                'post_url': post['post_url'],
                'username': post['username'],
                'display_name': display_name,
                'caption': post['caption'],
                'date': caption_info['date'],
                'location': caption_info['location'] or 'Unknown',
                'time': caption_info['time'] or 'Unknown',
            }
            
            # If we're missing date or location, try OCR on the image
            if (not show_info['date'] or show_info['location'] == 'Unknown') and post['local_image_path']:
                ocr_info = self.ocr_extractor.extract_show_info_from_image(
                    post['local_image_path'],
                    post['timestamp']
                )
                
                # Fill in missing information from OCR
                if not show_info['date'] and ocr_info['date']:
                    show_info['date'] = ocr_info['date']
                
                if show_info['location'] == 'Unknown' and ocr_info['location']:
                    show_info['location'] = ocr_info['location']
                
                if show_info['time'] == 'Unknown' and ocr_info['time']:
                    show_info['time'] = ocr_info['time']
            
            # Set defaults for missing info
            if not show_info['date']:
                show_info['date'] = 'Unknown'
            
            # Only add shows with at least a date or location
            if show_info['date'] != 'Unknown' or show_info['location'] != 'Unknown':
                shows.append(show_info)
            
            # Clean up temporary image file
            if post['local_image_path'] and os.path.exists(post['local_image_path']):
                try:
                    os.remove(post['local_image_path'])
                except:
                    pass
        
        return shows
