from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Exernal URLS

BOOTSTRAP_CSS_1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/css/bootstrap.min.css"
BOOTSTRAP_JS_1 = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.7/dist/js/bootstrap.bundle.min.js"

# Defining App and Static Directorys
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
        return template.TemplateResponse("components.html",
                                     {
                                         "request": requests,
                                         "BOOTSTRAP_CSS_1": BOOTSTRAP_CSS_1,
                                         "BOOTSTRAP_JS_1": BOOTSTRAP_JS_1
                                     })

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
    uvicorn.run(app=app, host="127.0.0.1", port=8000)