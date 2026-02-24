"""
Links management UI for adding and managing Instagram profile links.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
from links_manager import LinksManager


class LinksManagementUI:
    """UI for managing Instagram profile links and nicknames."""
    
    def __init__(self, parent, links_manager: LinksManager, on_fetch_callback: Callable = None, on_refetch_all_callback: Callable = None):
        self.root = parent if isinstance(parent, tk.Tk) else parent.winfo_toplevel()
        self.parent = parent
        self.links_manager = links_manager
        self.on_fetch_callback = on_fetch_callback
        self.on_refetch_all_callback = on_refetch_all_callback
        
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
            'error': '#d13438'
        }
        
        # Windows 11 font
        self.font_family = 'Segoe UI'
        self.font_normal = (self.font_family, 10)
        self.font_title = (self.font_family, 16, 'normal')
        self.font_subtitle = (self.font_family, 12, 'normal')
        self.font_small = (self.font_family, 9)
        
        self.setup_ui()
        self.refresh_links_list()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main container with padding
        main_frame = tk.Frame(self.parent, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Manage Instagram Profiles",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=self.font_title
        )
        title_label.pack(anchor='w', pady=(0, 20))
        
        # Add new link section
        add_frame = self.create_card(main_frame)
        add_frame.pack(fill=tk.X, pady=(0, 20))
        
        add_title = tk.Label(
            add_frame,
            text="Add New Profile",
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            font=self.font_subtitle
        )
        add_title.pack(anchor='w', pady=(15, 10), padx=20)
        
        # Link input
        link_frame = tk.Frame(add_frame, bg=self.colors['card_bg'])
        link_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        link_label = tk.Label(
            link_frame,
            text="Instagram Link or Username:",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=self.font_normal,
            anchor='w'
        )
        link_label.pack(fill=tk.X, pady=(0, 5))
        
        self.link_entry = tk.Entry(
            link_frame,
            bg=self.colors['secondary_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            font=self.font_normal,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.link_entry.pack(fill=tk.X, ipady=8)
        self.link_entry.bind('<FocusIn>', lambda e: self.link_entry.config(bg='#333333'))
        self.link_entry.bind('<FocusOut>', lambda e: self.link_entry.config(bg=self.colors['secondary_bg']))
        
        # Nickname input
        nickname_frame = tk.Frame(add_frame, bg=self.colors['card_bg'])
        nickname_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        nickname_label = tk.Label(
            nickname_frame,
            text="Display Name (Nickname):",
            bg=self.colors['card_bg'],
            fg=self.colors['text'],
            font=self.font_normal,
            anchor='w'
        )
        nickname_label.pack(fill=tk.X, pady=(0, 5))
        
        self.nickname_entry = tk.Entry(
            nickname_frame,
            bg=self.colors['secondary_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            font=self.font_normal,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.nickname_entry.pack(fill=tk.X, ipady=8)
        self.nickname_entry.bind('<FocusIn>', lambda e: self.nickname_entry.config(bg='#333333'))
        self.nickname_entry.bind('<FocusOut>', lambda e: self.nickname_entry.config(bg=self.colors['secondary_bg']))
        
        # Add button
        button_frame = tk.Frame(add_frame, bg=self.colors['card_bg'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        add_btn = self.create_button(
            button_frame,
            "Add Profile",
            self.add_link,
            is_primary=True
        )
        add_btn.pack(side=tk.LEFT)
        
        # Saved links section
        saved_frame = self.create_card(main_frame)
        saved_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        saved_title_frame = tk.Frame(saved_frame, bg=self.colors['card_bg'])
        saved_title_frame.pack(fill=tk.X, padx=20, pady=(15, 10))
        
        saved_title = tk.Label(
            saved_title_frame,
            text="Saved Profiles",
            bg=self.colors['card_bg'],
            fg=self.colors['fg'],
            font=self.font_subtitle
        )
        saved_title.pack(side=tk.LEFT)
        
        # Refetch all button
        refetch_all_btn = self.create_button(
            saved_title_frame,
            "Refetch All",
            self.refetch_all,
            is_primary=False
        )
        refetch_all_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Links list with scrollbar
        list_container = tk.Frame(saved_frame, bg=self.colors['card_bg'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_container, bg=self.colors['card_bg'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.links_listbox = tk.Listbox(
            list_container,
            bg=self.colors['secondary_bg'],
            fg=self.colors['fg'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['fg'],
            font=self.font_normal,
            relief=tk.FLAT,
            borderwidth=0,
            yscrollcommand=scrollbar.set
        )
        self.links_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.links_listbox.yview)
        
        # Action buttons for selected link
        action_frame = tk.Frame(saved_frame, bg=self.colors['card_bg'])
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        fetch_btn = self.create_button(
            action_frame,
            "Fetch Shows",
            self.fetch_selected,
            is_primary=True
        )
        fetch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        edit_btn = self.create_button(
            action_frame,
            "Edit Nickname",
            self.edit_selected,
            is_primary=False
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = self.create_button(
            action_frame,
            "Delete",
            self.delete_selected,
            is_primary=False,
            is_destructive=True
        )
        delete_btn.pack(side=tk.LEFT)
    
    def create_card(self, parent) -> tk.Frame:
        """Create a card-style frame with Windows 11 styling."""
        card = tk.Frame(
            parent,
            bg=self.colors['card_bg'],
            relief=tk.FLAT
        )
        return card
    
    def create_button(self, parent, text: str, command: Callable, is_primary: bool = False, is_destructive: bool = False) -> tk.Button:
        """Create a Windows 11 style button."""
        bg_color = self.colors['accent'] if is_primary else self.colors['secondary_bg']
        hover_color = self.colors['accent_hover'] if is_primary else self.colors['hover']
        
        if is_destructive:
            bg_color = self.colors['error']
            hover_color = '#b02a2e'
        
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
            padx=20,
            pady=8
        )
        
        # Add hover effect
        def on_enter(e):
            btn.config(bg=hover_color)
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        return btn
    
    def refresh_links_list(self):
        """Refresh the links listbox."""
        self.links_listbox.delete(0, tk.END)
        links = self.links_manager.get_all_links()
        for link in links:
            display_text = f"{link.get('nickname', link.get('username'))} (@{link.get('username')})"
            self.links_listbox.insert(tk.END, display_text)
    
    def add_link(self):
        """Add a new link."""
        link = self.link_entry.get().strip()
        nickname = self.nickname_entry.get().strip()
        
        if not link:
            messagebox.showerror("Error", "Please enter an Instagram link or username.")
            return
        
        success, message = self.links_manager.add_link(link, nickname)
        
        if success:
            self.link_entry.delete(0, tk.END)
            self.nickname_entry.delete(0, tk.END)
            self.refresh_links_list()
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
    
    def get_selected_username(self) -> str:
        """Get username from selected listbox item."""
        selection = self.links_listbox.curselection()
        if not selection:
            return None
        
        index = selection[0]
        links = self.links_manager.get_all_links()
        if index < len(links):
            return links[index].get('username')
        return None
    
    def fetch_selected(self):
        """Fetch shows for selected profile."""
        username = self.get_selected_username()
        if not username:
            messagebox.showwarning("No Selection", "Please select a profile to fetch shows from.")
            return
        
        if self.on_fetch_callback:
            self.on_fetch_callback([username])
    
    def edit_selected(self):
        """Edit nickname for selected profile."""
        username = self.get_selected_username()
        if not username:
            messagebox.showwarning("No Selection", "Please select a profile to edit.")
            return
        
        links = self.links_manager.get_all_links()
        current_link = next((l for l in links if l.get('username') == username), None)
        if not current_link:
            return
        
        current_nickname = current_link.get('nickname', username)
        
        # Simple dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Nickname")
        dialog.configure(bg=self.colors['bg'])
        dialog.geometry('400x150')
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = tk.Label(
            dialog,
            text=f"Edit nickname for @{username}:",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=self.font_normal
        )
        label.pack(pady=20)
        
        entry = tk.Entry(
            dialog,
            bg=self.colors['secondary_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            font=self.font_normal,
            relief=tk.FLAT
        )
        entry.insert(0, current_nickname)
        entry.pack(fill=tk.X, padx=20, ipady=8)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def save():
            new_nickname = entry.get().strip()
            if self.links_manager.update_link(username, new_nickname):
                self.refresh_links_list()
                dialog.destroy()
                messagebox.showinfo("Success", f"Nickname updated to '{new_nickname}'")
            else:
                messagebox.showerror("Error", "Failed to update nickname.")
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(pady=20)
        
        save_btn = self.create_button(button_frame, "Save", save, is_primary=True)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = self.create_button(button_frame, "Cancel", cancel, is_primary=False)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: save())
    
    def delete_selected(self):
        """Delete selected profile."""
        username = self.get_selected_username()
        if not username:
            messagebox.showwarning("No Selection", "Please select a profile to delete.")
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to remove @{username} from your saved profiles?"
        )
        
        if result:
            if self.links_manager.delete_link(username):
                self.refresh_links_list()
                messagebox.showinfo("Success", f"Removed @{username}")
            else:
                messagebox.showerror("Error", "Failed to delete profile.")
    
    def refetch_all(self):
        """Refetch shows from all saved profiles."""
        links = self.links_manager.get_all_links()
        if not links:
            messagebox.showwarning("No Profiles", "No saved profiles to fetch from.")
            return
        
        result = messagebox.askyesno(
            "Refetch All",
            f"Fetch shows from all {len(links)} saved profiles? This may take a while."
        )
        
        if result and self.on_refetch_all_callback:
            usernames = [link.get('username') for link in links]
            self.on_refetch_all_callback(usernames)
