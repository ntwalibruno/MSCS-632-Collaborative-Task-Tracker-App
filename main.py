"""
To-Do List Application with Multiple User Support

This application provides both command-line and GUI interfaces for managing tasks
with support for multiple users, categorization, and concurrent access.

Features:
- Multi-user support with authentication
- Task categorization and status tracking
- Command-line and GUI interfaces
- SQLite database for data persistence
- Concurrent access support with thread safety
- Task assignment and user-specific views

Course: Advanced Programming Languages Course
Date: July 2025
"""

from src.database import DatabaseManager
from src.task_manager import TaskManager
from src.cli import CLIInterface
from src.gui import GUIInterface
import argparse
import sys


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Multi-User To-Do List Application')
    parser.add_argument('--interface', '-i', choices=['cli', 'gui'], default='gui',
                        help='Choose interface type (default: gui)')
    parser.add_argument('--database', '-d', default='todo_app.db',
                        help='Database file path (default: todo_app.db)')
    
    args = parser.parse_args()
    
    try:
        # Initialize database and task manager
        db_manager = DatabaseManager(args.database)
        task_manager = TaskManager(db_manager)
        
        # Launch appropriate interface
        if args.interface == 'cli':
            cli = CLIInterface(task_manager)
            cli.run()
        else:
            gui = GUIInterface(task_manager)
            gui.run()
            
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
