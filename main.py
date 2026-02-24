"""
Main application file for Show Finder.
"""
import tkinter as tk
from tkinter import messagebox
from show_processor import ShowProcessor
from calendar_ui import CalendarUI
from links_ui import LinksManagementUI
from links_manager import LinksManager
import threading


class ShowFinderApp:
    """Main application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('1200x800')
        self.root.configure(bg='#202020')
        
        # Windows 11 font
        self.font_family = 'Segoe UI'
        
        self.processor = ShowProcessor()
        self.links_manager = LinksManager()
        self.instagram_username = None
        self.instagram_password = None
        
        # Create navigation bar
        self.nav_frame = tk.Frame(self.root, bg='#2a2a2a', height=50)
        self.nav_frame.pack(fill=tk.X, padx=0, pady=0)
        self.nav_frame.pack_propagate(False)
        self.setup_navigation()
        
        # Create main container for switching views
        self.main_container = tk.Frame(self.root, bg='#202020')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Initialize views
        self.calendar_ui = None
        self.links_ui = None
        self.current_view = 'calendar'
        
        # Start with calendar view
        self.show_calendar_view()
        
        # Add menu bar
        self.setup_menu()
        
        # Update login status after UI is set up
        self.root.after(100, self.update_login_status)
    
    def setup_navigation(self):
        """Set up navigation buttons."""
        # Left side - navigation buttons
        nav_left = tk.Frame(self.nav_frame, bg='#2a2a2a')
        nav_left.pack(side=tk.LEFT, padx=15, pady=8)
        
        self.calendar_btn = self.create_nav_button(
            nav_left,
            "📅 Calendar",
            self.show_calendar_view,
            is_active=True
        )
        self.calendar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.profiles_btn = self.create_nav_button(
            nav_left,
            "👥 Manage Profiles",
            self.show_links_view,
            is_active=False
        )
        self.profiles_btn.pack(side=tk.LEFT)
        
        # Right side - status and title
        right_frame = tk.Frame(self.nav_frame, bg='#2a2a2a')
        right_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Login status
        self.login_status_label = tk.Label(
            right_frame,
            text="",
            bg='#2a2a2a',
            fg='#a0a0a0',
            font=(self.font_family, 9)
        )
        self.login_status_label.pack(side=tk.RIGHT, padx=(0, 15))
        self.update_login_status()
        
        # App title
        title_label = tk.Label(
            right_frame,
            text="Show Finder",
            bg='#2a2a2a',
            fg='#ffffff',
            font=(self.font_family, 12, 'bold')
        )
        title_label.pack(side=tk.RIGHT)
    
    def create_nav_button(self, parent, text, command, is_active=False):
        """Create a navigation button."""
        bg_color = '#0078d4' if is_active else '#2a2a2a'
        hover_color = '#106ebe' if is_active else '#3a3a3a'
        fg_color = '#ffffff'
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=fg_color,
            activebackground=hover_color,
            activeforeground=fg_color,
            borderwidth=0,
            font=(self.font_family, 10),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8
        )
        
        def on_enter(e):
            if not is_active:
                btn.config(bg=hover_color)
        
        def on_leave(e):
            if not is_active:
                btn.config(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(
            self.root,
            bg='#2a2a2a',
            fg='#ffffff',
            activebackground='#0078d4',
            activeforeground='#ffffff',
            font=(self.font_family, 9)
        )
        self.root.config(menu=menubar)
        
        settings_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='#ffffff', activebackground='#0078d4')
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Instagram Login...", command=self.show_login_dialog)
        settings_menu.add_command(label="Logout", command=self.logout_instagram)
        
        help_menu = tk.Menu(menubar, tearoff=0, bg='#2a2a2a', fg='#ffffff', activebackground='#0078d4')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def clear_main_container(self):
        """Clear the main container."""
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_calendar_view(self):
        """Show the calendar view."""
        self.current_view = 'calendar'
        self.clear_main_container()
        self.calendar_ui = CalendarUI(self.main_container)
        self.root.title("Show Finder - Calendar")
        self.update_nav_buttons()
    
    def show_links_view(self):
        """Show the links management view."""
        self.current_view = 'profiles'
        self.clear_main_container()
        self.links_ui = LinksManagementUI(
            self.main_container,
            self.links_manager,
            on_fetch_callback=self.fetch_shows_from_usernames,
            on_refetch_all_callback=self.refetch_all_shows
        )
        self.root.title("Show Finder - Manage Profiles")
        self.update_nav_buttons()
    
    def update_nav_buttons(self):
        """Update navigation button states."""
        if not hasattr(self, 'calendar_btn') or not hasattr(self, 'profiles_btn'):
            return
        
        is_calendar = self.current_view == 'calendar'
        
        self.calendar_btn.config(
            bg='#0078d4' if is_calendar else '#2a2a2a',
            activebackground='#106ebe' if is_calendar else '#3a3a3a'
        )
        
        self.profiles_btn.config(
            bg='#0078d4' if not is_calendar else '#2a2a2a',
            activebackground='#106ebe' if not is_calendar else '#3a3a3a'
        )
    
    def update_login_status(self):
        """Update login status indicator."""
        if hasattr(self, 'login_status_label'):
            if self.processor.scraper.is_logged_in:
                self.login_status_label.config(text="✓ Logged in", fg='#4caf50')
            else:
                self.login_status_label.config(text="⚠ Not logged in", fg='#ff9800')
    
    def fetch_shows_from_usernames(self, usernames: list):
        """Fetch shows from given usernames."""
        if not usernames:
            return
        
        # Get nickname map
        nickname_map = {}
        for username in usernames:
            nickname = self.links_manager.get_nickname(username)
            nickname_map[username] = nickname
        
        self._fetch_and_display_shows(usernames, nickname_map, days_back=7, max_posts=20)
    
    def refetch_all_shows(self, usernames: list):
        """Refetch shows from all saved profiles."""
        if not usernames:
            messagebox.showwarning("No Profiles", "No saved profiles to fetch from.")
            return
        
        # Get nickname map
        nickname_map = {}
        for username in usernames:
            nickname = self.links_manager.get_nickname(username)
            nickname_map[username] = nickname
        
        self._fetch_and_display_shows(usernames, nickname_map, days_back=7, max_posts=20)
    
    def _fetch_and_display_shows(self, usernames: list, nickname_map: dict, days_back: int = 7, max_posts: int = 20):
        """Internal method to fetch and display shows."""
        # Show loading message
        loading_window = tk.Toplevel(self.root)
        loading_window.title("Loading Shows")
        loading_window.configure(bg='#202020')
        loading_window.geometry('350x120')
        loading_window.transient(self.root)
        loading_window.grab_set()
        
        # Center the loading window
        loading_window.update_idletasks()
        x = (loading_window.winfo_screenwidth() // 2) - (loading_window.winfo_width() // 2)
        y = (loading_window.winfo_screenheight() // 2) - (loading_window.winfo_height() // 2)
        loading_window.geometry(f"+{x}+{y}")
        
        status_label = tk.Label(
            loading_window,
            text=f"Fetching posts from {len(usernames)} profile(s)...\nThis may take a while.",
            bg='#202020',
            fg='#ffffff',
            font=(self.font_family, 10)
        )
        status_label.pack(expand=True, pady=20)
        
        def process_in_thread():
            try:
                # Warn if not logged in
                if not self.processor.scraper.is_logged_in:
                    print("⚠️ Warning: Not logged in. Rate limiting may occur. Consider logging in via Settings → Instagram Login...")
                
                shows = self.processor.process_posts(
                    usernames,
                    max_posts_per_profile=max_posts,
                    days_back=days_back,
                    nickname_map=nickname_map
                )
                loading_window.destroy()
                
                if shows:
                    # Switch to calendar view to show results
                    self.show_calendar_view()
                    self.calendar_ui.set_shows(shows)
                    
                    messagebox.showinfo(
                        "Success",
                        f"Loaded {len(shows)} shows from {len(usernames)} profile(s)."
                    )
                else:
                    warning_msg = "No shows were found in the posts from the provided profiles.\n\n"
                    warning_msg += "Make sure the posts are from the past week and contain show-related keywords."
                    if not self.processor.scraper.is_logged_in:
                        warning_msg += "\n\nTip: Logging in (Settings → Instagram Login) can help avoid rate limiting."
                    messagebox.showwarning("No Shows Found", warning_msg)
            except Exception as e:
                loading_window.destroy()
                error_msg = f"An error occurred while loading shows:\n{str(e)}"
                if not self.processor.scraper.is_logged_in and '429' in str(e):
                    error_msg += "\n\nTip: Logging in (Settings → Instagram Login) can help avoid rate limiting."
                messagebox.showerror("Error", error_msg)
        
        # Process in a separate thread to avoid freezing the UI
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()
        
        # Update the loading window periodically
        self.root.after(100, lambda: self.check_thread(thread, loading_window))
    
    def check_thread(self, thread, window):
        """Check if thread is still running."""
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread, window))
        else:
            if window.winfo_exists():
                window.destroy()
    
    def show_login_dialog(self):
        """Show Instagram login dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Instagram Login")
        dialog.configure(bg='#202020')
        dialog.geometry('400x250')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(
            dialog,
            text="Instagram Login",
            bg='#202020',
            fg='#ffffff',
            font=(self.font_family, 14, 'bold')
        )
        title_label.pack(pady=(20, 10))
        
        # Info text
        info_label = tk.Label(
            dialog,
            text="Login to reduce rate limiting.\nYour session will be saved securely.",
            bg='#202020',
            fg='#a0a0a0',
            font=(self.font_family, 9),
            justify=tk.CENTER
        )
        info_label.pack(pady=(0, 20))
        
        # Username
        username_frame = tk.Frame(dialog, bg='#202020')
        username_frame.pack(fill=tk.X, padx=30, pady=(0, 10))
        
        username_label = tk.Label(
            username_frame,
            text="Username:",
            bg='#202020',
            fg='#e0e0e0',
            font=(self.font_family, 10),
            anchor='w'
        )
        username_label.pack(fill=tk.X, pady=(0, 5))
        
        username_entry = tk.Entry(
            username_frame,
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#ffffff',
            font=(self.font_family, 10),
            relief=tk.FLAT
        )
        username_entry.pack(fill=tk.X, ipady=8)
        username_entry.focus()
        
        # Password
        password_frame = tk.Frame(dialog, bg='#202020')
        password_frame.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        password_label = tk.Label(
            password_frame,
            text="Password:",
            bg='#202020',
            fg='#e0e0e0',
            font=(self.font_family, 10),
            anchor='w'
        )
        password_label.pack(fill=tk.X, pady=(0, 5))
        
        password_entry = tk.Entry(
            password_frame,
            bg='#2a2a2a',
            fg='#ffffff',
            insertbackground='#ffffff',
            font=(self.font_family, 10),
            relief=tk.FLAT,
            show='*'
        )
        password_entry.pack(fill=tk.X, ipady=8)
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='#202020')
        button_frame.pack(pady=(0, 20))
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password.")
                return
            
            # Try to login
            if self.processor.scraper.login(username, password):
                self.instagram_username = username
                self.instagram_password = password
                self.update_login_status()
                dialog.destroy()
                messagebox.showinfo("Success", "Successfully logged in to Instagram!\n\nThis will significantly reduce rate limiting.")
            else:
                messagebox.showerror("Login Failed", "Could not log in. Please check your credentials.")
        
        def cancel():
            dialog.destroy()
        
        login_btn = tk.Button(
            button_frame,
            text="Login",
            command=login,
            bg='#0078d4',
            fg='#ffffff',
            activebackground='#106ebe',
            activeforeground='#ffffff',
            borderwidth=0,
            font=(self.font_family, 10),
            padx=25,
            pady=8,
            cursor='hand2'
        )
        login_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=cancel,
            bg='#2a2a2a',
            fg='#ffffff',
            activebackground='#3a3a3a',
            activeforeground='#ffffff',
            borderwidth=0,
            font=(self.font_family, 10),
            padx=25,
            pady=8,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: login())
    
    def logout_instagram(self):
        """Logout from Instagram."""
        if self.processor.scraper.is_logged_in:
            self.processor.scraper.logout()
            self.instagram_username = None
            self.instagram_password = None
            self.update_login_status()
            messagebox.showinfo("Logged Out", "You have been logged out from Instagram.")
        else:
            messagebox.showinfo("Not Logged In", "You are not currently logged in.")
    
    def show_about(self):
        """Show about dialog."""
        login_status = "Logged in" if self.processor.scraper.is_logged_in else "Not logged in"
        about_text = f"""Show Finder v2.0

A tool to scrape Instagram posts from venue accounts
and display upcoming shows in a calendar view.

Features:
- Scrapes posts from multiple Instagram accounts
- Extracts show information from captions
- Uses OCR to read text from images
- Displays shows in a Windows 11 styled calendar
- Manage profiles with custom nicknames
- Fetch posts from the past week (max 20 posts)

Status: {login_status}

Note: Logging in significantly reduces rate limiting.
Tesseract OCR must be installed for image text extraction."""
        
        messagebox.showinfo("About Show Finder", about_text)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


if __name__ == '__main__':
    app = ShowFinderApp()
    app.run()
