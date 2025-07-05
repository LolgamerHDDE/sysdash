import os
import shutil
import time
from datetime import datetime, timedelta
from .test_logger import TestResultLogger
from .logging_config import LoggingConfig

class LogBackupManager:
    """Manages automatic backups of encrypted log files"""
    
    def __init__(self, backup_dir: str = "logs/backups"):
        self.backup_dir = backup_dir
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def create_backup(self, log_file: str = None) -> str:
        """Create a backup of the current log file"""
        if not log_file:
            log_file = LoggingConfig.get_log_file_path()
            
        if not os.path.exists(log_file):
            raise FileNotFoundError(f"Log file not found: {log_file}")
            
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"test_results_backup_{timestamp}.enc"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Copy the encrypted file
        shutil.copy2(log_file, backup_path)
        
        # Create metadata file
        metadata = {
            'original_file': log_file,
            'backup_created': datetime.now().isoformat(),
            'file_size': os.path.getsize(backup_path),
            'backup_type': 'automatic'
        }
        
        metadata_path = backup_path.replace('.enc', '_metadata.json')
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return backup_path
    
    def cleanup_old_backups(self, days_to_keep: int = 7):
        """Remove old backup files"""
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        removed_files = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('test_results_backup_'):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    removed_files.append(filename)
                    
                    # Remove corresponding metadata file
                    metadata_file = filename.replace('.enc', '_metadata.json')
                    metadata_path = os.path.join(self.backup_dir, metadata_file)
                    if os.path.exists(metadata_path):
                        os.remove(metadata_path)
                        
        return removed_files
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        
        for filename in os.listdir(self.backup_dir):
            if filename.startswith('test_results_backup_') and filename.endswith('.enc'):
                file_path = os.path.join(self.backup_dir, filename)
                metadata_path = file_path.replace('.enc', '_metadata.json')
                
                backup_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': os.path.getsize(file_path),
                    'created': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
                }
                
                # Load metadata if available
                if os.path.exists(metadata_path):
                    try:
                        import json
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        backup_info['metadata'] = metadata
                    except:
                        pass
                        
                backups.append(backup_info)
                
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def restore_backup(self, backup_filename: str, target_file: str = None) -> bool:
        """Restore a backup file"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
        if not target_file:
            target_file = LoggingConfig.get_log_file_path()
            
        # Create backup of current file before restoring
        if os.path.exists(target_file):
            current_backup = target_file + f".backup_{int(time.time())}"
            shutil.copy2(target_file, current_backup)
            
        # Restore the backup
        shutil.copy2(backup_path, target_file)
        
        # Verify the restored file
        try:
            logger = TestResultLogger()
            integrity = logger.verify_integrity()
            return integrity['status'] == 'valid'
        except:
            return False