"""
Calendar UI module with Windows 11 dark theme to display shows.
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
from typing import List, Dict
import calendar as cal_lib


class CalendarUI:
    """Windows 11 styled calendar UI to display shows."""
    
    def __init__(self, parent):
        self.root = parent if isinstance(parent, tk.Tk) else parent.winfo_toplevel()
        self.parent = parent
        
        # Windows 11 style colors
        self.colors = {
            'bg': '#202020',
            'fg': '#ffffff',
            'secondary_bg': '#2a2a2a',
            'card_bg': '#2d2d2d',
            'accent': '#0078d4',
            'accent_hover': '#106ebe',
            'hover': '#3a3a3a',
            'text': '#e0e0e0',
            'text_secondary': '#a0a0a0',
            'border': '#404040',
            'today_bg': '#0078d4',
            'today_fg': '#ffffff'
        }
        
        # Windows 11 font
        self.font_family = 'Segoe UI'
        self.font_normal = (self.font_family, 10)
        self.font_title = (self.font_family, 18, 'normal')
        self.font_subtitle = (self.font_family, 12, 'normal')
        self.font_small = (self.font_family, 9)
        self.font_bold = (self.font_family, 10, 'bold')
        
        self.shows = []  # List of show dictionaries
        self.current_date = datetime.now()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container
        main_frame = tk.Frame(self.parent, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header with navigation
        header_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Previous month button
        prev_btn = self.create_button(
            header_frame,
            '◀',
            self.prev_month,
            is_primary=False,
            width=40
        )
        prev_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Month/Year label
        self.month_label = tk.Label(
            header_frame,
            text='',
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=self.font_title
        )
        self.month_label.pack(side=tk.LEFT, expand=True)
        
        # Next month button
        next_btn = self.create_button(
            header_frame,
            '▶',
            self.next_month,
            is_primary=False,
            width=40
        )
        next_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Today button
        today_btn = self.create_button(
            header_frame,
            'Today',
            self.go_to_today,
            is_primary=True
        )
        today_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Calendar frame
        calendar_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        calendar_frame.pack(fill=tk.BOTH, expand=True)
        
        # Day names header
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(day_names):
            label = tk.Label(
                calendar_frame,
                text=day,
                bg=self.colors['card_bg'],
                fg=self.colors['text'],
                font=self.font_bold,
                relief=tk.FLAT
            )
            label.grid(row=0, column=i, padx=3, pady=3, sticky='nsew')
        
        # Calendar grid
        self.calendar_cells = []
        for row in range(6):
            row_cells = []
            for col in range(7):
                cell_frame = self.create_card(calendar_frame)
                cell_frame.grid(row=row+1, column=col, padx=3, pady=3, sticky='nsew')
                
                # Date label
                date_label = tk.Label(
                    cell_frame,
                    text='',
                    bg=self.colors['card_bg'],
                    fg=self.colors['fg'],
                    font=self.font_bold,
                    anchor='nw',
                    relief=tk.FLAT
                )
                date_label.pack(fill=tk.X, padx=8, pady=6)
                
                # Shows list
                shows_frame = tk.Frame(cell_frame, bg=self.colors['card_bg'])
                shows_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=(0, 4))
                
                row_cells.append({
                    'frame': cell_frame,
                    'date_label': date_label,
                    'shows_frame': shows_frame
                })
            self.calendar_cells.append(row_cells)
        
        # Configure grid weights
        for i in range(7):
            calendar_frame.columnconfigure(i, weight=1)
        for i in range(6):
            calendar_frame.rowconfigure(i+1, weight=1)
        
        # Update calendar display
        self.update_calendar()
    
    def create_card(self, parent) -> tk.Frame:
        """Create a card-style frame with Windows 11 styling."""
        card = tk.Frame(
            parent,
            bg=self.colors['card_bg'],
            relief=tk.FLAT
        )
        return card
    
    def create_button(self, parent, text: str, command, is_primary: bool = False, width: int = None) -> tk.Button:
        """Create a Windows 11 style button."""
        bg_color = self.colors['accent'] if is_primary else self.colors['secondary_bg']
        hover_color = self.colors['accent_hover'] if is_primary else self.colors['hover']
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=self.colors['fg'],
            activebackground=hover_color,
            activeforeground=self.colors['fg'],
            borderwidth=0,
            font=self.font_normal,
            relief=tk.FLAT,
            cursor='hand2',
            padx=15,
            pady=8,
            width=width
        )
        
        # Add hover effect
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def prev_month(self):
        """Navigate to previous month."""
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)
        self.update_calendar()
    
    def next_month(self):
        """Navigate to next month."""
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)
        self.update_calendar()
    
    def go_to_today(self):
        """Navigate to current month."""
        self.current_date = datetime.now()
        self.update_calendar()
    
    def get_shows_for_date(self, date: datetime) -> List[Dict]:
        """Get all shows for a specific date."""
        date_str = date.strftime('%Y-%m-%d')
        return [show for show in self.shows if show.get('date') == date_str]
    
    def on_show_click(self, show: Dict):
        """Handle click on a show item."""
        display_name = show.get('display_name', show.get('username', 'Unknown'))
        details = f"Venue: {display_name}\n"
        details += f"Date: {show.get('date', 'Unknown')}\n"
        details += f"Time: {show.get('time', 'Unknown')}\n"
        details += f"Location: {show.get('location', 'Unknown')}\n"
        details += f"\nCaption:\n{show.get('caption', 'N/A')[:200]}...\n"
        details += f"\nPost URL: {show.get('post_url', 'N/A')}"
        
        messagebox.showinfo("Show Details", details)
    
    def update_calendar(self):
        """Update the calendar display with shows."""
        # Update month label
        month_name = self.current_date.strftime('%B %Y')
        self.month_label.config(text=month_name)
        
        # Get first day of month and number of days
        first_day = self.current_date.replace(day=1)
        first_weekday = first_day.weekday()  # 0 = Monday, 6 = Sunday
        num_days = cal_lib.monthrange(self.current_date.year, self.current_date.month)[1]
        
        # Clear all cells
        for row in self.calendar_cells:
            for cell in row:
                cell['date_label'].config(text='', bg=self.colors['card_bg'], fg=self.colors['fg'])
                # Clear shows
                for widget in cell['shows_frame'].winfo_children():
                    widget.destroy()
        
        # Fill calendar
        current_day = 1
        start_row = 0
        start_col = first_weekday
        
        for row in range(6):
            for col in range(7):
                if current_day > num_days:
                    break
                
                if row == start_row and col < start_col:
                    continue
                
                cell = self.calendar_cells[row][col]
                date_obj = datetime(self.current_date.year, self.current_date.month, current_day)
                
                # Update date label
                cell['date_label'].config(text=str(current_day))
                
                # Highlight today
                today = datetime.now()
                if (date_obj.year == today.year and 
                    date_obj.month == today.month and 
                    date_obj.day == today.day):
                    cell['date_label'].config(bg=self.colors['today_bg'], fg=self.colors['today_fg'])
                    cell['frame'].config(bg=self.colors['card_bg'])
                else:
                    cell['date_label'].config(bg=self.colors['card_bg'], fg=self.colors['fg'])
                    cell['frame'].config(bg=self.colors['card_bg'])
                
                # Add shows for this date
                shows_for_date = self.get_shows_for_date(date_obj)
                for show in shows_for_date[:3]:  # Limit to 3 shows per day for display
                    display_name = show.get('display_name', show.get('location', 'Unknown'))
                    show_text = f"• {display_name[:18]}"
                    if show.get('time') and show['time'] != 'Unknown':
                        show_text += f" @ {show['time'][:5]}"
                    
                    show_btn = tk.Button(
                        cell['shows_frame'],
                        text=show_text,
                        bg=self.colors['secondary_bg'],
                        fg=self.colors['fg'],
                        activebackground=self.colors['accent'],
                        activeforeground=self.colors['fg'],
                        borderwidth=0,
                        font=self.font_small,
                        anchor='w',
                        command=lambda s=show: self.on_show_click(s),
                        cursor='hand2',
                        relief=tk.FLAT
                    )
                    show_btn.pack(fill=tk.X, padx=2, pady=1)
                    
                    # Add hover effect
                    def on_enter(e, btn=show_btn):
                        btn.config(bg=self.colors['hover'])
                    
                    def on_leave(e, btn=show_btn):
                        btn.config(bg=self.colors['secondary_bg'])
                    
                    show_btn.bind('<Enter>', on_enter)
                    show_btn.bind('<Leave>', on_leave)
                
                if len(shows_for_date) > 3:
                    more_label = tk.Label(
                        cell['shows_frame'],
                        text=f"+{len(shows_for_date) - 3} more",
                        bg=self.colors['card_bg'],
                        fg=self.colors['accent'],
                        font=self.font_small
                    )
                    more_label.pack(fill=tk.X, padx=2)
                
                current_day += 1
    
    def set_shows(self, shows: List[Dict]):
        """Set the shows to display."""
        self.shows = shows
        self.update_calendar()
