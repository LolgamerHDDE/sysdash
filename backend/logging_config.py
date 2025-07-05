import os
from typing import Optional

class LoggingConfig:
    """Configuration for the secure logging system"""
    
    # Default settings
    DEFAULT_LOG_FILE = "logs/test_results.enc"
    DEFAULT_MAX_ENTRIES = 1000
    DEFAULT_CLEANUP_DAYS = 30
    
    # Security settings
    PBKDF2_ITERATIONS = 100000
    SALT = b'sysdash_salt_2025'
    
    # File settings
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 24
    
    @classmethod
    def get_log_file_path(cls, custom_path: Optional[str] = None) -> str:
        """Get the log file path"""
        if custom_path:
            return custom_path
        
        # Check environment variable
        env_path = os.getenv('SYSDASH_LOG_FILE')
        if env_path:
            return env_path
            
        return cls.DEFAULT_LOG_FILE
    
    @classmethod
    def get_password(cls) -> Optional[str]:
        """Get password from environment or return None for auto-generation"""
        return os.getenv('SYSDASH_LOG_PASSWORD')
    
    @classmethod
    def get_max_entries(cls) -> int:
        """Get maximum number of log entries to keep"""
        try:
            return int(os.getenv('SYSDASH_MAX_LOG_ENTRIES', cls.DEFAULT_MAX_ENTRIES))
        except ValueError:
            return cls.DEFAULT_MAX_ENTRIES
    
    @classmethod
    def should_backup(cls) -> bool:
        """Check if automatic backups are enabled"""
        return os.getenv('SYSDASH_BACKUP_ENABLED', 'true').lower() == 'true'
    
    @classmethod
    def get_backup_interval(cls) -> int:
        """Get backup interval in hours"""
        try:
            return int(os.getenv('SYSDASH_BACKUP_INTERVAL_HOURS', cls.BACKUP_INTERVAL_HOURS))
        except ValueError:
            return cls.BACKUP_INTERVAL_HOURS