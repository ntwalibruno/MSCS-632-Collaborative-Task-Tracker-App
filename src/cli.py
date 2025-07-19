"""
Command-line interface for the to-do list application.

This module provides a comprehensive CLI for managing tasks, users, and categories
with colored output and tabulated data display.
"""

import sys
import getpass
from datetime import datetime
from typing import Optional, Dict

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback when colorama is not available
    class Fore:
        RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

try:
    from tabulate import tabulate
    TABULATE_AVAILABLE = True
except ImportError:
    TABULATE_AVAILABLE = False

try:
    from .task_manager import TaskManager
except ImportError:
    from task_manager import TaskManager


class CLIInterface:
    """Command-line interface for the to-do list application."""
    
    def __init__(self, task_manager: TaskManager):
        """
        Initialize the CLI interface.
        
        Args:
            task_manager (TaskManager): Task manager instance
        """
        self.task_manager = task_manager
        self.current_session = None
        self.current_user = None
        
        # CLI commands mapping
        self.commands = {
            'help': self.show_help,
            'h': self.show_help,
            'register': self.register_user,
            'login': self.login_user,
            'logout': self.logout_user,
            'users': self.list_users,
            'categories': self.list_categories,
            'addcat': self.add_category,
            'add': self.add_task,
            'list': self.list_tasks,
            'my': self.list_my_tasks,
            'all': self.list_all_tasks,
            'pending': self.list_pending_tasks,
            'completed': self.list_completed_tasks,
            'update': self.update_task_status,
            'complete': self.complete_task,
            'delete': self.delete_task,
            'search': self.search_tasks,
            'stats': self.show_statistics,
            'summary': self.show_summary,
            'clear': self.clear_screen,
            'quit': self.quit_application,
            'exit': self.quit_application,
            'q': self.quit_application
        }
    
    def print_colored(self, text: str, color: str = "", style: str = ""):
        """Print colored text if colors are available."""
        if COLORS_AVAILABLE:
            print(f"{style}{color}{text}{Style.RESET_ALL}")
        else:
            print(text)
    
    def print_success(self, message: str):
        """Print success message in green."""
        self.print_colored(f"✓ {message}", Fore.GREEN, Style.BRIGHT)
    
    def print_error(self, message: str):
        """Print error message in red."""
        self.print_colored(f"✗ {message}", Fore.RED, Style.BRIGHT)
    
    def print_warning(self, message: str):
        """Print warning message in yellow."""
        self.print_colored(f"⚠ {message}", Fore.YELLOW, Style.BRIGHT)
    
    def print_info(self, message: str):
        """Print info message in blue."""
        self.print_colored(f"ℹ {message}", Fore.BLUE)
    
    def print_header(self, title: str):
        """Print section header."""
        separator = "=" * len(title)
        self.print_colored(f"\n{separator}", Fore.CYAN, Style.BRIGHT)
        self.print_colored(title, Fore.CYAN, Style.BRIGHT)
        self.print_colored(separator, Fore.CYAN, Style.BRIGHT)
    
    def print_table(self, data: list, headers: list):
        """Print tabulated data."""
        if TABULATE_AVAILABLE and data:
            print(tabulate(data, headers=headers, tablefmt="grid"))
        else:
            # Fallback without tabulate
            if not data:
                self.print_info("No data to display")
                return
            
            # Print headers
            header_str = " | ".join(f"{str(h):15}" for h in headers)
            print(header_str)
            print("-" * len(header_str))
            
            # Print data rows
            for row in data:
                row_str = " | ".join(f"{str(cell):15}" for cell in row)
                print(row_str)
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """Get user input with validation."""
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if required and not value:
                    self.print_error("This field is required")
                    continue
                return value
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return ""
            except EOFError:
                print("\nGoodbye!")
                sys.exit(0)
    
    def get_password(self, prompt: str = "Password") -> str:
        """Get password input securely."""
        try:
            return getpass.getpass(f"{prompt}: ")
        except KeyboardInterrupt:
            print("\nOperation cancelled")
            return ""
        except EOFError:
            print("\nGoodbye!")
            sys.exit(0)
    
    def show_banner(self):
        """Display application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Multi-User To-Do List                     ║
║                     Command Line Interface                   ║
╚══════════════════════════════════════════════════════════════╝
        """
        self.print_colored(banner, Fore.CYAN, Style.BRIGHT)
        
        if self.current_user:
            self.print_colored(f"Logged in as: {self.current_user['username']}", 
                             Fore.GREEN, Style.BRIGHT)
        else:
            self.print_warning("Not logged in. Type 'login' or 'register' to get started.")
        
        print("Type 'help' for available commands.\n")
    
    def show_help(self, *args):
        """Display help information."""
        self.print_header("Available Commands")
        
        commands_help = [
            ("Authentication", ""),
            ("register", "Register a new user account"),
            ("login", "Login to your account"),
            ("logout", "Logout from current session"),
            ("", ""),
            ("User & Category Management", ""),
            ("users", "List all registered users"),
            ("categories", "List all task categories"),
            ("addcat <name>", "Add a new category"),
            ("", ""),
            ("Task Management", ""),
            ("add", "Add a new task (interactive)"),
            ("list [status] [category]", "List tasks with optional filters"),
            ("my", "List your tasks"),
            ("all", "List all tasks (admin view)"),
            ("pending", "List pending tasks"),
            ("completed", "List completed tasks"),
            ("update <id> <status>", "Update task status"),
            ("complete <id>", "Mark task as completed"),
            ("delete <id>", "Delete a task"),
            ("search <query>", "Search tasks by title/description"),
            ("", ""),
            ("Information", ""),
            ("stats", "Show task statistics"),
            ("summary", "Show your task summary"),
            ("", ""),
            ("Utility", ""),
            ("clear", "Clear screen"),
            ("help", "Show this help"),
            ("quit/exit/q", "Exit application")
        ]
        
        for cmd, desc in commands_help:
            if not cmd:
                print()
                continue
            elif not desc:
                self.print_colored(f"{cmd}:", Fore.YELLOW, Style.BRIGHT)
                continue
            else:
                print(f"  {cmd:20} - {desc}")
    
    def register_user(self, *args):
        """Register a new user."""
        self.print_header("User Registration")
        
        username = self.get_input("Username (min 3 characters)")
        if not username:
            return
        
        email = self.get_input("Email (optional)", required=False)
        
        password = self.get_password("Password (min 6 characters)")
        if not password:
            return
        
        confirm_password = self.get_password("Confirm password")
        if password != confirm_password:
            self.print_error("Passwords do not match")
            return
        
        success, message = self.task_manager.create_user(username, password, email)
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def login_user(self, *args):
        """Login user."""
        if self.current_session:
            self.print_warning("Already logged in. Logout first to switch users.")
            return
        
        self.print_header("User Login")
        
        username = self.get_input("Username")
        if not username:
            return
        
        password = self.get_password()
        if not password:
            return
        
        success, message, user = self.task_manager.login(username, password)
        if success:
            self.current_session = user['session_id']
            self.current_user = user
            self.print_success(message)
        else:
            self.print_error(message)
    
    def logout_user(self, *args):
        """Logout current user."""
        if not self.current_session:
            self.print_warning("Not logged in")
            return
        
        self.task_manager.logout(self.current_session)
        self.print_success(f"Goodbye, {self.current_user['username']}!")
        self.current_session = None
        self.current_user = None
    
    def list_users(self, *args):
        """List all registered users."""
        self.print_header("Registered Users")
        users = self.task_manager.get_all_users()
        
        if not users:
            self.print_info("No users registered")
            return
        
        user_data = []
        for user in users:
            last_login = "Never"
            if user['last_login']:
                try:
                    last_login = datetime.fromisoformat(user['last_login']).strftime('%Y-%m-%d %H:%M')
                except:
                    last_login = user['last_login']
            
            user_data.append([
                user['id'],
                user['username'],
                user['email'] or 'N/A',
                last_login
            ])
        
        self.print_table(user_data, ['ID', 'Username', 'Email', 'Last Login'])
    
    def list_categories(self, *args):
        """List all categories."""
        self.print_header("Task Categories")
        categories = self.task_manager.get_categories()
        
        if not categories:
            self.print_info("No categories available")
            return
        
        cat_data = []
        for cat in categories:
            cat_data.append([
                cat['id'],
                cat['name'],
                cat['description'] or 'N/A',
                cat['created_by_username'] or 'System'
            ])
        
        self.print_table(cat_data, ['ID', 'Name', 'Description', 'Created By'])
    
    def add_category(self, *args):
        """Add a new category."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        self.print_header("Add New Category")
        
        name = self.get_input("Category name")
        if not name:
            return
        
        description = self.get_input("Description (optional)", required=False)
        color = self.get_input("Color (hex, e.g., #FF5722)", required=False) or '#0078D4'
        
        success, message = self.task_manager.create_category(name, description, color, self.current_session)
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def add_task(self, *args):
        """Add a new task interactively."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        self.print_header("Add New Task")
        
        title = self.get_input("Task title")
        if not title:
            return
        
        description = self.get_input("Description (optional)", required=False)
        
        # Show available categories
        categories = self.task_manager.get_categories()
        if categories:
            print("\nAvailable categories:")
            for cat in categories:
                print(f"  - {cat['name']}")
        
        category = self.get_input("Category (optional)", required=False)
        
        # Show available users
        users = self.task_manager.get_all_users()
        if users:
            print("\nAvailable users:")
            for user in users:
                print(f"  - {user['username']}")
        
        assigned_to = self.get_input("Assign to user (optional)", required=False)
        
        priority = self.get_input("Priority (low/medium/high/urgent)", required=False) or 'medium'
        due_date = self.get_input("Due date (YYYY-MM-DD HH:MM, optional)", required=False)
        
        success, message = self.task_manager.create_task(
            title=title,
            description=description,
            category_name=category,
            assigned_to_username=assigned_to,
            priority=priority,
            due_date=due_date,
            session_id=self.current_session
        )
        
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def list_tasks(self, *args):
        """List tasks with optional filters."""
        status_filter = args[0] if args else None
        category_filter = args[1] if len(args) > 1 else None
        
        tasks = self.task_manager.get_tasks(
            session_id=self.current_session,
            status=status_filter,
            category_name=category_filter
        )
        
        self._display_tasks(tasks, f"Tasks (Filtered: status={status_filter}, category={category_filter})")
    
    def list_my_tasks(self, *args):
        """List current user's tasks."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        tasks = self.task_manager.get_tasks(session_id=self.current_session)
        self._display_tasks(tasks, "My Tasks")
    
    def list_all_tasks(self, *args):
        """List all tasks (admin view)."""
        tasks = self.task_manager.get_tasks(show_all=True)
        self._display_tasks(tasks, "All Tasks")
    
    def list_pending_tasks(self, *args):
        """List pending tasks."""
        tasks = self.task_manager.get_tasks(session_id=self.current_session, status='pending')
        self._display_tasks(tasks, "Pending Tasks")
    
    def list_completed_tasks(self, *args):
        """List completed tasks."""
        tasks = self.task_manager.get_tasks(session_id=self.current_session, status='completed')
        self._display_tasks(tasks, "Completed Tasks")
    
    def _display_tasks(self, tasks: list, title: str):
        """Display tasks in a formatted table."""
        self.print_header(title)
        
        if not tasks:
            self.print_info("No tasks found")
            return
        
        task_data = []
        for task in tasks:
            status_color = {
                'pending': '🔄',
                'in_progress': '⏳',
                'completed': '✅',
                'cancelled': '❌'
            }.get(task['status'], '❓')
            
            priority_color = {
                'low': '🔵',
                'medium': '🟡',
                'high': '🟠',
                'urgent': '🔴'
            }.get(task['priority'], '⚪')
            
            overdue_marker = '⚠️' if task.get('is_overdue') else ''
            
            task_data.append([
                task['id'],
                f"{status_color} {task['title'][:30]}",
                task['category_name'] or 'None',
                task['assigned_to_username'] or 'Unassigned',
                f"{priority_color} {task['priority']}",
                task['status'],
                f"{overdue_marker} {task['due_date_formatted']}".strip()
            ])
        
        self.print_table(task_data, 
                        ['ID', 'Title', 'Category', 'Assigned To', 'Priority', 'Status', 'Due Date'])
        
        print(f"\nShowing {len(tasks)} task(s)")
    
    def update_task_status(self, *args):
        """Update task status."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        if len(args) < 2:
            self.print_error("Usage: update <task_id> <status>")
            self.print_info("Valid statuses: pending, in_progress, completed, cancelled")
            return
        
        try:
            task_id = int(args[0])
            status = args[1]
        except ValueError:
            self.print_error("Task ID must be a number")
            return
        
        success, message = self.task_manager.update_task_status(task_id, status, self.current_session)
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def complete_task(self, *args):
        """Mark task as completed."""
        if not args:
            self.print_error("Usage: complete <task_id>")
            return
        
        try:
            task_id = int(args[0])
        except ValueError:
            self.print_error("Task ID must be a number")
            return
        
        success, message = self.task_manager.update_task_status(task_id, 'completed', self.current_session)
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def delete_task(self, *args):
        """Delete a task."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        if not args:
            self.print_error("Usage: delete <task_id>")
            return
        
        try:
            task_id = int(args[0])
        except ValueError:
            self.print_error("Task ID must be a number")
            return
        
        confirm = self.get_input(f"Are you sure you want to delete task {task_id}? (y/N)", required=False)
        if confirm.lower() != 'y':
            self.print_info("Deletion cancelled")
            return
        
        success, message = self.task_manager.delete_task(task_id, self.current_session)
        if success:
            self.print_success(message)
        else:
            self.print_error(message)
    
    def search_tasks(self, *args):
        """Search tasks."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        if not args:
            query = self.get_input("Search query")
        else:
            query = ' '.join(args)
        
        if not query:
            return
        
        tasks = self.task_manager.search_tasks(query, self.current_session)
        self._display_tasks(tasks, f"Search Results for '{query}'")
    
    def show_statistics(self, *args):
        """Show task statistics."""
        stats = self.task_manager.get_task_statistics(self.current_session)
        
        self.print_header("Task Statistics")
        
        print("Status Distribution:")
        for status, count in stats.get('status_counts', {}).items():
            print(f"  {status.replace('_', ' ').title()}: {count}")
        
        print(f"\nTotal Tasks: {stats.get('total_tasks', 0)}")
        
        print("\nCategory Distribution:")
        for category, count in stats.get('category_counts', {}).items():
            print(f"  {category}: {count}")
    
    def show_summary(self, *args):
        """Show user task summary."""
        if not self.current_session:
            self.print_error("Please login first")
            return
        
        summary = self.task_manager.get_user_tasks_summary(self.current_session)
        
        self.print_header(f"Task Summary for {self.current_user['username']}")
        
        print(f"Total Tasks: {summary.get('total_tasks', 0)}")
        print(f"Pending: {summary.get('pending', 0)}")
        print(f"In Progress: {summary.get('in_progress', 0)}")
        print(f"Completed: {summary.get('completed', 0)}")
        print(f"Overdue: {summary.get('overdue', 0)}")
        print(f"Assigned to Me: {summary.get('assigned_to_me', 0)}")
        print(f"Created by Me: {summary.get('created_by_me', 0)}")
    
    def clear_screen(self, *args):
        """Clear the screen."""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        self.show_banner()
    
    def quit_application(self, *args):
        """Quit the application."""
        if self.current_session:
            self.task_manager.logout(self.current_session)
        
        self.print_success("Thank you for using the To-Do List application!")
        sys.exit(0)
    
    def process_command(self, command_line: str):
        """Process a command line input."""
        if not command_line.strip():
            return
        
        parts = command_line.strip().split()
        command = parts[0].lower()
        args = parts[1:]
        
        if command in self.commands:
            try:
                self.commands[command](*args)
            except KeyboardInterrupt:
                print("\nCommand interrupted")
            except Exception as e:
                self.print_error(f"Command error: {e}")
        else:
            self.print_error(f"Unknown command: {command}")
            self.print_info("Type 'help' for available commands")
    
    def run(self):
        """Run the CLI interface."""
        try:
            self.clear_screen()
            
            while True:
                try:
                    prompt = f"[{self.current_user['username']}] > " if self.current_user else "> "
                    command = input(prompt).strip()
                    
                    if command:
                        self.process_command(command)
                    
                except KeyboardInterrupt:
                    print("\nUse 'quit' to exit")
                except EOFError:
                    print("\nGoodbye!")
                    break
                    
        except Exception as e:
            self.print_error(f"Application error: {e}")
        finally:
            if self.current_session:
                self.task_manager.logout(self.current_session)
