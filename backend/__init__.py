"""
SysDash Backend Module
Comprehensive system information, benchmarking, and secure logging functionality
"""

# Version information
__version__ = "1.0.0"
__author__ = "LolgamerHD"
__description__ = "SysDash Backend - System monitoring and benchmarking with secure logging"

# Core system information functions
from backend.sysinfo import (
    get_all_cpu_info,
    get_cpu_details,
    get_cpu_stats,
    get_disk_io,
    get_disk_partitions,
    get_full_system_info,
    get_lscpu_info,
    get_network_info,
    get_platform_info,
    get_ram_info,
    get_sys_info,
    get_sysctl_info,
    get_wmic_info
)

# Network speed testing functions
from backend.speedtest import (
    ping_server,
    get_speedtest_results,
    test_download_speed,
    test_upload_speed
)

# Benchmark functions
from backend.benchmark import (
    ram_copy_speed,
    run_full_benchmark,
    gpu_benchmark,
    disk_benchmark,
    cpu_multi_thread,
    cpu_single_thread
)

# Secure logging system
try:
    from backend.crypto_utils import SecureLogger
    from backend.test_logger import TestResultLogger
    from backend.log_backup import LogBackupManager
    from backend.logging_config import LoggingConfig
    from backend.init_logging import initialize_logging
    LOGGING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Secure logging system not available: {e}")
    LOGGING_AVAILABLE = False
    
    # Create dummy classes for graceful degradation
    class SecureLogger:
        def __init__(self, *args, **kwargs):
            raise ImportError("Secure logging not available")
    
    class TestResultLogger:
        def __init__(self, *args, **kwargs):
            raise ImportError("Test result logging not available")
    
    class LogBackupManager:
        def __init__(self, *args, **kwargs):
            raise ImportError("Log backup system not available")
    
    class LoggingConfig:
        @staticmethod
        def load_config():
            return {}
    
    def initialize_logging():
        raise ImportError("Logging initialization not available")

# Utility functions for easy access
def get_system_overview():
    """Get a comprehensive system overview with key metrics"""
    try:
        system_info = get_full_system_info()
        
        # Extract key metrics for overview
        overview = {
            'cpu': {
                'model': system_info.get('cpu_info', {}).get('cpu_details', {}).get('brand_raw', 'Unknown'),
                'cores': system_info.get('cpu_info', {}).get('cpu_details', {}).get('count', 0),
                'usage': system_info.get('cpu_info', {}).get('cpu_stats', {}).get('cpu_percent', 0)
            },
            'memory': {
                'total_gb': round(system_info.get('ram_info', {}).get('total', 0) / (1024**3), 2),
                'used_gb': round(system_info.get('ram_info', {}).get('used', 0) / (1024**3), 2),
                'usage_percent': system_info.get('ram_info', {}).get('percent', 0)
            },
            'disk': {
                'partitions': len(system_info.get('disk_partitions', [])),
                'total_usage': system_info.get('disk_io', {})
            },
            'network': system_info.get('network_info', {}),
            'platform': system_info.get('cpu_info', {}).get('sys_info', {})
        }
        
        return overview
    except Exception as e:
        return {'error': f'Failed to get system overview: {e}'}

def run_quick_benchmark():
    """Run a quick benchmark suite with essential tests"""
    try:
        results = {
            'cpu_single': cpu_single_thread(),
            'cpu_multi': cpu_multi_thread(),
            'ram_speed': ram_copy_speed(),
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        # Add disk benchmark
        try:
            disk_write, disk_read = disk_benchmark()
            results['disk_write'] = disk_write
            results['disk_read'] = disk_read
        except Exception as e:
            results['disk_error'] = str(e)
        
        # Add GPU benchmark if available
        try:
            gpu_result = gpu_benchmark()
            results['gpu'] = gpu_result
        except Exception as e:
            results['gpu_error'] = str(e)
        
        return results
    except Exception as e:
        return {'error': f'Benchmark failed: {e}'}

def run_network_test():
    """Run comprehensive network testing"""
    try:
        # Get network info
        network_info = get_network_info()
        
        # Run speed test
        speed_results = get_speedtest_results()
        
        return {
            'network_interfaces': network_info,
            'speed_test': speed_results,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': f'Network test failed: {e}'}

def log_test_result(test_type, results, logger=None):
    """Convenience function to log test results"""
    if not LOGGING_AVAILABLE:
        print(f"Warning: Logging not available, test result not saved: {test_type}")
        return None
    
    try:
        if logger is None:
            logger = TestResultLogger()
        
        if test_type in ['cpu_single', 'cpu_multi', 'ram', 'disk', 'gpu']:
            return logger.log_benchmark_result(test_type, results)
        elif test_type == 'speedtest':
            return logger.log_speedtest_result(results)
        else:
            return logger.log_benchmark_result(test_type, results)
    except Exception as e:
        print(f"Warning: Failed to log test result: {e}")
        return None

def get_test_history(test_type=None, limit=10):
    """Get test history with optional filtering"""
    if not LOGGING_AVAILABLE:
        return []
    
    try:
        logger = TestResultLogger()
        
        if test_type == 'speedtest':
            return logger.get_speedtest_history(limit)
        elif test_type and test_type in ['cpu_single', 'cpu_multi', 'ram', 'disk', 'gpu']:
            return logger.get_benchmark_history(test_type, limit)
        else:
            # Get all results
            all_results = logger.secure_logger.get_test_results()
            if test_type:
                all_results = [r for r in all_results if r.get('test_type') == test_type]
            return all_results[-limit:] if len(all_results) > limit else all_results
    except Exception as e:
        print(f"Warning: Failed to get test history: {e}")
        return []

def verify_system_integrity():
    """Verify the integrity of the logging system and backend"""
    status = {
        'backend_available': True,
        'logging_available': LOGGING_AVAILABLE,
        'system_info_working': False,
        'benchmarks_working': False,
        'speedtest_working': False,
        'log_integrity': None
    }
    
    # Test system info
    try:
        info = get_full_system_info()
        status['system_info_working'] = 'error' not in info
    except Exception:
        status['system_info_working'] = False
    
    # Test benchmarks
    try:
        cpu_result = cpu_single_thread()
        status['benchmarks_working'] = isinstance(cpu_result, (int, float))
    except Exception:
        status['benchmarks_working'] = False
    
    # Test speedtest
    try:
        ping_result = ping_server()
        status['speedtest_working'] = ping_result > 0
    except Exception:
        status['speedtest_working'] = False
    
    # Test log integrity
    if LOGGING_AVAILABLE:
        try:
            logger = TestResultLogger()
            integrity = logger.verify_integrity()
            status['log_integrity'] = integrity['status']
        except Exception as e:
            status['log_integrity'] = f'error: {e}'
    
    return status

def create_system_report():
    """Create a comprehensive system report"""
    report = {
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'sysdash_version': __version__,
        'system_overview': get_system_overview(),
        'integrity_check': verify_system_integrity()
    }
    
    # Add recent test history if logging is available
    if LOGGING_AVAILABLE:
        try:
            logger = TestResultLogger()
            report['recent_tests'] = {
                'total_tests': len(logger.secure_logger.get_test_results()),
                'statistics': logger.get_test_statistics(),
                'recent_benchmarks': logger.get_benchmark_history('cpu_single', 5),
                'recent_speedtests': logger.get_speedtest_history(5)
            }
        except Exception as e:
            report['recent_tests'] = {'error': str(e)}
    
    return report

# Export all public functions and classes
__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__description__',
    
    # System information
    'get_all_cpu_info',
    'get_cpu_details', 
    'get_cpu_stats',
    'get_disk_io',
    'get_disk_partitions',
    'get_full_system_info',
    'get_lscpu_info',
    'get_network_info',
    'get_platform_info',
    'get_ram_info',
    'get_sys_info',
    'get_sysctl_info',
    'get_wmic_info',
    
    # Speed testing
    'ping_server',
    'get_speedtest_results',
    'test_download_speed',
    'test_upload_speed',
    
    # Benchmarking
    'ram_copy_speed',
    'run_full_benchmark',
    'gpu_benchmark',
    'disk_benchmark',
    'cpu_multi_thread',
    'cpu_single_thread',
    
    # Secure logging (if available)
    'SecureLogger',
    'TestResultLogger',
    'LogBackupManager',
    'LoggingConfig',
    'initialize_logging',
    'LOGGING_AVAILABLE',
    
    # Utility functions
    'get_system_overview',
    'run_quick_benchmark',
    'run_network_test',
    'log_test_result',
    'get_test_history',
    'verify_system_integrity',
    'create_system_report'
]

# Initialize logging system on import if available
if LOGGING_AVAILABLE:
    try:
        initialize_logging()
        print("✅ SysDash backend initialized with secure logging")
    except Exception as e:
        print(f"⚠️ SysDash backend initialized but logging setup failed: {e}")
        LOGGING_AVAILABLE = False
else:
    print("⚠️ SysDash backend initialized without secure logging")

# Module-level configuration
BACKEND_CONFIG = {
    'version': __version__,
    'logging_enabled': LOGGING_AVAILABLE,
    'features': {
        'system_info': True,
        'benchmarking': True,
        'speed_testing': True,
        'secure_logging': LOGGING_AVAILABLE,
        'backup_system': LOGGING_AVAILABLE
    }
}

def get_backend_info():
    """Get information about the backend module"""
    return BACKEND_CONFIG.copy()
