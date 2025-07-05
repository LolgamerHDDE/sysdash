import requests
import time
import os
from .test_logger import TestResultLogger

# Initialize logger
logger = TestResultLogger()

SERVER_URL = "http://fra1.syncwi.de:8080"
UPLOAD_SIZE_MB = 20
DOWNLOAD_URL = f"{SERVER_URL}/speedtest/download"
UPLOAD_URL = f"{SERVER_URL}/speedtest/upload"
PING_URL = f"{SERVER_URL}/speedtest/ping"

def ping_server() -> float:
    """Measure latency to the speedtest server with logging"""
    start_time = time.time()
    try:
        start = time.time()
        response = requests.get(PING_URL, timeout=5)
        end = time.time()
        
        if response.status_code == 200:
            ping_ms = round((end - start) * 1000, 2)
            
            # Log ping result
            results = {
                'ping_ms': ping_ms,
                'status_code': response.status_code,
                'server_url': PING_URL,
                'timeout': 5,
                'success': True
            }
            
        else:
            ping_ms = -1
            results = {
                'ping_ms': ping_ms,
                'status_code': response.status_code,
                'server_url': PING_URL,
                'timeout': 5,
                'success': False,
                'error': f"HTTP {response.status_code}"
            }
            
        logger.log_benchmark_result('ping', results)
        return ping_ms
        
    except Exception as e:
        results = {
            'ping_ms': -1,
            'server_url': PING_URL,
            'timeout': 5,
            'success': False,
            'error': str(e),
            'duration': round(time.time() - start_time, 2)
        }
        logger.log_benchmark_result('ping', results)
        return -1

def test_download_speed() -> float:
    """Measure download speed with logging"""
    start_time = time.time()
    try:
        start = time.time()
        response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
        total_bytes = 0
        
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            total_bytes += len(chunk)
            
        end = time.time()
        duration = end - start
        speed_mbps = (total_bytes * 8) / (duration * 1_000_000)  # bits/sec → Mbps
        speed_mbps = round(speed_mbps, 2)
        
        results = {
            'download_speed_mbps': speed_mbps,
            'total_bytes': total_bytes,
            'total_mb': round(total_bytes / (1024 * 1024), 2),
            'duration_seconds': round(duration, 2),
            'server_url': DOWNLOAD_URL,
            'success': True,
            'status_code': response.status_code
        }
        
        logger.log_benchmark_result('download', results)
        return speed_mbps
        
    except Exception as e:
        results = {
            'download_speed_mbps': -1,
            'server_url': DOWNLOAD_URL,
            'success': False,
            'error': str(e),
            'duration': round(time.time() - start_time, 2)
        }
        logger.log_benchmark_result('download', results)
        return -1

def test_upload_speed(size_mb: int = UPLOAD_SIZE_MB) -> float:
    """Measure upload speed with logging"""
    start_time = time.time()
    try:
        data = os.urandom(size_mb * 1024 * 1024)
        files = {'file': ('upload.dat', data, 'application/octet-stream')}
        
        start = time.time()
        response = requests.post(UPLOAD_URL, files=files, timeout=60)
        end = time.time()

        duration = end - start
        
        if response.status_code == 200:
            speed_mbps = (len(data) * 8) / (duration * 1_000_000)
            speed_mbps = round(speed_mbps, 2)
            success = True
        else:
            speed_mbps = -1
            success = False

        results = {
            'upload_speed_mbps': speed_mbps,
            'upload_size_mb': size_mb,
            'upload_bytes': len(data),
            'duration_seconds': round(duration, 2),
            'server_url': UPLOAD_URL,
            'success': success,
            'status_code': response.status_code
        }
        
        logger.log_benchmark_result('upload', results)
        return speed_mbps
        
    except Exception as e:
        results = {
            'upload_speed_mbps': -1,
            'upload_size_mb': size_mb,
            'server_url': UPLOAD_URL,
            'success': False,
            'error': str(e),
            'duration': round(time.time() - start_time, 2)
        }
        logger.log_benchmark_result('upload', results)
        return -1

def get_speedtest_results() -> dict:
    """Return all speedtest results with comprehensive logging"""
    test_start = time.time()
    
    print("Starting network speed test...")
    
    ping_result = ping_server()
    download_result = test_download_speed()
    upload_result = test_upload_speed()
    
    test_end = time.time()
    total_duration = round(test_end - test_start, 2)
    
    # Compile complete speedtest results
    complete_results = {
        "ping_ms": ping_result,
        "download_speed_mbps": download_result,
        "upload_speed_mbps": upload_result,
        "total_test_duration": total_duration,
        "server_info": {
            "server_url": SERVER_URL,
            "ping_endpoint": PING_URL,
            "download_endpoint": DOWNLOAD_URL,
            "upload_endpoint": UPLOAD_URL
        },
        "test_success": all([
            ping_result > 0,
            download_result > 0,
            upload_result > 0
        ])
    }
    
    # Log the complete speedtest session
    logger.log_speedtest_result(complete_results, complete_results["server_info"])
    
    print(f"Speed test completed in {total_duration} seconds")
    
    return complete_results

def get_speedtest_history(limit: int = 10):
    """Get speedtest history from encrypted logs"""
    return logger.get_speedtest_history(limit)
