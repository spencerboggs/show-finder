"""
Text parser module to detect show posts and extract information.
"""
import re
from datetime import datetime
from dateutil import parser as date_parser
from typing import Dict, Optional, Tuple
import calendar


class ShowTextParser:
    """Parses text to detect shows and extract date/location information."""
    
    # Keywords that suggest a post is about a show/event
    SHOW_KEYWORDS = [
        'show', 'concert', 'gig', 'performance', 'event', 'live',
        'tickets', 'doors', 'opening', 'headliner', 'support',
        'venue', 'playing', 'performing', 'on stage', 'tour',
        'tonight', 'this week', 'coming', 'upcoming'
    ]
    
    # Common date patterns
    DATE_PATTERNS = [
        r'\b(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,\s*\d{4})?\b',
        r'\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b',  # MM/DD/YYYY or DD/MM/YYYY
        r'\b(Mon|Monday|Tue|Tuesday|Wed|Wednesday|Thu|Thursday|Fri|Friday|Sat|Saturday|Sun|Sunday)\s+(?:the\s+)?\d{1,2}(?:st|nd|rd|th)?\b',
        r'\b(?:on|at|this|next)\s+(Mon|Monday|Tue|Tuesday|Wed|Wednesday|Thu|Thursday|Fri|Friday|Sat|Saturday|Sun|Sunday)\b',
        r'\b(?:tonight|tomorrow|today)\b',
        r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(Jan|January|Feb|February|Mar|March|Apr|April|May|Jun|June|Jul|July|Aug|August|Sep|September|Oct|October|Nov|November|Dec|December)\b'
    ]
    
    # Time patterns
    TIME_PATTERNS = [
        r'\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b',
        r'\b\d{1,2}:\d{2}\b',
        r'\b(?:doors|show|starts?)\s+(?:at|@)?\s*\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b'
    ]
    
    def __init__(self):
        self.current_year = datetime.now().year
    
    def is_show_post(self, text: str) -> bool:
        """
        Determine if a post is likely about a show/event.
        
        Args:
            text: Post caption text
            
        Returns:
            True if post appears to be about a show
        """
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for show keywords
        keyword_count = sum(1 for keyword in self.SHOW_KEYWORDS if keyword in text_lower)
        
        # If multiple keywords found, likely a show post
        if keyword_count >= 2:
            return True
        
        # Check for date patterns combined with event-related words
        has_date = any(re.search(pattern, text, re.IGNORECASE) for pattern in self.DATE_PATTERNS)
        has_event_word = any(word in text_lower for word in ['ticket', 'door', 'venue', 'stage', 'live'])
        
        return has_date and has_event_word
    
    def extract_date(self, text: str, post_timestamp: datetime) -> Optional[datetime]:
        """
        Extract date from text.
        
        Args:
            text: Post caption text
            post_timestamp: When the post was made (for context)
            
        Returns:
            Parsed datetime or None
        """
        if not text:
            return None
        
        # Try to find date patterns
        for pattern in self.DATE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                try:
                    # Try parsing with dateutil
                    parsed_date = date_parser.parse(date_str, default=post_timestamp)
                    
                    # Only accept future dates or dates within reasonable range
                    if parsed_date >= post_timestamp.replace(hour=0, minute=0, second=0, microsecond=0):
                        return parsed_date
                    # Also accept dates in the past if they're close (within 7 days)
                    elif (post_timestamp - parsed_date).days <= 7:
                        return parsed_date
                except:
                    continue
        
        # Check for relative dates
        text_lower = text.lower()
        if 'tonight' in text_lower or 'today' in text_lower:
            return post_timestamp.replace(hour=20, minute=0, second=0, microsecond=0)
        elif 'tomorrow' in text_lower:
            from datetime import timedelta
            return (post_timestamp + timedelta(days=1)).replace(hour=20, minute=0, second=0, microsecond=0)
        
        return None
    
    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location/venue from text.
        
        Args:
            text: Post caption text
            
        Returns:
            Location string or None
        """
        if not text:
            return None
        
        # Common location indicators
        location_patterns = [
            r'(?:at|@)\s+([A-Z][a-zA-Z\s&]+(?:Theatre|Theater|Hall|Venue|Club|Bar|Lounge|Cafe|Café|Pub|Arena|Stadium))',
            r'(?:at|@)\s+([A-Z][a-zA-Z\s&]{3,30})',
            r'@([a-zA-Z0-9_]+)',  # Instagram location tags
        ]
        
        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                location = match.group(1).strip()
                if len(location) > 2 and len(location) < 100:
                    return location
        
        return None
    
    def extract_time(self, text: str) -> Optional[str]:
        """
        Extract time from text.
        
        Args:
            text: Post caption text
            
        Returns:
            Time string or None
        """
        if not text:
            return None
        
        for pattern in self.TIME_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                return match.group(0).strip()
        
        return None
    
    def parse_show_info(self, caption: str, post_timestamp: datetime) -> Dict[str, Optional[str]]:
        """
        Parse all show information from text.
        
        Args:
            caption: Post caption
            post_timestamp: When the post was made
            
        Returns:
            Dictionary with date, location, time, and other info
        """
        info = {
            'date': None,
            'location': None,
            'time': None,
            'is_show': False
        }
        
        if not caption:
            return info
        
        info['is_show'] = self.is_show_post(caption)
        
        if info['is_show']:
            parsed_date = self.extract_date(caption, post_timestamp)
            if parsed_date:
                info['date'] = parsed_date.strftime('%Y-%m-%d')
            
            info['location'] = self.extract_location(caption)
            info['time'] = self.extract_time(caption)
        
        return info
