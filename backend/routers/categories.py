from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=List[schemas.Category])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    return db.query(models.Category).all()


@router.post("", response_model=schemas.Category, status_code=201)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    # Check if category with same name already exists
    existing = db.query(models.Category).filter(
        models.Category.name == category.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    db_category = models.Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category."""
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)

    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category."""
    db_category = db.query(models.Category).filter(
        models.Category.id == category_id
    ).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if any merchants or category rewards use this category
    merchants_count = db.query(models.Merchant).filter(
        models.Merchant.category_id == category_id
    ).count()
    rewards_count = db.query(models.CategoryReward).filter(
        models.CategoryReward.category_id == category_id
    ).count()

    if merchants_count > 0 or rewards_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category: {merchants_count} merchant(s) and {rewards_count} reward(s) are using it"
        )

    db.delete(db_category)
    db.commit()
    return None
