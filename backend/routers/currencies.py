from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/api/currencies", tags=["currencies"])


@router.get("", response_model=List[schemas.PointCurrency])
def list_currencies(db: Session = Depends(get_db)):
    """List all point currencies with CPP values."""
    return db.query(models.PointCurrency).all()


@router.post("", response_model=schemas.PointCurrency, status_code=201)
def create_currency(currency: schemas.PointCurrencyCreate, db: Session = Depends(get_db)):
    """Create a new point currency."""
    # Check if currency with same name already exists
    existing = db.query(models.PointCurrency).filter(
        models.PointCurrency.name == currency.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Currency with this name already exists")

    db_currency = models.PointCurrency(**currency.dict())
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)
    return db_currency


@router.put("/{currency_id}", response_model=schemas.PointCurrency)
def update_currency(
    currency_id: int,
    currency_update: schemas.PointCurrencyUpdate,
    db: Session = Depends(get_db)
):
    """Update a point currency (primarily for CPP changes)."""
    db_currency = db.query(models.PointCurrency).filter(
        models.PointCurrency.id == currency_id
    ).first()
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    update_data = currency_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_currency, field, value)

    db.commit()
    db.refresh(db_currency)
    return db_currency


@router.delete("/{currency_id}", status_code=204)
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    """Delete a point currency."""
    db_currency = db.query(models.PointCurrency).filter(
        models.PointCurrency.id == currency_id
    ).first()
    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    # Check if any cards use this currency
    cards_count = db.query(models.Card).filter(
        models.Card.point_currency_id == currency_id
    ).count()
    if cards_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete currency: {cards_count} card(s) are using it"
        )

    db.delete(db_currency)
    db.commit()
    return None
