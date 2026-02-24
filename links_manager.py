"""
Links management module for storing and managing Instagram profile links.
"""
import json
import os
import re
from typing import List, Dict, Optional


class LinksManager:
    """Manages saved Instagram profile links and nicknames."""
    
    def __init__(self, storage_file: str = 'saved_links.json'):
        self.storage_file = storage_file
        self.links = self.load_links()
    
    def extract_username_from_link(self, link: str) -> Optional[str]:
        """
        Extract Instagram username from a URL.
        
        Args:
            link: Instagram profile URL or username
            
        Returns:
            Username without @ or None if invalid
        """
        # Remove @ if present
        link = link.strip().replace('@', '')
        
        # Extract from URL patterns
        patterns = [
            r'instagram\.com/([^/?]+)',
            r'instagram\.com/([^/?]+)/',
            r'^([a-zA-Z0-9._]+)$'  # Just username
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                username = match.group(1)
                # Remove trailing slash or query params
                username = username.split('/')[0].split('?')[0]
                if username and username.replace('.', '').replace('_', '').isalnum():
                    return username
        
        return None
    
    def load_links(self) -> List[Dict]:
        """Load saved links from storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_links(self):
        """Save links to storage file."""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.links, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving links: {e}")
    
    def add_link(self, link: str, nickname: str):
        """
        Add a new link with nickname.
        
        Args:
            link: Instagram profile URL or username
            nickname: Display name for the profile
            
        Returns:
            (success, message)
        """
        username = self.extract_username_from_link(link)
        if not username:
            return False, "Invalid Instagram link or username"
        
        # Check if already exists
        for saved_link in self.links:
            if saved_link.get('username') == username:
                return False, f"Profile @{username} is already saved"
        
        self.links.append({
            'username': username,
            'link': link,
            'nickname': nickname.strip() or username
        })
        self.save_links()
        return True, f"Added @{username} as '{nickname}'"
    
    def update_link(self, username: str, nickname: str) -> bool:
        """
        Update nickname for a saved link.
        
        Args:
            username: Instagram username
            nickname: New display name
            
        Returns:
            True if updated successfully
        """
        for link in self.links:
            if link.get('username') == username:
                link['nickname'] = nickname.strip() or username
                self.save_links()
                return True
        return False
    
    def delete_link(self, username: str) -> bool:
        """
        Delete a saved link.
        
        Args:
            username: Instagram username to delete
            
        Returns:
            True if deleted successfully
        """
        original_count = len(self.links)
        self.links = [link for link in self.links if link.get('username') != username]
        if len(self.links) < original_count:
            self.save_links()
            return True
        return False
    
    def get_all_usernames(self) -> List[str]:
        """Get list of all saved usernames."""
        return [link.get('username') for link in self.links if link.get('username')]
    
    def get_nickname(self, username: str) -> str:
        """
        Get nickname for a username.
        
        Args:
            username: Instagram username
            
        Returns:
            Nickname or username if not found
        """
        for link in self.links:
            if link.get('username') == username:
                return link.get('nickname', username)
        return username
    
    def get_all_links(self) -> List[Dict]:
        """Get all saved links."""
        return self.links.copy()
