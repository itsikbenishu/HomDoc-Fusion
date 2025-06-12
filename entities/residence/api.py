from fastapi import APIRouter, Query
from sqlmodel import Session
from fastapi import Depends
from fastapi import Request
from typing import Optional
from db.session import get_session
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.residence.dtos import ResidenceCreate, ResidenceUpdate

api_router = APIRouter(
    tags=["Residence"]
)

def get_residence_srv():
    residence_repo = ResidenceRepository.get_instance()
    residence_srv = ResidenceService.get_instance(residence_repo)
    return residence_srv

@api_router.get(
    "/api/residence",
    summary="Retrieve a list of Residences with advanced filtering, sorting, and pagination",
    description="""
Fetch a list of Residences from the database with support for:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Number of results per page (default: 10)
- `sort`: Comma-separated fields to sort by. Use `-` for descending.  
  Example: `-createdAt,city`
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
/api/residence?page=1&limit=20&sort=-createdAt&price[$in]=1000,2000&createdAt[$gte]=2024-01-01&description[$ilike]=garden

This allows powerful querying across multiple related models (except for one-to-many relations, such as List History) using query string alone.
"""
)
async def get_residence(
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

    return get_residence_srv().get(session, query_dict)

@api_router.post("/api/residence") 
async def create_residence(
    residence: ResidenceCreate,
    session: Session = Depends(get_session)
):
    return get_residence_srv().create(residence, session)

@api_router.get("/api/residence/{residence_id}")
async def get_residence(
    residence_id: int,
    session: Session = Depends(get_session)
):
    return get_residence_srv().get_by_id(residence_id, session)

@api_router.put("/api/residence/{residence_id}")
async def update_residence(
    residence_id: int,
    residence: ResidenceUpdate,
    session: Session = Depends(get_session)
):
    return get_residence_srv().update(residence_id, residence, session)

@api_router.delete("/api/residence/{residence_id}")
async def delete_residence(
    residence_id: int,
    session: Session = Depends(get_session)
):
    return get_residence_srv().delete(residence_id, session)
