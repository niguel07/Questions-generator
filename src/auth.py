"""
Authentication Module with Supabase Integration
Handles user signup, login, and session management using local Supabase.
"""

import os
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json
from dotenv import load_dotenv

load_dotenv()

# For local development without Supabase, we'll use a secure JSON-based system
# In production, replace this with actual Supabase integration

class AuthManager:
    """
    Authentication manager with signup/login functionality.
    Uses secure password hashing and session tokens.
    """
    
    def __init__(self, db_file: str = "output/auth_users.json"):
        """Initialize authentication manager."""
        self.db_file = Path(db_file)
        self.db_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists()
        self.sessions = {}  # In-memory session storage
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist."""
        if not self.db_file.exists():
            self._save_db({"users": {}})
    
    def _load_db(self) -> Dict[str, Any]:
        """Load user database."""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"users": {}}
    
    def _save_db(self, data: Dict[str, Any]):
        """Save user database."""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt using SHA-256."""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2-like approach with multiple iterations
        pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        for _ in range(10000):  # 10000 iterations
            pwd_hash = hashlib.sha256(f"{pwd_hash}{salt}".encode()).hexdigest()
        
        return pwd_hash, salt
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def signup(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str = None
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: Unique username
            email: User email
            password: Password (will be hashed)
            full_name: Optional full name
            
        Returns:
            Response dictionary with success status and user data
        """
        # Validate input
        if not username or len(username.strip()) < 3:
            return {
                "success": False,
                "error": "Username must be at least 3 characters"
            }
        
        if not email or '@' not in email:
            return {
                "success": False,
                "error": "Valid email is required"
            }
        
        if not password or len(password) < 6:
            return {
                "success": False,
                "error": "Password must be at least 6 characters"
            }
        
        # Load database
        db = self._load_db()
        
        # Check if username or email already exists
        username_lower = username.strip().lower()
        email_lower = email.strip().lower()
        
        for user_data in db["users"].values():
            if user_data["username"].lower() == username_lower:
                return {
                    "success": False,
                    "error": "Username already exists"
                }
            if user_data["email"].lower() == email_lower:
                return {
                    "success": False,
                    "error": "Email already registered"
                }
        
        # Hash password
        pwd_hash, salt = self._hash_password(password)
        
        # Create user
        user_id = secrets.token_hex(16)
        user_data = {
            "user_id": user_id,
            "username": username.strip(),
            "email": email.strip(),
            "full_name": full_name or username.strip(),
            "password_hash": pwd_hash,
            "salt": salt,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "sessions": [],
            "total_questions": 0
        }
        
        db["users"][user_id] = user_data
        self._save_db(db)
        
        # Generate session token
        session_token = self._generate_session_token()
        self.sessions[session_token] = {
            "user_id": user_id,
            "username": username.strip(),
            "expires_at": datetime.now() + timedelta(days=7)
        }
        
        return {
            "success": True,
            "message": "Account created successfully",
            "user": {
                "user_id": user_id,
                "username": username.strip(),
                "email": email.strip(),
                "full_name": user_data["full_name"]
            },
            "session_token": session_token
        }
    
    def login(self, username_or_email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate a user.
        
        Args:
            username_or_email: Username or email
            password: Password
            
        Returns:
            Response dictionary with success status and session token
        """
        if not username_or_email or not password:
            return {
                "success": False,
                "error": "Username/email and password are required"
            }
        
        # Load database
        db = self._load_db()
        
        # Find user by username or email
        user_data = None
        user_id = None
        identifier_lower = username_or_email.strip().lower()
        
        for uid, data in db["users"].items():
            if (data["username"].lower() == identifier_lower or 
                data["email"].lower() == identifier_lower):
                user_data = data
                user_id = uid
                break
        
        if not user_data:
            return {
                "success": False,
                "error": "Invalid username/email or password"
            }
        
        # Verify password
        pwd_hash, _ = self._hash_password(password, user_data["salt"])
        
        if pwd_hash != user_data["password_hash"]:
            return {
                "success": False,
                "error": "Invalid username/email or password"
            }
        
        # Update last login
        user_data["last_login"] = datetime.now().isoformat()
        db["users"][user_id] = user_data
        self._save_db(db)
        
        # Generate session token
        session_token = self._generate_session_token()
        self.sessions[session_token] = {
            "user_id": user_id,
            "username": user_data["username"],
            "expires_at": datetime.now() + timedelta(days=7)
        }
        
        return {
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user_id,
                "username": user_data["username"],
                "email": user_data["email"],
                "full_name": user_data["full_name"]
            },
            "session_token": session_token
        }
    
    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """
        Verify a session token.
        
        Args:
            session_token: Session token to verify
            
        Returns:
            Response with user data if valid
        """
        if not session_token or session_token not in self.sessions:
            return {
                "success": False,
                "error": "Invalid session"
            }
        
        session = self.sessions[session_token]
        
        # Check if expired
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_token]
            return {
                "success": False,
                "error": "Session expired"
            }
        
        return {
            "success": True,
            "user": {
                "user_id": session["user_id"],
                "username": session["username"]
            }
        }
    
    def logout(self, session_token: str) -> Dict[str, Any]:
        """
        Logout user by removing session.
        
        Args:
            session_token: Session token to invalidate
            
        Returns:
            Response dictionary
        """
        if session_token in self.sessions:
            del self.sessions[session_token]
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data by user ID."""
        db = self._load_db()
        return db["users"].get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user data by username."""
        db = self._load_db()
        username_lower = username.lower()
        
        for user_data in db["users"].values():
            if user_data["username"].lower() == username_lower:
                return user_data
        
        return None


if __name__ == "__main__":
    # Test authentication
    auth = AuthManager("output/test_auth.json")
    
    # Test signup
    result = auth.signup("testuser", "test@example.com", "password123", "Test User")
    print(f"Signup: {result}")
    
    if result["success"]:
        token = result["session_token"]
        
        # Test session verification
        verify = auth.verify_session(token)
        print(f"Verify: {verify}")
        
        # Test login
        login = auth.login("testuser", "password123")
        print(f"Login: {login}")
        
        # Test logout
        logout = auth.logout(token)
        print(f"Logout: {logout}")
    
    # Clean up test file
    Path("output/test_auth.json").unlink(missing_ok=True)

