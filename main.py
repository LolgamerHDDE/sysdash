from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Run the Application
if __name__ == "__main__":
    multiprocessing.freeze_support()
    print(f"Backend available: {BACKEND_AVAILABLE}")
    print(f"Speedtest available: {SPEEDTEST_AVAILABLE}")
    print(f"Benchmark available: {BENCHMARK_AVAILABLE}")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)