from fastapi import FastAPI, Request, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any
import uvicorn
from app_config import app_settings
from fastapi import FastAPI
from exceptions import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from fusion.rental_listing.run_pipeline import run_pipeline
from entities.abstracts.response_model import ResponseModel
from entities.home_doc.api import api_router as home_doc_api_router
from entities.residence.api import api_router as residence_api_router

app = FastAPI(
    title="Fusion HomeDoc API",
    openapi_tags=[
        {"name": "HomeDocsFusion", "description": "HomeDocs Fusion"},
        {"name": "HomeDocs", "description": "Basic HomeDocs management"},
        {"name": "Residence", "description": "Residence management"},
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

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

api_router_fusion = APIRouter(
    tags=["HomeDocsFusion"]
)

@api_router_fusion.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request})

@api_router_fusion.get("/api/fuse", response_model=ResponseModel[list[dict[str, Any]]], tags=["HomeDocsFusion"])
async def run_fusion():
    try:
        run_pipeline("Single Family")
        return ResponseModel(message="HomeDoc retrieved successfully.", data=[{"id": 1, "name": "Itsik"}], status=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve fuse HomeDocs: {e}")


app.include_router(api_router_fusion)
app.include_router(home_doc_api_router)
app.include_router(residence_api_router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
