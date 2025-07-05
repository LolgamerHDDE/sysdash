from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from backend.log_backup import LogBackupManager
from backend.init_logging import initialize_logging, cleanup_old_logs
from backend.logging_config import LoggingConfig
from datetime import datetime
from backend.test_logger import TestResultLogger
from backend.benchmark import run_full_benchmark
from backend.speedtest import get_speedtest_results
import multiprocessing
import uvicorn

if __name__ == "__main__":
    multiprocessing.freeze_support()

# Try to import backend functions
try:
    from backend.sysinfo import get_full_system_info
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import backend functions: {e}")
    BACKEND_AVAILABLE = False
    
    # Create a dummy function for testing
    def get_full_system_info():
        return {
            "error": "Backend functions not available",
            "cpu_info": {"sys_info": {"python_version": "Unknown"}},
            "ram_info": {},
            "disk_partitions": [],
            "disk_io": {},
            "network_info": {}
        }

try:
    from backend.speedtest import get_speedtest_results, ping_server, test_download_speed, test_upload_speed
    SPEEDTEST_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import speedtest functions: {e}")
    SPEEDTEST_AVAILABLE = False

# Try to import speedtest functions
try:
    from backend.speedtest import get_speedtest_results, ping_server, test_download_speed, test_upload_speed
    SPEEDTEST_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import speedtest functions: {e}")
    SPEEDTEST_AVAILABLE = False
    
    # Create dummy functions for testing
    def get_speedtest_results():
        return {
            "error": "Speedtest functions not available",
            "ping_ms": -1,
            "download_speed_mbps": -1,
            "upload_speed_mbps": -1
        }
    
    def ping_server():
        return -1
    
    def test_download_speed():
        return -1
    
    def test_upload_speed():
        return -1

# Try to import benchmark functions
try:
    from backend.benchmark import (
        run_full_benchmark, 
        cpu_single_thread, 
        cpu_multi_thread, 
        ram_copy_speed, 
        disk_benchmark, 
        gpu_benchmark
    )
    BENCHMARK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import benchmark functions: {e}")
    BENCHMARK_AVAILABLE = False
    
    # Create dummy functions for testing
    def run_full_benchmark():
        return {
            "error": "Benchmark functions not available",
            "cpu_single_thread_sec": -1,
            "cpu_multi_thread_sec": -1,
            "ram_copy_speed_MBps": -1,
            "disk_write_MBps": -1,
            "disk_read_MBps": -1,
            "gpu_vector_add_sec": "GPU not available"
        }
    
    def cpu_single_thread():
        return -1
    
    def cpu_multi_thread():
        return -1
    
    def ram_copy_speed():
        return -1
    
    def disk_benchmark():
        return -1, -1
    
    def gpu_benchmark():
        return None

# External URLS
BOOTSTRAP_CSS_1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css"
BOOTSTRAP_JS_1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"

# Defining App and Static Directories
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
template = Jinja2Templates(directory="frontend")

@app.on_event("startup")
async def startup_event():
    """Initialize logging system when the application starts"""
    try:
        initialize_logging()
        print("✅ Secure logging system initialized")
        
        # Create initial backup if enabled
        if LoggingConfig.should_backup():
            try:
                backup_manager = LogBackupManager()
                backup_path = backup_manager.create_backup()
                print(f"✅ Initial backup created: {backup_path}")
            except Exception as e:
                print(f"⚠️ Could not create initial backup: {e}")
                
    except Exception as e:
        print(f"❌ Error initializing logging system: {e}")

# Root Directory
@app.get("/")
async def root(requests: Request):
    return template.TemplateResponse("index.html",
                                     {
                                         "request": requests,
                                         "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                         "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1,
                                         "speedtest_available": SPEEDTEST_AVAILABLE,
                                         "benchmark_available": BENCHMARK_AVAILABLE
                                     })

# Components List
@app.get("/components")
async def components(requests: Request):
    try:
        # Get full system information
        system_info = get_full_system_info()
        print(f"System info retrieved: {type(system_info)}")  # Debug print
        
        return template.TemplateResponse("components.html",
                                         {
                                             "request": requests,
                                             "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                             "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1,
                                             "system_info": system_info
                                         })
    except Exception as e:
        print(f"Error in components endpoint: {e}")
        return template.TemplateResponse("components.html",
                                         {
                                             "request": requests,
                                             "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                             "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1,
                                             "system_info": {"error": str(e)}
                                         })

# Tests page with speedtest and benchmark functionality
@app.get("/tests")
async def tests(requests: Request):
    return template.TemplateResponse("tests.html",
                                     {
                                         "request": requests,
                                         "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                         "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1,
                                         "speedtest_available": SPEEDTEST_AVAILABLE,
                                         "benchmark_available": BENCHMARK_AVAILABLE
                                     })

# API endpoints for different system components
@app.get("/api/components")
async def api_components():
    try:
        return get_full_system_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cpu")
async def api_cpu():
    try:
        from backend.sysinfo import get_all_cpu_info
        return get_all_cpu_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ram")
async def api_ram():
    try:
        from backend.sysinfo import get_ram_info
        return get_ram_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/disk")
async def api_disk():
    try:
        from backend.sysinfo import get_disk_partitions, get_disk_io
        return {
            "partitions": get_disk_partitions(),
            "io": get_disk_io()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/network")
async def api_network():
    try:
        from backend.sysinfo import get_network_info
        return get_network_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Speedtest API endpoints
@app.get("/api/speedtest")
async def api_speedtest():
    if not SPEEDTEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Speedtest functionality not available")
    try:
        from backend.speedtest import get_speedtest_results
        return get_speedtest_results()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speedtest/ping")
async def api_speedtest_ping():
    if not SPEEDTEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Speedtest functionality not available")
    try:
        from backend.speedtest import ping_server
        return {"ping_ms": ping_server()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speedtest/download")
async def api_speedtest_download():
    if not SPEEDTEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Speedtest functionality not available")
    try:
        from backend.speedtest import test_download_speed
        return {"download_speed_mbps": test_download_speed()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/speedtest/upload")
async def api_speedtest_upload():
    if not SPEEDTEST_AVAILABLE:
        raise HTTPException(status_code=503, detail="Speedtest functionality not available")
    try:
        from backend.speedtest import test_upload_speed
        return {"upload_speed_mbps": test_upload_speed()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Benchmark API endpoints
@app.get("/api/benchmark")
async def api_benchmark():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import run_full_benchmark
        return run_full_benchmark()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/cpu-single")
async def api_benchmark_cpu_single():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import cpu_single_thread
        return {"cpu_single_thread_sec": cpu_single_thread()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/cpu-multi")
async def api_benchmark_cpu_multi():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import cpu_multi_thread
        return {"cpu_multi_thread_sec": cpu_multi_thread()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/ram")
async def api_benchmark_ram():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import ram_copy_speed
        return {"ram_copy_speed_MBps": ram_copy_speed()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/disk")
async def api_benchmark_disk():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import disk_benchmark
        write_speed, read_speed = disk_benchmark()
        return {
            "disk_write_MBps": write_speed,
            "disk_read_MBps": read_speed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/gpu")
async def api_benchmark_gpu():
    if not BENCHMARK_AVAILABLE:
        raise HTTPException(status_code=503, detail="Benchmark functionality not available")
    try:
        from backend.benchmark import gpu_benchmark
        return {"gpu_vector_add_sec": gpu_benchmark()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Test history and statistics endpoints
@app.get("/api/test-history")
async def api_test_history(test_type: str = None, limit: int = 50):
    """Get test history from encrypted logs"""
    try:
        from backend.test_logger import TestResultLogger
        logger = TestResultLogger()
        
        if test_type:
            if test_type.startswith('benchmark_'):
                benchmark_type = test_type.replace('benchmark_', '')
                return logger.get_benchmark_history(benchmark_type, limit)
            elif test_type == 'speedtest':
                return logger.get_speedtest_history(limit)
            else:
                return logger.secure_logger.get_test_results(test_type, limit)
        else:
            return logger.secure_logger.get_test_results(None, limit)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-statistics")
async def api_test_statistics():
    """Get test statistics from encrypted logs"""
    try:
        from backend.test_logger import TestResultLogger
        logger = TestResultLogger()
        return logger.get_test_statistics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify-logs")
async def api_verify_logs():
    """Verify integrity of encrypted log files"""
    try:
        from backend.test_logger import TestResultLogger
        logger = TestResultLogger()
        return logger.verify_integrity()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-logs")
async def api_export_logs(output_file: str, password: str = None):
    """Export encrypted logs to a new file"""
    try:
        from backend.test_logger import TestResultLogger
        logger = TestResultLogger()
        success = logger.export_logs(output_file, password)
        return {"success": success, "output_file": output_file}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced benchmark endpoints that return history
@app.get("/api/benchmark-history/{benchmark_type}")
async def api_benchmark_history(benchmark_type: str, limit: int = 10):
    """Get specific benchmark history"""
    try:
        from backend.benchmark import get_benchmark_history
        return get_benchmark_history(benchmark_type, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speedtest-history")
async def api_speedtest_history(limit: int = 10):
    """Get speedtest history"""
    try:
        from backend.speedtest import get_speedtest_history
        return get_speedtest_history(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/backup")
async def api_create_backup():
    """Create a backup of the current log file"""
    try:
        backup_manager = LogBackupManager()
        backup_path = backup_manager.create_backup()
        return {
            "success": True,
            "backup_path": backup_path,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/backups")
async def api_list_backups():
    """List all available log backups"""
    try:
        backup_manager = LogBackupManager()
        backups = backup_manager.list_backups()
        return {"backups": backups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/restore")
async def api_restore_backup(backup_filename: str):
    """Restore a log backup"""
    try:
        backup_manager = LogBackupManager()
        success = backup_manager.restore_backup(backup_filename)
        return {
            "success": success,
            "restored_from": backup_filename,
            "restored_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs/cleanup")
async def api_cleanup_logs(days_to_keep: int = 30):
    """Clean up old log entries"""
    try:
        result = cleanup_old_logs(days_to_keep)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs/config")
async def api_log_config():
    """Get current logging configuration"""
    try:
        return {
            "log_file": LoggingConfig.get_log_file_path(),
            "max_entries": LoggingConfig.get_max_entries(),
            "backup_enabled": LoggingConfig.should_backup(),
            "backup_interval_hours": LoggingConfig.get_backup_interval(),
            "password_set": LoggingConfig.get_password() is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-history")
async def api_test_history(test_type: str = None, limit: int = 10):
    """Get test history with optional filtering"""
    try:
        logger = TestResultLogger()
        
        if test_type and test_type.startswith('benchmark_'):
            benchmark_type = test_type.replace('benchmark_', '')
            results = logger.get_benchmark_history(benchmark_type, limit)
        elif test_type == 'speedtest':
            results = logger.get_speedtest_history(limit)
        else:
            # Get all results
            all_results = logger.secure_logger.get_test_results()
            if test_type:
                all_results = [r for r in all_results if r.get('test_type') == test_type]
            results = all_results[-limit:] if len(all_results) > limit else all_results
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-statistics")
async def api_test_statistics():
    """Get comprehensive test statistics"""
    try:
        logger = TestResultLogger()
        stats = logger.get_test_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/verify-logs")
async def api_verify_logs():
    """Verify log file integrity"""
    try:
        logger = TestResultLogger()
        integrity = logger.verify_integrity()
        return integrity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/speedtest")
async def api_speedtest_with_logging():
    """Run speed test and log results"""
    try:
        # Run speed test
        results = get_speedtest_results()
        
        # Log results
        logger = TestResultLogger()
        logger.log_speedtest_result(results)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/benchmark/full")
async def api_full_benchmark_with_logging():
    """Run full benchmark suite and log results"""
    try:
        # Run full benchmark
        results = run_full_benchmark()
        
        # Log individual benchmark results
        logger = TestResultLogger()
        
        # Log each benchmark type separately
        benchmark_mapping = {
            'cpu_single_thread_sec': 'cpu_single',
            'cpu_multi_thread_sec': 'cpu_multi', 
            'ram_copy_speed_MBps': 'ram',
            'disk_write_MBps': 'disk_write',
            'disk_read_MBps': 'disk_read',
            'gpu_vector_add_sec': 'gpu'
        }
        
        for key, benchmark_type in benchmark_mapping.items():
            if key in results:
                benchmark_result = {
                    'value': results[key],
                    'unit': 'seconds' if 'sec' in key else 'MBps',
                    'timestamp': datetime.now().isoformat()
                }
                logger.log_benchmark_result(benchmark_type, benchmark_result)
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Update the startup event to include more initialization
@app.on_event("startup")
async def startup_event():
    """Initialize all systems when the application starts"""
    try:
        # Initialize logging system
        from backend.init_logging import initialize_logging
        initialize_logging()
        print("✅ Secure logging system initialized")
        
        # Create initial backup if enabled
        from backend.logging_config import LoggingConfig
        if LoggingConfig.should_backup():
            try:
                from backend.log_backup import LogBackupManager
                backup_manager = LogBackupManager()
                backup_path = backup_manager.create_backup()
                print(f"✅ Initial backup created: {backup_path}")
            except Exception as e:
                print(f"⚠️ Could not create initial backup: {e}")
        
        # Log application startup
        logger = TestResultLogger()
        startup_info = {
            'event': 'application_startup',
            'timestamp': datetime.now().isoformat(),
            'backend_available': BACKEND_AVAILABLE
        }
        logger.log_benchmark_result('system_event', startup_info)
        print("✅ Application startup logged")
                
    except Exception as e:
        print(f"❌ Error during startup: {e}")

# Add graceful shutdown logging
@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown"""
    try:
        logger = TestResultLogger()
        shutdown_info = {
            'event': 'application_shutdown',
            'timestamp': datetime.now().isoformat()
        }
        logger.log_benchmark_result('system_event', shutdown_info)
        print("✅ Application shutdown logged")
    except Exception as e:
        print(f"⚠️ Error logging shutdown: {e}")

# Run the Application
if __name__ == "__main__":
    multiprocessing.freeze_support()
    print(f"Backend available: {BACKEND_AVAILABLE}")
    print(f"Speedtest available: {SPEEDTEST_AVAILABLE}")
    print(f"Benchmark available: {BENCHMARK_AVAILABLE}")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)