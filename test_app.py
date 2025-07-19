#!/usr/bin/env python3
"""
Test script for the Multi-User To-Do List Application.

This script performs basic functionality tests to ensure the application
is working correctly.
"""

import os
import sys
import sqlite3
import time
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import with absolute imports
from src.database import DatabaseManager
from src.task_manager import TaskManager


def test_database_operations():
    """Test basic database operations."""
    print("Testing database operations...")
    
    # Create a test database
    test_db = "test_todo.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    try:
        # Initialize database
        db = DatabaseManager(test_db)
        print("✓ Database initialization successful")
        
        # Test user creation
        success = db.create_user("testuser", "password123", "test@example.com")
        assert success, "User creation failed"
        print("✓ User creation successful")
        
        # Test user authentication
        user = db.authenticate_user("testuser", "password123")
        assert user is not None, "User authentication failed"
        assert user['username'] == "testuser", "Username mismatch"
        print("✓ User authentication successful")
        
        # Test category creation
        success = db.create_category("Test Category", "A test category", "#FF5722", user['id'])
        assert success, "Category creation failed"
        print("✓ Category creation successful")
        
        # Test task creation
        categories = db.get_categories()
        test_category = next((c for c in categories if c['name'] == "Test Category"), None)
        assert test_category is not None, "Test category not found"
        
        task_id = db.create_task(
            title="Test Task",
            description="A test task",
            category_id=test_category['id'],
            assigned_to=user['id'],
            created_by=user['id'],
            priority="high"
        )
        assert task_id is not None, "Task creation failed"
        print("✓ Task creation successful")
        
        # Test task retrieval
        tasks = db.get_tasks(user_id=user['id'])
        assert len(tasks) > 0, "No tasks retrieved"
        assert tasks[0]['title'] == "Test Task", "Task title mismatch"
        print("✓ Task retrieval successful")
        
        # Test task status update
        success = db.update_task_status(task_id, "completed", user['id'])
        assert success, "Task status update failed"
        print("✓ Task status update successful")
        
        # Test statistics
        stats = db.get_task_statistics(user['id'])
        assert stats['total_tasks'] > 0, "Statistics retrieval failed"
        print("✓ Statistics retrieval successful")
        
        # Cleanup
        db.close()
        
        # Wait a bit for file handles to be released
        time.sleep(0.1)
        
        try:
            os.remove(test_db)
            print("✓ Database cleanup successful")
        except OSError:
            print("⚠ Database cleanup: file in use, will be cleaned up later")
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        if os.path.exists(test_db):
            os.remove(test_db)
        raise


def test_task_manager():
    """Test task manager operations."""
    print("\nTesting task manager operations...")
    
    test_db = "test_task_manager.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    try:
        # Initialize task manager
        db = DatabaseManager(test_db)
        task_manager = TaskManager(db)
        print("✓ Task manager initialization successful")
        
        # Test user registration
        success, message = task_manager.create_user("tmuser", "password123", "tm@example.com")
        assert success, f"User registration failed: {message}"
        print("✓ User registration successful")
        
        # Test login
        success, message, user = task_manager.login("tmuser", "password123")
        assert success, f"Login failed: {message}"
        assert user is not None, "User info not returned"
        session_id = user['session_id']
        print("✓ Login successful")
        
        # Test category creation
        success, message = task_manager.create_category("TM Category", "Task manager test category", session_id=session_id)
        assert success, f"Category creation failed: {message}"
        print("✓ Category creation via task manager successful")
        
        # Test task creation
        success, message = task_manager.create_task(
            title="Task Manager Test Task",
            description="Testing task creation via task manager",
            category_name="TM Category",
            priority="medium",
            session_id=session_id
        )
        assert success, f"Task creation failed: {message}"
        print("✓ Task creation via task manager successful")
        
        # Test task retrieval
        tasks = task_manager.get_tasks(session_id=session_id)
        assert len(tasks) > 0, "No tasks retrieved via task manager"
        test_task = tasks[0]
        print("✓ Task retrieval via task manager successful")
        
        # Test task status update
        success, message = task_manager.update_task_status(test_task['id'], "in_progress", session_id)
        assert success, f"Task status update failed: {message}"
        print("✓ Task status update via task manager successful")
        
        # Test search
        search_results = task_manager.search_tasks("Task Manager", session_id)
        assert len(search_results) > 0, "Search returned no results"
        print("✓ Task search successful")
        
        # Test statistics
        stats = task_manager.get_task_statistics(session_id)
        assert stats['total_tasks'] > 0, "Statistics via task manager failed"
        print("✓ Statistics via task manager successful")
        
        # Test logout
        success = task_manager.logout(session_id)
        assert success, "Logout failed"
        print("✓ Logout successful")
        
        # Cleanup
        db.close()
        os.remove(test_db)
        print("✓ Task manager cleanup successful")
        
    except Exception as e:
        print(f"✗ Task manager test failed: {e}")
        if os.path.exists(test_db):
            os.remove(test_db)
        raise


def test_concurrent_access():
    """Test concurrent access capabilities."""
    print("\nTesting concurrent access...")
    
    import threading
    import time
    
    test_db = "test_concurrent.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    try:
        db = DatabaseManager(test_db)
        task_manager = TaskManager(db)
        
        # Create test users
        for i in range(3):
            success, _ = task_manager.create_user(f"user{i}", "password123")
            assert success, f"Failed to create user{i}"
        
        print("✓ Multiple users created")
        
        # Test concurrent logins
        sessions = []
        
        def login_user(user_id):
            success, _, user = task_manager.login(f"user{user_id}", "password123")
            if success:
                sessions.append(user['session_id'])
        
        threads = []
        for i in range(3):
            thread = threading.Thread(target=login_user, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(sessions) == 3, "Not all users logged in concurrently"
        print("✓ Concurrent login successful")
        
        # Test concurrent task creation
        created_tasks = []
        
        def create_task(session_id, task_num):
            success, message = task_manager.create_task(
                title=f"Concurrent Task {task_num}",
                description=f"Task created concurrently by session {session_id}",
                session_id=session_id
            )
            if success:
                created_tasks.append(task_num)
        
        threads = []
        for i, session_id in enumerate(sessions):
            thread = threading.Thread(target=create_task, args=(session_id, i))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(created_tasks) == 3, "Not all tasks created concurrently"
        print("✓ Concurrent task creation successful")
        
        # Test concurrent task updates
        all_tasks = task_manager.get_tasks(show_all=True)
        
        def update_task_status(session_id, task_id):
            task_manager.update_task_status(task_id, "completed", session_id)
        
        threads = []
        for i, task in enumerate(all_tasks[:3]):
            thread = threading.Thread(target=update_task_status, args=(sessions[i], task['id']))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print("✓ Concurrent task updates successful")
        
        # Cleanup
        for session_id in sessions:
            task_manager.logout(session_id)
        
        db.close()
        
        # Wait a bit for file handles to be released
        time.sleep(0.1)
        
        try:
            os.remove(test_db)
            print("✓ Concurrent access cleanup successful")
        except OSError:
            print("⚠ Concurrent access cleanup: database file in use, will be cleaned up later")
        
    except Exception as e:
        print(f"✗ Concurrent access test failed: {e}")
        # Don't try to remove if there's an error, it might be in use
        try:
            if os.path.exists(test_db):
                os.remove(test_db)
        except OSError:
            pass  # Ignore cleanup errors
        raise


def main():
    """Run all tests."""
    print("Multi-User To-Do List Application - Test Suite")
    print("=" * 50)
    
    try:
        test_database_operations()
        test_task_manager()
        test_concurrent_access()
        
        print("\n" + "=" * 50)
        print("✓ All tests passed successfully!")
        print("The application is ready to use.")
        
    except Exception as e:
        print("\n" + "=" * 50)
        print(f"✗ Tests failed: {e}")
        print("Please check the error messages above and fix any issues.")
        sys.exit(1)


if __name__ == "__main__":
    main()
