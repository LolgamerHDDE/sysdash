from .crypto_utils import SecureLogger
from datetime import datetime
import json

class TestResultLogger:
    def __init__(self, log_file: str = "logs/test_results.enc", password: str = None):
        self.secure_logger = SecureLogger(password, log_file)
        
    def log_benchmark_result(self, benchmark_type: str, results: dict, user_agent: str = None):
        """Log benchmark test results"""
        metadata = {
            'user_agent': user_agent,
            'test_duration': results.get('duration', 0),
            'test_version': '1.0.0'
        }
        
        return self.secure_logger.log_test_result(
            test_type=f"benchmark_{benchmark_type}",
            results=results,
            metadata=metadata
        )
    
    def log_speedtest_result(self, results: dict, server_info: dict = None):
        """Log network speed test results"""
        metadata = {
            'server_info': server_info,
            'test_version': '1.0.0'
        }
        
        return self.secure_logger.log_test_result(
            test_type="speedtest",
            results=results,
            metadata=metadata
        )
    
    def log_system_info(self, system_info: dict):
        """Log system information snapshot"""
        return self.secure_logger.log_test_result(
            test_type="system_info",
            results=system_info,
            metadata={'snapshot_type': 'full_system'}
        )
    
    def get_benchmark_history(self, benchmark_type: str = None, limit: int = 50):
        """Get benchmark history"""
        test_type = f"benchmark_{benchmark_type}" if benchmark_type else None
        return self.secure_logger.get_test_results(test_type, limit)
    
    def get_speedtest_history(self, limit: int = 50):
        """Get speedtest history"""
        return self.secure_logger.get_test_results("speedtest", limit)
    
    def get_test_statistics(self):
        """Get overall test statistics"""
        return self.secure_logger.get_statistics()
    
    def export_logs(self, output_file: str, password: str = None):
        """Export logs to file"""
        return self.secure_logger.export_results(output_file, password)
    
    def verify_integrity(self):
        """Verify log file integrity"""
        return self.secure_logger.verify_file_integrity()