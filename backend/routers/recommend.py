from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from backend import schemas
from backend.database import get_db
from backend.services import recommendation

router = APIRouter(prefix="/api/recommend", tags=["recommendations"])


@router.get("", response_model=schemas.RecommendationResponse)
def get_recommendations(
    category_id: Optional[int] = Query(None, description="Category ID to get recommendations for"),
    merchant: Optional[str] = Query(None, description="Merchant name to resolve to category"),
    db: Session = Depends(get_db)
):
    """
    Get ranked card recommendations.
    Provide either category_id OR merchant name.
    """
    if category_id is None and merchant is None:
        raise HTTPException(
            status_code=400,
            detail="Must provide either category_id or merchant parameter"
        )

    if category_id is not None and merchant is not None:
        raise HTTPException(
            status_code=400,
            detail="Cannot provide both category_id and merchant parameters"
        )

    if merchant:
        result = recommendation.get_recommendations_by_merchant(db, merchant)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Merchant '{merchant}' not found"
            )
    else:
        result = recommendation.get_recommendations(db, category_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id {category_id} not found"
            )

    return result


@router.get("/simple", response_model=schemas.SimpleRecommendationResponse)
def get_simple_recommendation(
    category_id: int = Query(..., description="Category ID to get recommendation for"),
    db: Session = Depends(get_db)
):
    """
    Get the top recommended card for a category (simple view).
    Returns only the best card.
    """
    result = recommendation.get_simple_recommendation(db, category_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id {category_id} not found or no cards available"
        )

    return result
