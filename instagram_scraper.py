"""
Instagram scraper module to fetch posts from venue accounts.
"""
import instaloader
from typing import List, Dict, Optional
from datetime import datetime
import time
import requests
import os
import random


class InstagramScraper:
    """Handles scraping Instagram posts from venue accounts."""
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.loader = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=1  # Reduce connection attempts
        )
        
        # Try to load session if exists
        self.session_file = 'instagram_session'
        self.is_logged_in = False
        
        if username and password:
            self.login(username, password)
        else:
            self.try_load_session()
    
    def try_load_session(self):
        """Try to load existing session."""
        try:
            # Check if session file exists (instaloader uses username.session format)
            # We'll look for any .session file in current directory
            session_files = [f for f in os.listdir('.') if f.endswith('.session')]
            if session_files:
                # Try to load the first session file found
                username_from_file = session_files[0].replace('.session', '')
                self.loader.load_session_from_file(username_from_file)
                self.is_logged_in = True
                print(f"✓ Loaded existing Instagram session for {username_from_file}")
        except Exception as e:
            # Session might be expired or invalid
            self.is_logged_in = False
    
    def login(self, username: str, password: str) -> bool:
        """
        Login to Instagram.
        
        Args:
            username: Instagram username
            password: Instagram password
            
        Returns:
            True if login successful
        """
        try:
            self.loader.login(username, password)
            # Save session (instaloader saves as username.session)
            self.is_logged_in = True
            print(f"✓ Successfully logged in as {username}")
            return True
        except instaloader.exceptions.BadCredentialsException:
            print("❌ Invalid username or password")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            print("❌ Two-factor authentication is required. Please disable it temporarily or use an app password.")
            return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def logout(self):
        """Logout and remove session."""
        try:
            # Remove all .session files
            session_files = [f for f in os.listdir('.') if f.endswith('.session')]
            for session_file in session_files:
                try:
                    os.remove(session_file)
                except:
                    pass
            self.is_logged_in = False
            print("Logged out")
        except Exception as e:
            print(f"Error logging out: {e}")
    
    def get_profile_posts(self, username: str, max_posts: int = 50, days_back: int = None) -> List[Dict]:
        """
        Fetch posts from an Instagram profile.
        
        Args:
            username: Instagram username (without @)
            max_posts: Maximum number of posts to fetch
            days_back: Only fetch posts from the last N days (None = no limit)
            
        Returns:
            List of post dictionaries with caption, image URL, post URL, and timestamp
        """
        posts = []
        cutoff_date = None
        if days_back:
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_back)
        
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                profile = instaloader.Profile.from_username(self.loader.context, username)
                
                post_count = 0
                for post in profile.get_posts():
                    if len(posts) >= max_posts:
                        break
                    
                    # Filter by date if specified
                    if cutoff_date and post.date_utc < cutoff_date:
                        break
                    
                    post_data = {
                        'username': username,
                        'caption': post.caption or '',
                        'post_url': f"https://www.instagram.com/p/{post.shortcode}/",
                        'timestamp': post.date_utc,
                        'image_url': post.url if post.typename == 'GraphImage' else None,
                        'is_video': post.is_video,
                        'shortcode': post.shortcode
                    }
                    
                    # Download image for OCR if it's an image post
                    if post.typename == 'GraphImage' and not post.is_video:
                        try:
                            image_path = f"temp_{post.shortcode}.jpg"
                            # Add delay before image request
                            time.sleep(0.5 + random.uniform(0, 0.5))
                            response = requests.get(post.url, timeout=15)
                            if response.status_code == 200:
                                with open(image_path, 'wb') as f:
                                    f.write(response.content)
                                post_data['local_image_path'] = image_path
                            elif response.status_code == 429:
                                print(f"Rate limited on image download. Waiting {retry_delay * 2} seconds...")
                                time.sleep(retry_delay * 2)
                                post_data['local_image_path'] = None
                            else:
                                post_data['local_image_path'] = None
                        except requests.exceptions.RequestException as e:
                            if '429' in str(e) or 'rate limit' in str(e).lower():
                                print(f"Rate limited. Waiting {retry_delay * 2} seconds...")
                                time.sleep(retry_delay * 2)
                            print(f"Error downloading image for post {post.shortcode}: {e}")
                            post_data['local_image_path'] = None
                    else:
                        post_data['local_image_path'] = None
                    
                    posts.append(post_data)
                    post_count += 1
                    
                    # Rate limiting - longer delays if not logged in
                    if self.is_logged_in:
                        delay = 1.5 + random.uniform(0, 0.5)  # 1.5-2 seconds when logged in
                    else:
                        delay = 5 + random.uniform(0, 2)  # 5-7 seconds when not logged in
                    time.sleep(delay)
                
                # Success - break out of retry loop
                break
                
            except instaloader.exceptions.ProfileNotExistsException:
                print(f"Profile @{username} does not exist.")
                break
            except instaloader.exceptions.LoginRequiredException:
                print(f"Login required for @{username}. You may need to log in.")
                break
            except instaloader.exceptions.ConnectionException as e:
                error_str = str(e).lower()
                is_rate_limit = '429' in str(e) or 'rate limit' in error_str or 'too many requests' in error_str
                if is_rate_limit or attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1) * 2  # Exponential backoff
                    if is_rate_limit:
                        print(f"⚠️ Rate limited by Instagram. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    else:
                        print(f"⚠️ Connection error. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"❌ Error fetching posts from @{username}: {e}")
                    break
            except Exception as e:
                # Catch any other exceptions (including rate limits not caught by ConnectionException)
                error_str = str(e).lower()
                is_rate_limit = '429' in str(e) or 'rate limit' in error_str or 'too many' in error_str
                
                if is_rate_limit:
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (attempt + 1) * 2
                        print(f"⚠️ Rate limited. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ Rate limit exceeded for @{username}. Please try again in 10-15 minutes.")
                        break
                else:
                    print(f"❌ Error fetching posts from @{username}: {e}")
                    break
        
        return posts
    
    def get_multiple_profiles_posts(self, usernames: List[str], max_posts_per_profile: int = 50, days_back: int = None) -> List[Dict]:
        """
        Fetch posts from multiple Instagram profiles.
        
        Args:
            usernames: List of Instagram usernames
            max_posts_per_profile: Maximum posts per profile
            days_back: Only fetch posts from the last N days (None = no limit)
            
        Returns:
            Combined list of all posts from all profiles
        """
        all_posts = []
        for i, username in enumerate(usernames):
            print(f"Fetching posts from @{username}... ({i+1}/{len(usernames)})")
            posts = self.get_profile_posts(username, max_posts_per_profile, days_back)
            all_posts.extend(posts)
            
            # Delay between profiles - longer if not logged in
            if i < len(usernames) - 1:  # Don't wait after last profile
                if self.is_logged_in:
                    delay = 3 + random.uniform(0, 1)  # 3-4 seconds when logged in
                else:
                    delay = 10 + random.uniform(0, 3)  # 10-13 seconds when not logged in
                print(f"Waiting {delay:.1f} seconds before next profile...")
                time.sleep(delay)
        
        # Sort by timestamp (newest first)
        all_posts.sort(key=lambda x: x['timestamp'], reverse=True)
        return all_posts
