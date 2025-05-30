from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
import uvicorn

from app_config import app_settings
from db_config import db_settings
from fusion.rental_listing.run_pipeline import run_pipeline

app = FastAPI()

templates = Jinja2Templates(directory="templates")

password_encoded = quote_plus(db_settings.POSTGRES_PASSWORD)
DATABASE_URL = f"postgresql+psycopg://{db_settings.POSTGRES_USER}:{password_encoded}@{db_settings.POSTGRES_HOST}:{db_settings.POSTGRES_PORT}/{db_settings.POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("welcome.html", {"request": request})
    except Exception as e:
        return HTMLResponse(f"Error: {e}", status_code=500)

@app.get("/fuse")
async def run_fusion():
    run_pipeline("Single Family")
    return [{"id": 1, "name": "Itsik"}]

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
