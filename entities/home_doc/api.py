from fastapi import APIRouter, Query
from sqlmodel import Session
from fastapi import Depends
from fastapi import Request
from typing import Optional
from db.session import get_session
from entities.home_doc.repository import HomeDocRepository
from entities.home_doc.service import HomeDocService
from entities.home_doc.models import HomeDoc
from entities.home_doc.models import HomeDocTypeEnum

api_router = APIRouter(
    tags=["HomeDocs"]
)

@api_router.get("/api/home_docs/newest-properties")
async def get_newest_properties(
    count: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query_dict = {
        "type": HomeDocTypeEnum.PROPERTY,
        "limit": count,
        "order": "created_at",
        "offset": 0
    }
    return get_home_doc_srv().get(session, query_dict)

@api_router.get("/api/home_docs/oldest-properties")
async def get_oldest_properties(
    count: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query_dict = {
        "type": HomeDocTypeEnum.PROPERTY,
        "limit": count,
        "order": "-created_at",
        "offset": 0
    }
    return get_home_doc_srv().get(session, query_dict)

def get_home_doc_srv():
    home_doc_repo = HomeDocRepository.get_instance()
    home_doc_srv = HomeDocService.get_instance(home_doc_repo)
    return home_doc_srv

@api_router.get("/api/home_docs")
async def get_home_docs(
    request: Request, 
    session: Session = Depends(get_session)
):
    query_dict = dict(request.query_params)
    return get_home_doc_srv().get(session, query_dict)

@api_router.get("/api/home_docs/{home_doc_id}")
async def get_home_doc(
    home_doc_id: int,
    session: Session = Depends(get_session)
):
    return get_home_doc_srv().get_by_id(home_doc_id, session)

@api_router.post("/api/home_docs")
async def create_home_doc(
    home_doc: HomeDoc,
    session: Session = Depends(get_session)
):
    return get_home_doc_srv().create(home_doc.model_dump(), session)

@api_router.put("/api/home_docs/{home_doc_id}")
async def update_home_doc(
    home_doc_id: int,
    home_doc: HomeDoc,
    session: Session = Depends(get_session)
):
    return get_home_doc_srv().update(home_doc_id, home_doc.model_dump(), session)

@api_router.delete("/api/home_docs/{home_doc_id}")
async def delete_home_doc(
    home_doc_id: int,     
    session: Session = Depends(get_session)
):
    return get_home_doc_srv().delete(home_doc_id, session)

