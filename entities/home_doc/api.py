from fastapi import APIRouter, Query, Body, Request, Depends, HTTPException, status 
from sqlmodel import Session
from typing import Optional, List
from db.session import get_session
from entities.home_doc.repository import HomeDocRepository
from entities.home_doc.service import HomeDocService
from entities.home_doc.models import HomeDoc, HomeDocTypeEnum
from entities.home_doc.dtos import HomeDocCreate, HomeDocUpdate
from entities.home_doc.examples import home_doc_create_example, home_doc_update_example
from entities.abstracts.response_model import ResponseModel

api_router = APIRouter(tags=["HomeDocs"])

def get_home_doc_srv():
    home_doc_repo = HomeDocRepository.get_instance()
    home_doc_srv = HomeDocService.get_instance(home_doc_repo)
    return home_doc_srv

@api_router.get("/api/home_docs/newest-properties", response_model=ResponseModel[List[HomeDoc]])
async def get_newest_properties(
    count: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    try:
        query_dict = {
            "type": HomeDocTypeEnum.PROPERTY,
            "limit": count,
            "order": "created_at",
            "offset": 0
        }
        data = get_home_doc_srv().get(session, query_dict)
        return ResponseModel(message="Newest properties fetched successfully.", data=data, status=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch newest properties: {e}")

@api_router.get("/api/home_docs/oldest-properties", response_model=ResponseModel[List[HomeDoc]])
async def get_oldest_properties(
    count: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    try:
        query_dict = {
            "type": HomeDocTypeEnum.PROPERTY,
            "limit": count,
            "order": "-created_at",
            "offset": 0
        }
        data = get_home_doc_srv().get(session, query_dict)
        return ResponseModel(message="Oldest properties fetched successfully.", data=data, status=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch oldest properties: {e}")

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
/api/home_docs?page=2&limit=25&sort=-createdAt&createdAt[$gte]=2024-01-01&fields=id,createAt,description
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
    try:
        query_dict = dict(request.query_params)
        query_dict.setdefault("limit", str(limit))
        query_dict.setdefault("page", str(page))
        if sort:
            query_dict.setdefault("sort", sort)
        if fields:
            query_dict.setdefault("fields", fields)
        if tz:
            query_dict.setdefault("tz", tz)

        data = get_home_doc_srv().get(session, query_dict)
        return ResponseModel(message="HomeDocs fetched successfully.", data=data, status=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch home docs: {e}")

@api_router.get("/api/home_docs/{home_doc_id}", response_model=ResponseModel[HomeDoc])
async def get_home_doc(
    home_doc_id: int,
    session: Session = Depends(get_session)
):
    try:
        data = get_home_doc_srv().get_by_id(home_doc_id, session)
        if not data:
            raise HTTPException(status_code=404, detail="HomeDoc not found")
        return ResponseModel(message="HomeDoc retrieved successfully.", data=data, status=status.HTTP_200_OK)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve HomeDoc: {e}")

@api_router.post("/api/home_docs", response_model=ResponseModel[HomeDoc], status_code=status.HTTP_201_CREATED)
async def create_home_doc(
    home_doc: HomeDocCreate = Body(..., example=home_doc_create_example),
    session: Session = Depends(get_session)
):
    try:
        data = get_home_doc_srv().create(home_doc.model_dump(), session)
        return ResponseModel(message="HomeDoc created successfully.", data=data, status=status.HTTP_201_CREATED)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create HomeDoc: {e}")

@api_router.put("/api/home_docs/{home_doc_id}", response_model=ResponseModel[HomeDoc])
async def update_home_doc(
    home_doc_id: int,
    home_doc: HomeDocUpdate = Body(..., example=home_doc_update_example),
    session: Session = Depends(get_session)
):
    try:
        data = get_home_doc_srv().update(home_doc_id, home_doc.model_dump(), session)
        return ResponseModel(message="HomeDoc updated successfully.", data=data, status=status.HTTP_200_OK)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update HomeDoc: {e}")

@api_router.delete("/api/home_docs/{home_doc_id}", response_model=ResponseModel[None])
async def delete_home_doc(
    home_doc_id: int,
    session: Session = Depends(get_session)
):
    try:
        get_home_doc_srv().delete(home_doc_id, session)
        return ResponseModel(message="HomeDoc deleted successfully.", data=None, status=status.HTTP_200_OK)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete HomeDoc: {e}")
