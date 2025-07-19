# Multi-User To-Do List Application

A comprehensive task management application with both command-line and graphical user interfaces, supporting multiple users, task categorization, and concurrent access.

## Features

### Core Features
- **Multi-user Support**: Multiple users can register and login with secure authentication
- **Task Management**: Create, edit, delete, and organize tasks
- **Task Categorization**: Organize tasks with customizable categories
- **Task Assignment**: Assign tasks to specific users
- **Status Tracking**: Track task progress (pending, in_progress, completed, cancelled)
- **Priority Levels**: Set task priorities (low, medium, high, urgent)
- **Due Dates**: Set and track task deadlines
- **Concurrent Access**: Thread-safe operations for multiple simultaneous users

### Interface Options
- **Command-Line Interface (CLI)**: Full-featured terminal interface with colored output
- **Graphical User Interface (GUI)**: User-friendly Tkinter-based interface

### Database Features
- **SQLite Storage**: Persistent data storage with SQLite database
- **Data Integrity**: Foreign key constraints and data validation
- **Thread Safety**: Concurrent access support with proper locking

## Installation

### Prerequisites
- Python 3.7 or higher
- Built-in Python modules (no external dependencies required for basic functionality)

### Setup
1. Clone or download the application files
2. Navigate to the application directory
3. Install optional dependencies (recommended):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Application

#### GUI Interface (Default)
```bash
python main.py
```
or
```bash
python main.py --interface gui
```

#### Command-Line Interface
```bash
python main.py --interface cli
```

#### Custom Database Location
```bash
python main.py --database /path/to/your/database.db
```

### First Time Setup

1. **Register a User**: Create your first user account
2. **Login**: Authenticate with your credentials
3. **Create Categories**: Set up task categories (optional, default categories are provided)
4. **Start Managing Tasks**: Begin creating and organizing your tasks

## GUI Interface Guide

### Main Window
- **User Panel**: Shows current login status
- **Filters**: Filter tasks by status, category, or search
- **Task List**: Displays tasks in a sortable table
- **Action Buttons**: Quick access to common operations

### Key Operations
- **Login/Register**: Use the File menu or toolbar buttons
- **New Task**: Click "New Task" button or use Task menu
- **Edit Task**: Double-click a task or right-click for context menu
- **Update Status**: Right-click task for status options
- **Search**: Use the search box to find specific tasks
- **View Options**: Use View menu for different task views

## CLI Interface Guide

### Available Commands

#### Authentication
- `register` - Register a new user account
- `login` - Login to your account
- `logout` - Logout from current session

#### Task Management
- `add` - Add a new task (interactive)
- `list [status] [category]` - List tasks with optional filters
- `my` - List your tasks
- `all` - List all tasks (admin view)
- `pending` - List pending tasks
- `completed` - List completed tasks
- `update <id> <status>` - Update task status
- `complete <id>` - Mark task as completed
- `delete <id>` - Delete a task
- `search <query>` - Search tasks by title/description

#### Information
- `users` - List all registered users
- `categories` - List all task categories
- `addcat <name>` - Add a new category
- `stats` - Show task statistics
- `summary` - Show your task summary

#### Utility
- `help` - Show available commands
- `clear` - Clear screen
- `quit/exit/q` - Exit application

### Example CLI Session
```
> register
Username (min 3 characters): john_doe
Email (optional): john@example.com
Password (min 6 characters): ******
Confirm password: ******
✓ User 'john_doe' created successfully

> login
Username: john_doe
Password: ******
✓ Welcome back, john_doe!

[john_doe] > add
Task title: Complete project documentation
Description (optional): Write comprehensive docs for the project
Category (optional): Work
Assign to user (optional): 
Priority (low/medium/high/urgent): high
Due date (YYYY-MM-DD HH:MM, optional): 2025-07-25 17:00
✓ Task 'Complete project documentation' created successfully (ID: 1)

[john_doe] > list
Tasks (Filtered: status=None, category=None)
╔════╤════════════════════════════════════╤══════════╤═════════════╤══════════╤═══════════╤═══════════════════╗
║ ID │ Title                              │ Category │ Assigned To │ Priority │ Status    │ Due Date          ║
╠════╪════════════════════════════════════╪══════════╪═════════════╪══════════╪═══════════╪═══════════════════╣
║  1 │ 🔄 Complete project documentation │ Work     │ Unassigned  │ 🟠 high  │ pending   │ 2025-07-25 17:00  ║
╚════╧════════════════════════════════════╧══════════╧═════════════╧══════════╧═══════════╧═══════════════════╝

Showing 1 task(s)
```

## Database Schema

The application uses SQLite with the following main tables:

### Users Table
- User accounts with secure password hashing
- Login tracking and session management

### Categories Table
- Task categorization system
- User-defined and system categories

### Tasks Table
- Main task storage with all attributes
- Foreign key relationships to users and categories
- Status and priority tracking

### Task Assignments Table
- Many-to-many relationship for task assignments
- Support for multiple users per task

## Concurrency Support

The application is designed for concurrent access:

- **Thread-safe Database Operations**: Using connection pooling and locking
- **Session Management**: Unique session tokens for each user login
- **Real-time Updates**: Auto-refresh capabilities in GUI
- **Data Integrity**: Proper transaction handling and rollback

## Configuration

### Database Configuration
- Default database file: `todo_app.db`
- Custom location via `--database` parameter
- Automatic schema creation on first run

### Session Configuration
- Session timeout: 24 hours (configurable)
- Auto-refresh interval: 30 seconds (GUI)
- Concurrent session support per user

## Troubleshooting

### Common Issues

1. **Database Locked Error**
   - Ensure no other instances are running
   - Check file permissions
   - Restart the application

2. **Import Errors**
   - Verify Python version (3.7+)
   - Install optional dependencies if using enhanced features

3. **Permission Errors**
   - Check write permissions in application directory
   - Run with appropriate user privileges

4. **GUI Not Displaying**
   - Ensure tkinter is installed (usually included with Python)
   - Try CLI interface as fallback

### Getting Help

For issues and questions:
1. Check this README for common solutions
2. Review the help command in CLI: `help`
3. Check the About dialog in GUI for version information

## Technical Details

### Architecture
- **Model**: SQLite database with proper schema design
- **Business Logic**: TaskManager class with session management
- **View**: Separate CLI and GUI interfaces
- **Threading**: Safe concurrent access with proper locking

### Dependencies
- **Built-in**: sqlite3, tkinter, threading, datetime, argparse, hashlib, getpass
- **Optional**: colorama (CLI colors), tabulate (CLI tables)

### File Structure
```
To-Do List Application/
├── main.py                 # Application entry point
├── requirements.txt        # Optional dependencies
├── README.md              # This file
└── src/
    ├── __init__.py        # Package initialization
    ├── database.py        # Database management
    ├── task_manager.py    # Business logic
    ├── cli.py            # Command-line interface
    └── gui.py            # Graphical interface
```

---

**Version**: 1.0.0  
**Date**: July 2025  
**Author**: Advanced Programming Languages Course
