"""
Task management module providing high-level operations for the to-do list application.

This module acts as a business logic layer between the database and user interfaces,
providing thread-safe operations and managing user sessions.
"""

import threading
from typing import List, Dict, Optional, Tuple
from datetime import datetime

try:
    from .database import DatabaseManager
except ImportError:
    from database import DatabaseManager


class TaskManager:
    """Manages task operations with user authentication and concurrency support."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the task manager.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
        """
        self.db = db_manager
        self._sessions = {}  # Active user sessions
        self._session_lock = threading.RLock()
    
    def create_user(self, username: str, password: str, email: str = None) -> Tuple[bool, str]:
        """
        Create a new user account.
        
        Args:
            username (str): Desired username
            password (str): Password
            email (str): Email address (optional)
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if len(username.strip()) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if self.db.create_user(username.strip(), password, email):
            return True, f"User '{username}' created successfully"
        else:
            return False, f"Username '{username}' already exists"
    
    def login(self, username: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate a user and create a session.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: (Success, Message, User info)
        """
        user = self.db.authenticate_user(username, password)
        if user:
            with self._session_lock:
                session_id = f"session_{user['id']}_{datetime.now().timestamp()}"
                self._sessions[session_id] = {
                    'user_id': user['id'],
                    'username': user['username'],
                    'login_time': datetime.now(),
                    'last_activity': datetime.now()
                }
            
            user['session_id'] = session_id
            return True, f"Welcome back, {user['username']}!", user
        else:
            return False, "Invalid username or password", None
    
    def logout(self, session_id: str) -> bool:
        """
        End a user session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            bool: True if logout successful
        """
        with self._session_lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    def get_session_user(self, session_id: str) -> Optional[Dict]:
        """
        Get user information from session.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Optional[Dict]: User information if session valid
        """
        with self._session_lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                session['last_activity'] = datetime.now()
                return {
                    'user_id': session['user_id'],
                    'username': session['username']
                }
            return None
    
    def is_session_valid(self, session_id: str) -> bool:
        """Check if a session is valid."""
        with self._session_lock:
            return session_id in self._sessions
    
    def get_all_users(self) -> List[Dict]:
        """Get all registered users."""
        return self.db.get_all_users()
    
    def create_category(self, name: str, description: str = None, 
                       color: str = '#0078D4', session_id: str = None) -> Tuple[bool, str]:
        """
        Create a new task category.
        
        Args:
            name (str): Category name
            description (str): Category description
            color (str): Category color (hex)
            session_id (str): User session ID
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        created_by = None
        if session_id:
            user = self.get_session_user(session_id)
            if user:
                created_by = user['user_id']
        
        if self.db.create_category(name.strip(), description, color, created_by):
            return True, f"Category '{name}' created successfully"
        else:
            return False, f"Category '{name}' already exists"
    
    def get_categories(self) -> List[Dict]:
        """Get all available categories."""
        return self.db.get_categories()
    
    def create_task(self, title: str, description: str = None, category_name: str = None,
                   assigned_to_username: str = None, priority: str = 'medium',
                   due_date: str = None, session_id: str = None) -> Tuple[bool, str]:
        """
        Create a new task.
        
        Args:
            title (str): Task title
            description (str): Task description
            category_name (str): Category name
            assigned_to_username (str): Username to assign task to
            priority (str): Task priority (low, medium, high, urgent)
            due_date (str): Due date (ISO format)
            session_id (str): Creator's session ID
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if not title.strip():
            return False, "Task title cannot be empty"
        
        # Get creator user ID
        created_by = None
        if session_id:
            user = self.get_session_user(session_id)
            if user:
                created_by = user['user_id']
            else:
                return False, "Invalid session"
        
        # Get category ID
        category_id = None
        if category_name:
            categories = self.get_categories()
            for cat in categories:
                if cat['name'].lower() == category_name.lower():
                    category_id = cat['id']
                    break
            
            if category_id is None:
                return False, f"Category '{category_name}' not found"
        
        # Get assigned user ID
        assigned_to = None
        if assigned_to_username:
            users = self.get_all_users()
            for user in users:
                if user['username'].lower() == assigned_to_username.lower():
                    assigned_to = user['id']
                    break
            
            if assigned_to is None:
                return False, f"User '{assigned_to_username}' not found"
        
        # Validate priority
        if priority not in ['low', 'medium', 'high', 'urgent']:
            priority = 'medium'
        
        task_id = self.db.create_task(
            title=title.strip(),
            description=description,
            category_id=category_id,
            assigned_to=assigned_to,
            created_by=created_by,
            priority=priority,
            due_date=due_date
        )
        
        if task_id:
            return True, f"Task '{title}' created successfully (ID: {task_id})"
        else:
            return False, "Failed to create task"
    
    def get_tasks(self, session_id: str = None, status: str = None, 
                 category_name: str = None, show_all: bool = False) -> List[Dict]:
        """
        Get tasks with optional filtering.
        
        Args:
            session_id (str): User session ID (for user-specific tasks)
            status (str): Filter by status
            category_name (str): Filter by category name
            show_all (bool): Show all tasks (admin view)
            
        Returns:
            List[Dict]: List of tasks
        """
        user_id = None
        if session_id and not show_all:
            user = self.get_session_user(session_id)
            if user:
                user_id = user['user_id']
        
        # Get category ID if specified
        category_id = None
        if category_name:
            categories = self.get_categories()
            for cat in categories:
                if cat['name'].lower() == category_name.lower():
                    category_id = cat['id']
                    break
        
        tasks = self.db.get_tasks(user_id=user_id, status=status, category_id=category_id)
        
        # Add formatted due date and time since creation
        for task in tasks:
            if task['due_date']:
                try:
                    due_date = datetime.fromisoformat(task['due_date'])
                    task['due_date_formatted'] = due_date.strftime('%Y-%m-%d %H:%M')
                    task['is_overdue'] = due_date < datetime.now()
                except:
                    task['due_date_formatted'] = task['due_date']
                    task['is_overdue'] = False
            else:
                task['due_date_formatted'] = 'No due date'
                task['is_overdue'] = False
            
            if task['created_at']:
                try:
                    created_at = datetime.fromisoformat(task['created_at'])
                    task['created_at_formatted'] = created_at.strftime('%Y-%m-%d %H:%M')
                except:
                    task['created_at_formatted'] = task['created_at']
        
        return tasks
    
    def update_task_status(self, task_id: int, status: str, 
                          session_id: str = None) -> Tuple[bool, str]:
        """
        Update a task's status.
        
        Args:
            task_id (int): Task ID
            status (str): New status
            session_id (str): User session ID
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        if status not in ['pending', 'in_progress', 'completed', 'cancelled']:
            return False, "Invalid status"
        
        user_id = None
        if session_id:
            user = self.get_session_user(session_id)
            if user:
                user_id = user['user_id']
            else:
                return False, "Invalid session"
        
        if self.db.update_task_status(task_id, status, user_id):
            return True, f"Task status updated to '{status}'"
        else:
            return False, "Failed to update task status (task not found or no permission)"
    
    def delete_task(self, task_id: int, session_id: str = None) -> Tuple[bool, str]:
        """
        Delete a task.
        
        Args:
            task_id (int): Task ID
            session_id (str): User session ID
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        user_id = None
        if session_id:
            user = self.get_session_user(session_id)
            if user:
                user_id = user['user_id']
            else:
                return False, "Invalid session"
        
        if self.db.delete_task(task_id, user_id):
            return True, "Task deleted successfully"
        else:
            return False, "Failed to delete task (task not found or no permission)"
    
    def get_task_statistics(self, session_id: str = None, 
                           show_all: bool = False) -> Dict:
        """
        Get task statistics.
        
        Args:
            session_id (str): User session ID
            show_all (bool): Show statistics for all users
            
        Returns:
            Dict: Statistics data
        """
        user_id = None
        if session_id and not show_all:
            user = self.get_session_user(session_id)
            if user:
                user_id = user['user_id']
        
        return self.db.get_task_statistics(user_id)
    
    def search_tasks(self, query: str, session_id: str = None) -> List[Dict]:
        """
        Search tasks by title or description.
        
        Args:
            query (str): Search query
            session_id (str): User session ID
            
        Returns:
            List[Dict]: Matching tasks
        """
        all_tasks = self.get_tasks(session_id=session_id)
        query_lower = query.lower()
        
        matching_tasks = []
        for task in all_tasks:
            if (query_lower in task['title'].lower() or 
                (task['description'] and query_lower in task['description'].lower())):
                matching_tasks.append(task)
        
        return matching_tasks
    
    def get_user_tasks_summary(self, session_id: str) -> Dict:
        """
        Get a summary of user's tasks.
        
        Args:
            session_id (str): User session ID
            
        Returns:
            Dict: Task summary
        """
        user = self.get_session_user(session_id)
        if not user:
            return {}
        
        tasks = self.get_tasks(session_id=session_id)
        
        summary = {
            'total_tasks': len(tasks),
            'pending': len([t for t in tasks if t['status'] == 'pending']),
            'in_progress': len([t for t in tasks if t['status'] == 'in_progress']),
            'completed': len([t for t in tasks if t['status'] == 'completed']),
            'overdue': len([t for t in tasks if t.get('is_overdue', False)]),
            'assigned_to_me': len([t for t in tasks if t['assigned_to'] == user['user_id']]),
            'created_by_me': len([t for t in tasks if t['created_by'] == user['user_id']])
        }
        
        return summary
    
    def cleanup_sessions(self, max_idle_hours: int = 24):
        """
        Clean up inactive sessions.
        
        Args:
            max_idle_hours (int): Maximum idle time in hours
        """
        with self._session_lock:
            current_time = datetime.now()
            sessions_to_remove = []
            
            for session_id, session_data in self._sessions.items():
                idle_time = current_time - session_data['last_activity']
                if idle_time.total_seconds() > (max_idle_hours * 3600):
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self._sessions[session_id]
    
    def get_active_sessions(self) -> List[Dict]:
        """Get information about active sessions."""
        with self._session_lock:
            sessions = []
            for session_id, session_data in self._sessions.items():
                sessions.append({
                    'session_id': session_id,
                    'username': session_data['username'],
                    'login_time': session_data['login_time'],
                    'last_activity': session_data['last_activity']
                })
            return sessions
