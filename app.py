from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import uvicorn
from app_config import app_settings
from fusion.rental_listing.run_pipeline import run_pipeline
from entities.home_doc.api import api_router as home_doc_api_router

app = FastAPI(
    title="Fusion HomeDoc API",
    openapi_tags=[
        {"name": "HomeDocsFusion", "description": "HomeDocs Fusion"},
        {"name": "HomeDocs", "description": "Basic HomeDocs management"},
    ]
)
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router_fusion = APIRouter(
    tags=["HomeDocsFusion"]
)

@api_router_fusion.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@api_router_fusion.get("/api/fuse", tags=["HomeDocsFusion"])
async def run_fusion():
    run_pipeline("Single Family")
    return [{"id": 1, "name": "Itsik"}]

app.include_router(api_router_fusion)
app.include_router(home_doc_api_router)
#app.include_router(residence_api_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
