from fastapi import APIRouter, Query, Request, Depends
from sqlmodel import Session
from typing import Optional, Dict, Any
from db.session import get_session
from entities.home_doc.repository import HomeDocRepository
from entities.home_doc.service import HomeDocService
from entities.home_doc.models import HomeDoc
from entities.home_doc.models import HomeDocTypeEnum

api_router = APIRouter(
    tags=["HomeDocs"]
)

def get_home_doc_srv():
    home_doc_repo = HomeDocRepository.get_instance()
    home_doc_srv = HomeDocService.get_instance(home_doc_repo)
    return home_doc_srv

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

@api_router.get(
    "/api/home_docs/",
    summary="Retrieve a list of HomeDocs with advanced filtering, sorting, and pagination",
    description="""
Fetch a list of HomeDocs from the database with support for:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Number of results per page (default: 10)
- `sort`: Comma-separated fields to sort by. Use `-` for descending.  
  Example: `-createdAt,interiorEntityKey`
- `tz`: Timezone for date filtering (default: Asia/Jerusalem)
- `fields`: (optional) Specify which fields to return
- Any other field will be treated as a filter.

**Supported filter operators (use square brackets):**
- `[$eq]`: Equal (default)
- `[$ne]`: Not equal
- `[$gt]`, `[$gte]`, `[$lt]`, `[$lte]`: Greater/Less than
- `[$in]`, `[$not_in]`: Accepts comma-separated lists
- `[$like]`, `[$ilike]`: SQL-style pattern matching
- `[$wildcard]=start|end|both`: Wildcard matching position for LIKE/ILIKE filters

**Example request:**
/api/home_docs?page=2&limit=25&sort=-createdAt&createdAt[$gte]=2024-01-01&fields=id,name,description
"""
)
async def get_home_docs(
    request: Request,
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    page: int = Query(1, ge=1),
    sort: Optional[str] = Query(None),
    fields: Optional[str] = Query(None),
    tz: Optional[str] = Query("Asia/Jerusalem"),
):
    query_dict = dict(request.query_params)
    
    query_dict.setdefault("limit", str(limit))
    query_dict.setdefault("page", str(page))
    if sort:
        query_dict.setdefault("sort", sort)
    if fields:
        query_dict.setdefault("fields", fields)
    if tz:
        query_dict.setdefault("tz", tz)

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

