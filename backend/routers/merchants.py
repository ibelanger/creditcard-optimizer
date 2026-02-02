from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/api/merchants", tags=["merchants"])


@router.get("", response_model=List[schemas.Merchant])
def list_merchants(db: Session = Depends(get_db)):
    """List all merchants."""
    merchants = db.query(models.Merchant).all()
    result = []
    for merchant in merchants:
        merchant_dict = {
            "id": merchant.id,
            "name": merchant.name,
            "category_id": merchant.category_id,
            "category_name": merchant.category.name if merchant.category else None
        }
        result.append(schemas.Merchant(**merchant_dict))
    return result


@router.get("/search", response_model=List[schemas.Merchant])
def search_merchants(q: str, db: Session = Depends(get_db)):
    """Search merchants by name."""
    merchants = db.query(models.Merchant).filter(
        models.Merchant.name.ilike(f"%{q}%")
    ).all()
    result = []
    for merchant in merchants:
        merchant_dict = {
            "id": merchant.id,
            "name": merchant.name,
            "category_id": merchant.category_id,
            "category_name": merchant.category.name if merchant.category else None
        }
        result.append(schemas.Merchant(**merchant_dict))
    return result


@router.post("", response_model=schemas.Merchant, status_code=201)
def create_merchant(merchant: schemas.MerchantCreate, db: Session = Depends(get_db)):
    """Create a merchant with category mapping."""
    # Check if merchant with same name already exists
    existing = db.query(models.Merchant).filter(
        models.Merchant.name == merchant.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Merchant with this name already exists")

    # Check if category exists
    category = db.query(models.Category).filter(
        models.Category.id == merchant.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_merchant = models.Merchant(**merchant.dict())
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)

    return schemas.Merchant(
        id=db_merchant.id,
        name=db_merchant.name,
        category_id=db_merchant.category_id,
        category_name=db_merchant.category.name if db_merchant.category else None
    )


@router.put("/{merchant_id}", response_model=schemas.Merchant)
def update_merchant(
    merchant_id: int,
    merchant_update: schemas.MerchantUpdate,
    db: Session = Depends(get_db)
):
    """Update a merchant."""
    db_merchant = db.query(models.Merchant).filter(
        models.Merchant.id == merchant_id
    ).first()
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    update_data = merchant_update.dict(exclude_unset=True)

    # If updating category, verify it exists
    if "category_id" in update_data:
        category = db.query(models.Category).filter(
            models.Category.id == update_data["category_id"]
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    for field, value in update_data.items():
        setattr(db_merchant, field, value)

    db.commit()
    db.refresh(db_merchant)

    return schemas.Merchant(
        id=db_merchant.id,
        name=db_merchant.name,
        category_id=db_merchant.category_id,
        category_name=db_merchant.category.name if db_merchant.category else None
    )


@router.delete("/{merchant_id}", status_code=204)
def delete_merchant(merchant_id: int, db: Session = Depends(get_db)):
    """Delete a merchant."""
    db_merchant = db.query(models.Merchant).filter(
        models.Merchant.id == merchant_id
    ).first()
    if not db_merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    db.delete(db_merchant)
    db.commit()
    return None
