from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

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
                                         "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1
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

# Tests
@app.get("/tests")
async def tests(requests: Request):
    return template.TemplateResponse("tests.html",
                                     {
                                         "request": requests,
                                         "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                         "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1
                                     })

# Run the Application
if __name__ == "__main__":
    print(f"Backend available: {BACKEND_AVAILABLE}")
    uvicorn.run(app=app, host="127.0.0.1", port=8000)
