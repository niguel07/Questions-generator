"""
User Management Module - Phase 9
Handles user profiles, session history, and dataset management.
Simple username-based system for local use (no passwords).
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class UserManager:
    """
    Manages user profiles and generation history.
    Stores data in a simple JSON file for local use.
    """
    
    def __init__(self, users_file: str = "output/users.json"):
        """Initialize user manager with JSON file path."""
        self.users_file = Path(users_file)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create users file if it doesn't exist."""
        if not self.users_file.exists():
            self._save_users({})
    
    def _load_users(self) -> Dict[str, Any]:
        """Load users from JSON file."""
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_users(self, users: Dict[str, Any]):
        """Save users to JSON file."""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    
    def login(self, username: str) -> Dict[str, Any]:
        """
        Login or create a user.
        
        Args:
            username: Username to login with
            
        Returns:
            User data dictionary
        """
        if not username or len(username.strip()) == 0:
            return {
                "success": False,
                "error": "Username cannot be empty"
            }
        
        username = username.strip()
        users = self._load_users()
        
        # Create user if doesn't exist
        if username not in users:
            users[username] = {
                "created_at": datetime.now().isoformat(),
                "sessions": [],
                "total_questions": 0
            }
            self._save_users(users)
        
        return {
            "success": True,
            "username": username,
            "user_data": users[username]
        }
    
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data."""
        users = self._load_users()
        return users.get(username)
    
    def add_session(self, username: str, session_data: Dict[str, Any]):
        """
        Add a generation session to user history.
        
        Args:
            username: Username
            session_data: Session information (topics, questions, timestamp, etc.)
        """
        users = self._load_users()
        
        if username not in users:
            return
        
        # Add timestamp if not present
        if 'timestamp' not in session_data:
            session_data['timestamp'] = datetime.now().isoformat()
        
        users[username]['sessions'].append(session_data)
        users[username]['total_questions'] = users[username].get('total_questions', 0) + session_data.get('questions_generated', 0)
        
        self._save_users(users)
    
    def get_sessions(self, username: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's generation history.
        
        Args:
            username: Username
            limit: Maximum number of sessions to return
            
        Returns:
            List of session dictionaries
        """
        user = self.get_user(username)
        if not user:
            return []
        
        sessions = user.get('sessions', [])
        # Return most recent sessions first
        return sorted(sessions, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]
    
    def get_all_users(self) -> Dict[str, Any]:
        """Get all users."""
        return self._load_users()
    
    def get_stats(self, username: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            username: Username
            
        Returns:
            Statistics dictionary
        """
        user = self.get_user(username)
        if not user:
            return {}
        
        sessions = user.get('sessions', [])
        
        # Calculate stats
        total_sessions = len(sessions)
        total_questions = sum(s.get('questions_generated', 0) for s in sessions)
        topics_used = set()
        
        for session in sessions:
            topics = session.get('topics', [])
            if isinstance(topics, list):
                topics_used.update(topics)
            elif isinstance(topics, str):
                topics_used.add(topics)
        
        return {
            "username": username,
            "total_sessions": total_sessions,
            "total_questions_generated": total_questions,
            "unique_topics": len(topics_used),
            "topics_list": list(topics_used),
            "created_at": user.get('created_at'),
            "latest_session": sessions[0] if sessions else None
        }


if __name__ == "__main__":
    # Test user management
    manager = UserManager("output/users.json")
    
    # Test login
    result = manager.login("test_user")
    print(f"Login result: {result}")
    
    # Test adding session
    manager.add_session("test_user", {
        "topics": ["Cameroon", "AI"],
        "questions_generated": 1000,
        "avg_quality": 0.92
    })
    
    # Test getting sessions
    sessions = manager.get_sessions("test_user")
    print(f"Sessions: {sessions}")
    
    # Test stats
    stats = manager.get_stats("test_user")
    print(f"Stats: {stats}")

