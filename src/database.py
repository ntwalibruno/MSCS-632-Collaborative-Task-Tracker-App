"""
Database management module for the to-do list application.

This module handles SQLite database operations including user management,
task storage, and provides thread-safe database access.
"""

import sqlite3
import threading
import hashlib
import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    """Manages SQLite database operations with thread safety."""
    
    def __init__(self, db_path: str = "todo_app.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._local = threading.local()  # Thread-local storage for connections
        
        # Initialize database schema
        self._init_database()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self._local.connection.row_factory = sqlite3.Row  # Enable dict-like access
        return self._local.connection
    
    def _init_database(self):
        """Initialize the database schema."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    color TEXT DEFAULT '#0078D4',
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            ''')
            
            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category_id INTEGER,
                    assigned_to INTEGER,
                    created_by INTEGER,
                    status TEXT DEFAULT 'pending',
                    priority TEXT DEFAULT 'medium',
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id),
                    FOREIGN KEY (assigned_to) REFERENCES users (id),
                    FOREIGN KEY (created_by) REFERENCES users (id),
                    CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
                    CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
                )
            ''')
            
            # Create task_assignments table for multiple user assignments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS task_assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    user_id INTEGER,
                    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    assigned_by INTEGER,
                    FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (assigned_by) REFERENCES users (id),
                    UNIQUE (task_id, user_id)
                )
            ''')
            
            # Create default categories
            default_categories = [
                ('Work', 'Work-related tasks', '#0078D4'),
                ('Personal', 'Personal tasks', '#107C10'),
                ('Shopping', 'Shopping lists', '#FF8C00'),
                ('Health', 'Health and fitness', '#E74856'),
                ('Education', 'Learning and study', '#5C2D91')
            ]
            
            for name, desc, color in default_categories:
                cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, description, color)
                    VALUES (?, ?, ?)
                ''', (name, desc, color))
            
            conn.commit()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username: str, password: str, email: str = None) -> bool:
        """
        Create a new user.
        
        Args:
            username (str): Username
            password (str): Plain text password
            email (str): Email address (optional)
            
        Returns:
            bool: True if user created successfully, False otherwise
        """
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                password_hash = self._hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email)
                    VALUES (?, ?, ?)
                ''', (username, password_hash, email))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError:
                return False  # Username already exists
            except Exception:
                return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user.
        
        Args:
            username (str): Username
            password (str): Plain text password
            
        Returns:
            Dict: User information if authentication successful, None otherwise
        """
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                password_hash = self._hash_password(password)
                cursor.execute('''
                    SELECT id, username, email, created_at
                    FROM users
                    WHERE username = ? AND password_hash = ?
                ''', (username, password_hash))
                
                user = cursor.fetchone()
                if user:
                    # Update last login
                    cursor.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (user['id'],))
                    conn.commit()
                    
                    return dict(user)
                return None
                
            except Exception:
                return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user information by ID."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, created_at, last_login
                    FROM users WHERE id = ?
                ''', (user_id,))
                
                user = cursor.fetchone()
                return dict(user) if user else None
                
            except Exception:
                return None
    
    def get_all_users(self) -> List[Dict]:
        """Get all users."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT id, username, email, created_at, last_login
                    FROM users ORDER BY username
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception:
                return []
    
    def create_category(self, name: str, description: str = None, 
                       color: str = '#0078D4', created_by: int = None) -> bool:
        """Create a new category."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO categories (name, description, color, created_by)
                    VALUES (?, ?, ?, ?)
                ''', (name, description, color, created_by))
                
                conn.commit()
                return True
                
            except sqlite3.IntegrityError:
                return False  # Category already exists
            except Exception:
                return False
    
    def get_categories(self) -> List[Dict]:
        """Get all categories."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT c.*, u.username as created_by_username
                    FROM categories c
                    LEFT JOIN users u ON c.created_by = u.id
                    ORDER BY c.name
                ''')
                
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception:
                return []
    
    def create_task(self, title: str, description: str = None, category_id: int = None,
                   assigned_to: int = None, created_by: int = None, priority: str = 'medium',
                   due_date: str = None) -> Optional[int]:
        """
        Create a new task.
        
        Returns:
            int: Task ID if created successfully, None otherwise
        """
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO tasks (title, description, category_id, assigned_to,
                                     created_by, priority, due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (title, description, category_id, assigned_to, created_by,
                      priority, due_date))
                
                task_id = cursor.lastrowid
                conn.commit()
                return task_id
                
            except Exception:
                return None
    
    def get_tasks(self, user_id: int = None, status: str = None, 
                 category_id: int = None) -> List[Dict]:
        """
        Get tasks with optional filtering.
        
        Args:
            user_id (int): Filter by assigned user
            status (str): Filter by status
            category_id (int): Filter by category
            
        Returns:
            List[Dict]: List of tasks
        """
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                query = '''
                    SELECT t.*, 
                           c.name as category_name, c.color as category_color,
                           u1.username as assigned_to_username,
                           u2.username as created_by_username
                    FROM tasks t
                    LEFT JOIN categories c ON t.category_id = c.id
                    LEFT JOIN users u1 ON t.assigned_to = u1.id
                    LEFT JOIN users u2 ON t.created_by = u2.id
                '''
                
                conditions = []
                params = []
                
                if user_id:
                    conditions.append('(t.assigned_to = ? OR t.created_by = ?)')
                    params.extend([user_id, user_id])
                
                if status:
                    conditions.append('t.status = ?')
                    params.append(status)
                
                if category_id:
                    conditions.append('t.category_id = ?')
                    params.append(category_id)
                
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                
                query += ' ORDER BY t.created_at DESC'
                
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
                
            except Exception:
                return []
    
    def update_task_status(self, task_id: int, status: str, user_id: int = None) -> bool:
        """Update task status."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Check if user has permission to update this task
                if user_id:
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM tasks
                        WHERE id = ? AND (assigned_to = ? OR created_by = ?)
                    ''', (task_id, user_id, user_id))
                    
                    if cursor.fetchone()['count'] == 0:
                        return False  # No permission
                
                completed_at = None
                if status == 'completed':
                    completed_at = datetime.datetime.now().isoformat()
                
                cursor.execute('''
                    UPDATE tasks 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP, completed_at = ?
                    WHERE id = ?
                ''', (status, completed_at, task_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception:
                return False
    
    def delete_task(self, task_id: int, user_id: int = None) -> bool:
        """Delete a task."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Check if user has permission to delete this task
                if user_id:
                    cursor.execute('''
                        SELECT COUNT(*) as count FROM tasks
                        WHERE id = ? AND (assigned_to = ? OR created_by = ?)
                    ''', (task_id, user_id, user_id))
                    
                    if cursor.fetchone()['count'] == 0:
                        return False  # No permission
                
                cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
                conn.commit()
                return cursor.rowcount > 0
                
            except Exception:
                return False
    
    def get_task_statistics(self, user_id: int = None) -> Dict:
        """Get task statistics."""
        with self._lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                
                base_query = '''
                    SELECT status, COUNT(*) as count
                    FROM tasks
                '''
                
                if user_id:
                    base_query += ' WHERE assigned_to = ? OR created_by = ?'
                    params = [user_id, user_id]
                else:
                    params = []
                
                base_query += ' GROUP BY status'
                
                cursor.execute(base_query, params)
                status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
                
                # Get category statistics
                category_query = '''
                    SELECT c.name, COUNT(t.id) as count
                    FROM categories c
                    LEFT JOIN tasks t ON c.id = t.category_id
                '''
                
                if user_id:
                    category_query += ' AND (t.assigned_to = ? OR t.created_by = ?)'
                    category_params = [user_id, user_id]
                else:
                    category_params = []
                
                category_query += ' GROUP BY c.id, c.name ORDER BY count DESC'
                
                cursor.execute(category_query, category_params)
                category_counts = {row['name']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'status_counts': status_counts,
                    'category_counts': category_counts,
                    'total_tasks': sum(status_counts.values())
                }
                
            except Exception:
                return {'status_counts': {}, 'category_counts': {}, 'total_tasks': 0}
    
    def close(self):
        """Close database connections."""
        with self._lock:
            if hasattr(self._local, 'connection'):
                self._local.connection.close()
