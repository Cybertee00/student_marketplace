"""
Logging Service
Optional logging to Supabase logs table (disabled by default)
"""

from supabase_config import supabase
import os
from typing import Optional, Dict, Any

# Enable/disable logging via environment variable
ENABLE_LOGGING = os.getenv("ENABLE_LOGGING", "false").lower() == "true"

class LoggingService:
    """Service for logging to Supabase logs table"""
    
    def __init__(self):
        self.enabled = ENABLE_LOGGING
        self.client = supabase
    
    def log(
        self, 
        level: str, 
        message: str, 
        metadata: Optional[Dict[str, Any]] = None, 
        user_id: Optional[str] = None
    ):
        """
        Log to Supabase logs table (only if enabled)
        
        Args:
            level: Log level (info, warning, error, debug)
            message: Log message
            metadata: Optional metadata dictionary
            user_id: Optional user ID
        """
        if not self.enabled:
            return
        
        try:
            log_entry = {
                "level": level,
                "message": message,
                "metadata": metadata or {},
                "user_id": user_id
            }
            self.client.table("logs").insert(log_entry).execute()
        except Exception as e:
            # Fail silently - don't break app if logging fails
            print(f"Logging error: {e}")
    
    def info(self, message: str, metadata: Optional[Dict] = None, user_id: Optional[str] = None):
        """Log info message"""
        self.log("info", message, metadata, user_id)
    
    def warning(self, message: str, metadata: Optional[Dict] = None, user_id: Optional[str] = None):
        """Log warning message"""
        self.log("warning", message, metadata, user_id)
    
    def error(self, message: str, metadata: Optional[Dict] = None, user_id: Optional[str] = None):
        """Log error message"""
        self.log("error", message, metadata, user_id)
    
    def debug(self, message: str, metadata: Optional[Dict] = None, user_id: Optional[str] = None):
        """Log debug message"""
        self.log("debug", message, metadata, user_id)
    
    def enable(self):
        """Enable logging"""
        self.enabled = True
        print("✅ Logging enabled")
    
    def disable(self):
        """Disable logging"""
        self.enabled = False
        print("✅ Logging disabled")

# Create global instance
logging_service = LoggingService()

