from fastapi import APIRouter, Query, Body, Request, Depends, status, HTTPException
from sqlmodel import Session
from typing import Optional, List
from db.session import get_session
from entities.abstracts.response_model import ResponseModel
from entities.residence.repository import ResidenceRepository
from entities.residence.service import ResidenceService
from entities.residence.dtos import ResidenceCreate, ResidenceUpdate, ResidenceResponse
from entities.residence.examples import residence_update_example, residence_create_example

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
/api/residence?page=1&limit=20&sort=-createdAt&price[$in]=1000,2000&createdAt[$gte]=2024-01-01&description[$ilike]=new

This allows powerful querying across multiple related models (except for one-to-many relations, such as List history using query string alone.
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

        data = get_residence_srv().get(session, query_dict)
        return ResponseModel(
            message="Residences fetched successfully",
            data=data,
            status=status.HTTP_200_OK
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch residences: {e}")

@api_router.post(
    "/api/residence",
    response_model=ResponseModel[ResidenceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_residence(
    residence: ResidenceCreate = Body(..., example=residence_create_example),
    session: Session = Depends(get_session)
):
    try:
        data = get_residence_srv().create(residence, session)
        return ResponseModel(
            message="Residence created successfully",
            data=data,
            status=status.HTTP_201_CREATED
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create residence: {e}")

@api_router.get(
    "/api/residence/{residence_id}",
    response_model=ResponseModel[ResidenceResponse],
)
async def get_residence_by_id(
    residence_id: int,
    session: Session = Depends(get_session)
):
    try:
        data = get_residence_srv().get_by_id(residence_id, session)
        if not data:
            raise HTTPException(status_code=404, detail="Residence not found")
        return ResponseModel(
            message="Residence fetched successfully",
            data=data,
            status=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve residence: {e}")

@api_router.put(
    "/api/residence/{residence_id}",
    response_model=ResponseModel[ResidenceResponse],
)
async def update_residence(
    residence_id: int,
    residence: ResidenceUpdate = Body(..., example=residence_update_example),
    session: Session = Depends(get_session)
):
    try:
        data = get_residence_srv().update(residence_id, residence, session)
        return ResponseModel(
            message="Residence updated successfully",
            data=data,
            status=status.HTTP_200_OK
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update residence: {e}")

@api_router.delete(
    "/api/residence/{residence_id}",
    response_model=ResponseModel[None],
)
async def delete_residence(
    residence_id: int,
    session: Session = Depends(get_session)
):
    try:
        get_residence_srv().delete(residence_id, session)
        return ResponseModel(
            message="Residence deleted successfully",
            data=None,
            status=status.HTTP_200_OK
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete residence: {e}")
