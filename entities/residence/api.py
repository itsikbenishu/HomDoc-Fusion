from fastapi import APIRouter, Query
from sqlmodel import Session
from fastapi import Depends
from fastapi import Request
from typing import Optional
from db.session import get_session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.residence.dtos import ResidenceResponse, ResidenceCreate, ResidenceUpdate

api_router = APIRouter(
    tags=["Residence"]
)

def get_residence_srv():
    residence_repo = ResidenceRepository.get_instance()
    residence_srv = ResidenceService.get_instance(residence_repo)
    return residence_srv

@api_router.get("/api/residence/{residence_id}")
async def get_residence(
    residence_id: int,
    session: Session = Depends(get_session)
):
    return get_residence_srv().get_by_id(residence_id, session)

@api_router.get("/api/residence")
async def get_residence(
    request: Request,
    session: Session = Depends(get_session)
):
    query_params = request.query_params
    return get_residence_srv().get(session, query_params)

@api_router.post("/api/residence")
async def create_residence(
    residence: ResidenceCreate,
    session: Session = Depends(get_session)
):
    return get_residence_srv().create(ResidenceCreate, session)

@api_router.put("/api/residence/{residence_id}")
async def update_residence(
    residence_id: int,
    residence: ResidenceUpdate,
    session: Session = Depends(get_session)
):
    return get_residence_srv().update(residence_id, ResidenceUpdate, session)

@api_router.delete("/api/residence/{residence_id}")
async def delete_residence(
    residence_id: int,
    session: Session = Depends(get_session)
):
    return get_residence_srv().delete(residence_id, session)
