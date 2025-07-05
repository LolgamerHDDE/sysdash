import os
from .test_logger import TestResultLogger

def initialize_logging():
    """Initialize the logging system"""
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    
    # Initialize logger to create encrypted file
    logger = TestResultLogger()
    
    # Test the logging system
    test_results = {
        'initialization': True,
        'timestamp': '2025-01-01T00:00:00',
        'version': '1.0.0'
    }
    
    log_id = logger.secure_logger.log_test_result(
        'system_initialization',
        test_results,
        {'event': 'logging_system_initialized'}
    )
    
    print(f"Logging system initialized successfully. Log ID: {log_id}")
    
        # Verify integrity
    integrity_check = logger.verify_integrity()
    print(f"Log file integrity check: {integrity_check['status']}")
    
    return logger

def cleanup_old_logs(days_to_keep: int = 30):
    """Clean up old log entries (keep only recent ones)"""
    try:
        from datetime import datetime, timedelta
        logger = TestResultLogger()
        
        # Get all test results
        all_results = logger.secure_logger.get_test_results()
        
        # Filter results to keep only recent ones
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        recent_results = []
        
        for result in all_results:
            try:
                result_date = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
                if result_date >= cutoff_date:
                    recent_results.append(result)
            except:
                # Keep results with invalid timestamps
                recent_results.append(result)
        
        # Save filtered results
        logger.secure_logger._save_encrypted_data(recent_results)
        
        removed_count = len(all_results) - len(recent_results)
        print(f"Cleanup completed. Removed {removed_count} old entries, kept {len(recent_results)} recent entries.")
        
        return {
            'removed_entries': removed_count,
            'kept_entries': len(recent_results),
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    initialize_logging()
