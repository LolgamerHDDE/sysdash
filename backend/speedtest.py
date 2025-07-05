import requests
import time
import os

SERVER_URL = "http://fra1.syncwi.de:8080"
UPLOAD_SIZE_MB = 20
DOWNLOAD_URL = f"{SERVER_URL}/speedtest/download"
UPLOAD_URL = f"{SERVER_URL}/speedtest/upload"
PING_URL = f"{SERVER_URL}/speedtest/ping"

def ping_server() -> float:
    """Measure latency to the speedtest server"""
    try:
        start = time.time()
        response = requests.get(PING_URL, timeout=5)
        end = time.time()
        if response.status_code == 200:
            return round((end - start) * 1000, 2)  # ms
        else:
            return -1
    except Exception:
        return -1

def test_download_speed() -> float:
    """Measure download speed in Mbps"""
    try:
        start = time.time()
        response = requests.get(DOWNLOAD_URL, stream=True, timeout=30)
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            total_bytes += len(chunk)
        end = time.time()

        duration = end - start
        speed_mbps = (total_bytes * 8) / (duration * 1_000_000)  # bits/sec → Mbps
        return round(speed_mbps, 2)
    except Exception:
        return -1

def test_upload_speed(size_mb: int = UPLOAD_SIZE_MB) -> float:
    """Measure upload speed in Mbps"""
    try:
        data = os.urandom(size_mb * 1024 * 1024)
        files = {'file': ('upload.dat', data, 'application/octet-stream')}
        start = time.time()
        response = requests.post(UPLOAD_URL, files=files, timeout=60)
        end = time.time()

        duration = end - start
        if response.status_code != 200:
            return -1
        speed_mbps = (len(data) * 8) / (duration * 1_000_000)
        return round(speed_mbps, 2)
    except Exception:
        return -1

def get_speedtest_results() -> dict:
    """Return all speedtest results in a single dict"""
    return {
        "ping_ms": ping_server(),
        "download_speed_mbps": test_download_speed(),
        "upload_speed_mbps": test_upload_speed()
    }
