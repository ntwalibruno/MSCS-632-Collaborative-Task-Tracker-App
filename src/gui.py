"""
Graphical User Interface for the to-do list application.

This module provides a comprehensive GUI using Tkinter with support for
multi-user authentication, task management, and real-time updates.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import threading
import time
from typing import Optional, Dict, List

try:
    from .task_manager import TaskManager
except ImportError:
    from task_manager import TaskManager


class LoginDialog:
    """Login/Registration dialog window."""
    
    def __init__(self, parent, task_manager):
        self.parent = parent
        self.task_manager = task_manager
        self.result = None
        self.user_info = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Login / Register")
        self.dialog.geometry("450x400")  # Increased size for better visibility
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login dialog UI."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Multi-User To-Do List", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Login tab
        login_frame = ttk.Frame(notebook, padding="10")
        notebook.add(login_frame, text="Login")
        
        ttk.Label(login_frame, text="Username:").pack(anchor=tk.W, pady=(0, 5))
        self.login_username = ttk.Entry(login_frame, width=30)
        self.login_username.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(login_frame, text="Password:").pack(anchor=tk.W, pady=(0, 5))
        self.login_password = ttk.Entry(login_frame, width=30, show="*")
        self.login_password.pack(fill=tk.X, pady=(0, 20))
        
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.pack(pady=(0, 10))
        
        # Register tab
        register_frame = ttk.Frame(notebook, padding="15")
        notebook.add(register_frame, text="Register")
        
        # Add a scrollable frame for register content
        canvas = tk.Canvas(register_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(register_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Registration form fields
        ttk.Label(scrollable_frame, text="Username (min 3 characters):").pack(anchor=tk.W, pady=(5, 5))
        self.register_username = ttk.Entry(scrollable_frame, width=35)
        self.register_username.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(scrollable_frame, text="Email (optional):").pack(anchor=tk.W, pady=(0, 5))
        self.register_email = ttk.Entry(scrollable_frame, width=35)
        self.register_email.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(scrollable_frame, text="Password (min 6 characters):").pack(anchor=tk.W, pady=(0, 5))
        self.register_password = ttk.Entry(scrollable_frame, width=35, show="*")
        self.register_password.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(scrollable_frame, text="Confirm Password:").pack(anchor=tk.W, pady=(0, 5))
        self.register_confirm = ttk.Entry(scrollable_frame, width=35, show="*")
        self.register_confirm.pack(fill=tk.X, pady=(0, 20))
        
        register_btn = ttk.Button(scrollable_frame, text="Register", command=self.register)
        register_btn.pack(pady=(10, 20))
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.login() if notebook.index(notebook.select()) == 0 else self.register())
    
    def login(self):
        """Handle login."""
        username = self.login_username.get().strip()
        password = self.login_password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
        
        success, message, user_info = self.task_manager.login(username, password)
        
        if success:
            self.result = "login"
            self.user_info = user_info
            self.dialog.destroy()
        else:
            messagebox.showerror("Login Failed", message)
    
    def register(self):
        """Handle registration."""
        username = self.register_username.get().strip()
        email = self.register_email.get().strip()
        password = self.register_password.get()
        confirm = self.register_confirm.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Username and password are required")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        success, message = self.task_manager.create_user(username, password, email or None)
        
        if success:
            messagebox.showinfo("Success", message)
            # Switch to login tab and fill username
            self.login_username.delete(0, tk.END)
            self.login_username.insert(0, username)
        else:
            messagebox.showerror("Registration Failed", message)


class TaskDialog:
    """Dialog for creating/editing tasks."""
    
    def __init__(self, parent, task_manager, task=None):
        self.parent = parent
        self.task_manager = task_manager
        self.task = task
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Task" if task else "New Task")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"500x400+{x}+{y}")
        
        self.setup_ui()
        
        if task:
            self.populate_fields()
    
    def setup_ui(self):
        """Setup the task dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text="Title:").pack(anchor=tk.W, pady=(0, 5))
        self.title_entry = ttk.Entry(main_frame, width=50)
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor=tk.W, pady=(0, 5))
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.description_text = tk.Text(desc_frame, height=5, wrap=tk.WORD)
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        
        self.description_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Category
        ttk.Label(main_frame, text="Category:").pack(anchor=tk.W, pady=(0, 5))
        self.category_combo = ttk.Combobox(main_frame, width=47, state="readonly")
        categories = self.task_manager.get_categories()
        category_names = [""] + [cat['name'] for cat in categories]
        self.category_combo['values'] = category_names
        self.category_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Assigned to
        ttk.Label(main_frame, text="Assign to:").pack(anchor=tk.W, pady=(0, 5))
        self.assigned_combo = ttk.Combobox(main_frame, width=47, state="readonly")
        users = self.task_manager.get_all_users()
        user_names = [""] + [user['username'] for user in users]
        self.assigned_combo['values'] = user_names
        self.assigned_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Priority and Due Date frame
        detail_frame = ttk.Frame(main_frame)
        detail_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Priority
        ttk.Label(detail_frame, text="Priority:").pack(side=tk.LEFT)
        self.priority_combo = ttk.Combobox(detail_frame, width=15, state="readonly")
        self.priority_combo['values'] = ['low', 'medium', 'high', 'urgent']
        self.priority_combo.set('medium')
        self.priority_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        # Due Date
        ttk.Label(detail_frame, text="Due Date:").pack(side=tk.LEFT)
        self.due_date_entry = ttk.Entry(detail_frame, width=20)
        self.due_date_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(detail_frame, text="(YYYY-MM-DD HH:MM)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT)
    
    def populate_fields(self):
        """Populate fields with existing task data."""
        if not self.task:
            return
        
        self.title_entry.insert(0, self.task.get('title', ''))
        
        if self.task.get('description'):
            self.description_text.insert(tk.END, self.task['description'])
        
        if self.task.get('category_name'):
            self.category_combo.set(self.task['category_name'])
        
        if self.task.get('assigned_to_username'):
            self.assigned_combo.set(self.task['assigned_to_username'])
        
        if self.task.get('priority'):
            self.priority_combo.set(self.task['priority'])
        
        if self.task.get('due_date'):
            self.due_date_entry.insert(0, self.task['due_date'])
    
    def save(self):
        """Save the task."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Title is required")
            return
        
        description = self.description_text.get(1.0, tk.END).strip()
        category = self.category_combo.get()
        assigned_to = self.assigned_combo.get()
        priority = self.priority_combo.get()
        due_date = self.due_date_entry.get().strip()
        
        self.result = {
            'title': title,
            'description': description if description else None,
            'category_name': category if category else None,
            'assigned_to_username': assigned_to if assigned_to else None,
            'priority': priority,
            'due_date': due_date if due_date else None
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel the dialog."""
        self.result = None
        self.dialog.destroy()


class GUIInterface:
    """Main GUI interface for the to-do list application."""
    
    def __init__(self, task_manager: TaskManager):
        """
        Initialize the GUI interface.
        
        Args:
            task_manager (TaskManager): Task manager instance
        """
        self.task_manager = task_manager
        self.current_session = None
        self.current_user = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("Multi-User To-Do List")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Auto-refresh thread
        self.auto_refresh_enabled = True
        self.auto_refresh_interval = 30  # seconds
        
        self.setup_ui()
        self.setup_menu()
        
        # Protocol for window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start auto-refresh
        self.start_auto_refresh()
    
    def setup_menu(self):
        """Setup the application menu."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Login", command=self.show_login)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Task menu
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tasks", menu=task_menu)
        task_menu.add_command(label="New Task", command=self.new_task)
        task_menu.add_command(label="Refresh", command=self.refresh_tasks)
        task_menu.add_separator()
        task_menu.add_command(label="Mark Completed", command=self.complete_selected_task)
        task_menu.add_command(label="Delete Task", command=self.delete_selected_task)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="All Tasks", command=lambda: self.load_tasks(show_all=True))
        view_menu.add_command(label="My Tasks", command=lambda: self.load_tasks(show_all=False))
        view_menu.add_separator()
        view_menu.add_command(label="Pending Only", command=lambda: self.load_tasks(status='pending'))
        view_menu.add_command(label="Completed Only", command=lambda: self.load_tasks(status='completed'))
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Statistics", command=self.show_statistics)
        tools_menu.add_command(label="Users", command=self.show_users)
        tools_menu.add_command(label="Categories", command=self.show_categories)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame for user info and controls
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # User info frame
        user_frame = ttk.LabelFrame(top_frame, text="User", padding="5")
        user_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.user_label = ttk.Label(user_frame, text="Not logged in", font=("Arial", 10, "bold"))
        self.user_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = ttk.Frame(top_frame)
        control_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.login_btn = ttk.Button(control_frame, text="Login", command=self.show_login)
        self.login_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.logout_btn = ttk.Button(control_frame, text="Logout", command=self.logout, state=tk.DISABLED)
        self.logout_btn.pack(side=tk.LEFT)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.main_frame, text="Filters", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT)
        self.status_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.status_filter['values'] = ['All', 'pending', 'in_progress', 'completed', 'cancelled']
        self.status_filter.set('All')
        self.status_filter.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)
        self.category_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.category_filter.pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT, padx=(5, 0))
        
        # Search frame
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_tasks())
        ttk.Button(search_frame, text="Search", command=self.search_tasks).pack(side=tk.LEFT)
        
        # Task list frame
        list_frame = ttk.LabelFrame(self.main_frame, text="Tasks", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Task tree
        columns = ('ID', 'Title', 'Category', 'Assigned', 'Priority', 'Status', 'Due Date', 'Created')
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.task_tree.heading('ID', text='ID')
        self.task_tree.heading('Title', text='Title')
        self.task_tree.heading('Category', text='Category')
        self.task_tree.heading('Assigned', text='Assigned To')
        self.task_tree.heading('Priority', text='Priority')
        self.task_tree.heading('Status', text='Status')
        self.task_tree.heading('Due Date', text='Due Date')
        self.task_tree.heading('Created', text='Created')
        
        # Configure column widths
        self.task_tree.column('ID', width=50, minwidth=50)
        self.task_tree.column('Title', width=200, minwidth=150)
        self.task_tree.column('Category', width=100, minwidth=80)
        self.task_tree.column('Assigned', width=100, minwidth=80)
        self.task_tree.column('Priority', width=80, minwidth=60)
        self.task_tree.column('Status', width=100, minwidth=80)
        self.task_tree.column('Due Date', width=130, minwidth=100)
        self.task_tree.column('Created', width=130, minwidth=100)
        
        # Scrollbars for tree
        tree_scroll_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        tree_scroll_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.task_tree.xview)
        self.task_tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)
        
        # Pack tree and scrollbars
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
        tree_scroll_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu for task tree
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Task", command=self.edit_selected_task)
        self.context_menu.add_command(label="Mark Completed", command=self.complete_selected_task)
        self.context_menu.add_command(label="Mark In Progress", command=lambda: self.update_selected_task_status('in_progress'))
        self.context_menu.add_command(label="Mark Pending", command=lambda: self.update_selected_task_status('pending'))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Task", command=self.delete_selected_task)
        
        self.task_tree.bind("<Button-3>", self.show_context_menu)  # Right click
        self.task_tree.bind("<Double-1>", lambda e: self.edit_selected_task())  # Double click
        
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="New Task", command=self.new_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Edit Task", command=self.edit_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Complete", command=self.complete_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self.delete_selected_task).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_tasks).pack(side=tk.RIGHT)
        
        # Status bar
        self.status_bar = ttk.Label(self.main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        # Initial UI state
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update UI state based on login status."""
        logged_in = self.current_session is not None
        
        if logged_in:
            self.user_label.config(text=f"Logged in as: {self.current_user['username']}")
            self.login_btn.config(state=tk.DISABLED)
            self.logout_btn.config(state=tk.NORMAL)
            self.status_bar.config(text=f"Logged in as {self.current_user['username']}")
        else:
            self.user_label.config(text="Not logged in")
            self.login_btn.config(state=tk.NORMAL)
            self.logout_btn.config(state=tk.DISABLED)
            self.status_bar.config(text="Please login to access tasks")
        
        # Update category filter
        self.update_category_filter()
        
        # Load tasks if logged in
        if logged_in:
            self.load_tasks()
        else:
            # Clear task list
            for item in self.task_tree.get_children():
                self.task_tree.delete(item)
    
    def update_category_filter(self):
        """Update the category filter combobox."""
        categories = self.task_manager.get_categories()
        category_names = ['All'] + [cat['name'] for cat in categories]
        self.category_filter['values'] = category_names
        if not self.category_filter.get():
            self.category_filter.set('All')
    
    def show_login(self):
        """Show login dialog."""
        if self.current_session:
            messagebox.showwarning("Already Logged In", "You are already logged in. Logout first to switch users.")
            return
        
        dialog = LoginDialog(self.root, self.task_manager)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result == "login" and dialog.user_info:
            self.current_session = dialog.user_info['session_id']
            self.current_user = dialog.user_info
            self.update_ui_state()
            messagebox.showinfo("Success", f"Welcome, {self.current_user['username']}!")
    
    def logout(self):
        """Logout current user."""
        if not self.current_session:
            return
        
        self.task_manager.logout(self.current_session)
        username = self.current_user['username']
        self.current_session = None
        self.current_user = None
        self.update_ui_state()
        messagebox.showinfo("Logged Out", f"Goodbye, {username}!")
    
    def load_tasks(self, status=None, category_name=None, show_all=None):
        """Load tasks into the tree view."""
        if not self.current_session:
            return
        
        # Determine show_all based on current user or parameter
        if show_all is None:
            show_all = False  # Default to user's tasks
        
        tasks = self.task_manager.get_tasks(
            session_id=self.current_session if not show_all else None,
            status=status,
            category_name=category_name,
            show_all=show_all
        )
        
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add tasks to tree
        for task in tasks:
            # Color code by status
            tags = []
            if task['status'] == 'completed':
                tags.append('completed')
            elif task['status'] == 'cancelled':
                tags.append('cancelled')
            elif task.get('is_overdue'):
                tags.append('overdue')
            elif task['priority'] == 'urgent':
                tags.append('urgent')
            
            self.task_tree.insert('', tk.END, values=(
                task['id'],
                task['title'][:50] + ('...' if len(task['title']) > 50 else ''),
                task['category_name'] or '',
                task['assigned_to_username'] or '',
                task['priority'],
                task['status'],
                task['due_date_formatted'],
                task['created_at_formatted']
            ), tags=tags)
        
        # Configure tag colors
        self.task_tree.tag_configure('completed', foreground='green')
        self.task_tree.tag_configure('cancelled', foreground='gray')
        self.task_tree.tag_configure('overdue', foreground='red', font=('Arial', 9, 'bold'))
        self.task_tree.tag_configure('urgent', foreground='darkred', font=('Arial', 9, 'bold'))
        
        # Update status bar
        self.status_bar.config(text=f"Loaded {len(tasks)} tasks")
    
    def apply_filters(self):
        """Apply current filters."""
        status = self.status_filter.get()
        category = self.category_filter.get()
        
        status = None if status == 'All' else status
        category = None if category == 'All' else category
        
        self.load_tasks(status=status, category_name=category)
    
    def clear_filters(self):
        """Clear all filters."""
        self.status_filter.set('All')
        self.category_filter.set('All')
        self.search_entry.delete(0, tk.END)
        self.load_tasks()
    
    def search_tasks(self):
        """Search tasks."""
        if not self.current_session:
            return
        
        query = self.search_entry.get().strip()
        if not query:
            self.load_tasks()
            return
        
        tasks = self.task_manager.search_tasks(query, self.current_session)
        
        # Clear existing items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Add matching tasks
        for task in tasks:
            tags = []
            if task['status'] == 'completed':
                tags.append('completed')
            elif task.get('is_overdue'):
                tags.append('overdue')
            
            self.task_tree.insert('', tk.END, values=(
                task['id'],
                task['title'][:50] + ('...' if len(task['title']) > 50 else ''),
                task['category_name'] or '',
                task['assigned_to_username'] or '',
                task['priority'],
                task['status'],
                task['due_date_formatted'],
                task['created_at_formatted']
            ), tags=tags)
        
        self.status_bar.config(text=f"Found {len(tasks)} tasks matching '{query}'")
    
    def refresh_tasks(self):
        """Refresh the task list."""
        self.apply_filters()
    
    def new_task(self):
        """Create a new task."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        dialog = TaskDialog(self.root, self.task_manager)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            success, message = self.task_manager.create_task(
                session_id=self.current_session,
                **dialog.result
            )
            
            if success:
                messagebox.showinfo("Success", message)
                self.refresh_tasks()
            else:
                messagebox.showerror("Error", message)
    
    def get_selected_task(self):
        """Get the currently selected task."""
        selection = self.task_tree.selection()
        if not selection:
            return None
        
        item = selection[0]
        values = self.task_tree.item(item, 'values')
        if not values:
            return None
        
        return {'id': int(values[0])}
    
    def edit_selected_task(self):
        """Edit the selected task."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return
        
        # Get full task details
        all_tasks = self.task_manager.get_tasks(session_id=self.current_session)
        task_details = None
        for t in all_tasks:
            if t['id'] == task['id']:
                task_details = t
                break
        
        if not task_details:
            messagebox.showerror("Error", "Task not found")
            return
        
        dialog = TaskDialog(self.root, self.task_manager, task_details)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # For now, we'll just show a message since we don't have edit functionality
            # In a full implementation, you'd add an edit_task method to TaskManager
            messagebox.showinfo("Edit Task", "Task editing would be implemented here")
    
    def complete_selected_task(self):
        """Mark selected task as completed."""
        self.update_selected_task_status('completed')
    
    def update_selected_task_status(self, status):
        """Update selected task status."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Please select a task")
            return
        
        success, message = self.task_manager.update_task_status(
            task['id'], status, self.current_session
        )
        
        if success:
            self.refresh_tasks()
            self.status_bar.config(text=message)
        else:
            messagebox.showerror("Error", message)
    
    def delete_selected_task(self):
        """Delete the selected task."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        task = self.get_selected_task()
        if not task:
            messagebox.showwarning("No Selection", "Please select a task to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task {task['id']}?"):
            success, message = self.task_manager.delete_task(task['id'], self.current_session)
            
            if success:
                self.refresh_tasks()
                self.status_bar.config(text=message)
            else:
                messagebox.showerror("Error", message)
    
    def show_context_menu(self, event):
        """Show context menu for task tree."""
        # Select the item under cursor
        item = self.task_tree.identify_row(event.y)
        if item:
            self.task_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def show_statistics(self):
        """Show task statistics."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        stats = self.task_manager.get_task_statistics(self.current_session)
        
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Task Statistics")
        stats_window.geometry("400x300")
        stats_window.transient(self.root)
        
        frame = ttk.Frame(stats_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Task Statistics", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Status counts
        ttk.Label(frame, text="Status Distribution:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        for status, count in stats.get('status_counts', {}).items():
            ttk.Label(frame, text=f"  {status.replace('_', ' ').title()}: {count}").pack(anchor=tk.W)
        
        ttk.Label(frame, text=f"\nTotal Tasks: {stats.get('total_tasks', 0)}", 
                 font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
        
        # Category counts
        if stats.get('category_counts'):
            ttk.Label(frame, text="\nCategory Distribution:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 0))
            for category, count in stats.get('category_counts', {}).items():
                ttk.Label(frame, text=f"  {category}: {count}").pack(anchor=tk.W)
    
    def show_users(self):
        """Show all users."""
        users = self.task_manager.get_all_users()
        
        users_window = tk.Toplevel(self.root)
        users_window.title("Registered Users")
        users_window.geometry("600x400")
        users_window.transient(self.root)
        
        frame = ttk.Frame(users_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Registered Users", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Users tree
        columns = ('ID', 'Username', 'Email', 'Last Login')
        users_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            users_tree.heading(col, text=col)
            users_tree.column(col, width=120)
        
        for user in users:
            last_login = "Never"
            if user['last_login']:
                try:
                    last_login = datetime.fromisoformat(user['last_login']).strftime('%Y-%m-%d %H:%M')
                except:
                    last_login = user['last_login']
            
            users_tree.insert('', tk.END, values=(
                user['id'],
                user['username'],
                user['email'] or 'N/A',
                last_login
            ))
        
        users_tree.pack(fill=tk.BOTH, expand=True)
    
    def show_categories(self):
        """Show all categories."""
        categories = self.task_manager.get_categories()
        
        cat_window = tk.Toplevel(self.root)
        cat_window.title("Task Categories")
        cat_window.geometry("600x400")
        cat_window.transient(self.root)
        
        frame = ttk.Frame(cat_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Task Categories", font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Categories tree
        columns = ('ID', 'Name', 'Description', 'Created By')
        cat_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            cat_tree.heading(col, text=col)
            cat_tree.column(col, width=120)
        
        for cat in categories:
            cat_tree.insert('', tk.END, values=(
                cat['id'],
                cat['name'],
                cat['description'] or 'N/A',
                cat['created_by_username'] or 'System'
            ))
        
        cat_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Add category button
        ttk.Button(frame, text="Add Category", command=self.add_category).pack()
    
    def add_category(self):
        """Add a new category."""
        if not self.current_session:
            messagebox.showwarning("Not Logged In", "Please login first")
            return
        
        name = simpledialog.askstring("New Category", "Category name:")
        if not name:
            return
        
        description = simpledialog.askstring("New Category", "Description (optional):")
        
        success, message = self.task_manager.create_category(
            name, description, session_id=self.current_session
        )
        
        if success:
            messagebox.showinfo("Success", message)
            self.update_category_filter()
        else:
            messagebox.showerror("Error", message)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """Multi-User To-Do List Application
        
Version: 1.0.0
Author: Advanced Programming Languages Course

Features:
• Multi-user support with authentication
• Task categorization and assignment
• Command-line and GUI interfaces
• SQLite database for data persistence
• Concurrent access support
• Real-time updates

Built with Python and Tkinter"""
        
        messagebox.showinfo("About", about_text)
    
    def start_auto_refresh(self):
        """Start auto-refresh thread."""
        def auto_refresh():
            while self.auto_refresh_enabled:
                time.sleep(self.auto_refresh_interval)
                if self.current_session and self.auto_refresh_enabled:
                    # Schedule refresh on main thread
                    self.root.after(0, self.refresh_tasks)
        
        thread = threading.Thread(target=auto_refresh, daemon=True)
        thread.start()
    
    def on_closing(self):
        """Handle application closing."""
        self.auto_refresh_enabled = False
        
        if self.current_session:
            self.task_manager.logout(self.current_session)
        
        self.root.destroy()
    
    def run(self):
        """Run the GUI application."""
        # Show login dialog on startup
        self.root.after(100, self.show_login)
        
        # Start the main loop
        self.root.mainloop()
