from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend import models, schemas
from backend.database import get_db

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.get("", response_model=List[schemas.Card])
def list_cards(db: Session = Depends(get_db)):
    """List all cards with their category rewards."""
    cards = db.query(models.Card).all()
    result = []
    for card in cards:
        rewards = []
        for reward in card.category_rewards:
            reward_dict = {
                "id": reward.id,
                "card_id": reward.card_id,
                "category_id": reward.category_id,
                "reward_rate": reward.reward_rate,
                "annual_cap": reward.annual_cap,
                "current_spend": reward.current_spend,
                "cap_reset_date": reward.cap_reset_date,
                "category_name": reward.category.name if reward.category else None
            }
            rewards.append(schemas.CategoryReward(**reward_dict))

        card_dict = {
            "id": card.id,
            "name": card.name,
            "issuer": card.issuer,
            "last_four": card.last_four,
            "point_currency_id": card.point_currency_id,
            "default_reward_rate": card.default_reward_rate,
            "is_active": card.is_active,
            "notes": card.notes,
            "created_at": card.created_at,
            "point_currency_name": card.point_currency.name if card.point_currency else None,
            "category_rewards": rewards
        }
        result.append(schemas.Card(**card_dict))
    return result


@router.post("", response_model=schemas.Card, status_code=201)
def create_card(card: schemas.CardCreate, db: Session = Depends(get_db)):
    """Create a new card."""
    # Check if point currency exists
    currency = db.query(models.PointCurrency).filter(
        models.PointCurrency.id == card.point_currency_id
    ).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Point currency not found")

    db_card = models.Card(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    return schemas.Card(
        id=db_card.id,
        name=db_card.name,
        issuer=db_card.issuer,
        last_four=db_card.last_four,
        point_currency_id=db_card.point_currency_id,
        default_reward_rate=db_card.default_reward_rate,
        is_active=db_card.is_active,
        notes=db_card.notes,
        created_at=db_card.created_at,
        point_currency_name=db_card.point_currency.name if db_card.point_currency else None,
        category_rewards=[]
    )


@router.get("/{card_id}", response_model=schemas.Card)
def get_card(card_id: int, db: Session = Depends(get_db)):
    """Get a specific card with its rewards."""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    rewards = []
    for reward in card.category_rewards:
        reward_dict = {
            "id": reward.id,
            "card_id": reward.card_id,
            "category_id": reward.category_id,
            "reward_rate": reward.reward_rate,
            "annual_cap": reward.annual_cap,
            "current_spend": reward.current_spend,
            "cap_reset_date": reward.cap_reset_date,
            "category_name": reward.category.name if reward.category else None
        }
        rewards.append(schemas.CategoryReward(**reward_dict))

    return schemas.Card(
        id=card.id,
        name=card.name,
        issuer=card.issuer,
        last_four=card.last_four,
        point_currency_id=card.point_currency_id,
        default_reward_rate=card.default_reward_rate,
        is_active=card.is_active,
        notes=card.notes,
        created_at=card.created_at,
        point_currency_name=card.point_currency.name if card.point_currency else None,
        category_rewards=rewards
    )


@router.put("/{card_id}", response_model=schemas.Card)
def update_card(
    card_id: int,
    card_update: schemas.CardUpdate,
    db: Session = Depends(get_db)
):
    """Update card details."""
    db_card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")

    update_data = card_update.dict(exclude_unset=True)

    # If updating point currency, verify it exists
    if "point_currency_id" in update_data:
        currency = db.query(models.PointCurrency).filter(
            models.PointCurrency.id == update_data["point_currency_id"]
        ).first()
        if not currency:
            raise HTTPException(status_code=404, detail="Point currency not found")

    for field, value in update_data.items():
        setattr(db_card, field, value)

    db.commit()
    db.refresh(db_card)

    rewards = []
    for reward in db_card.category_rewards:
        reward_dict = {
            "id": reward.id,
            "card_id": reward.card_id,
            "category_id": reward.category_id,
            "reward_rate": reward.reward_rate,
            "annual_cap": reward.annual_cap,
            "current_spend": reward.current_spend,
            "cap_reset_date": reward.cap_reset_date,
            "category_name": reward.category.name if reward.category else None
        }
        rewards.append(schemas.CategoryReward(**reward_dict))

    return schemas.Card(
        id=db_card.id,
        name=db_card.name,
        issuer=db_card.issuer,
        last_four=db_card.last_four,
        point_currency_id=db_card.point_currency_id,
        default_reward_rate=db_card.default_reward_rate,
        is_active=db_card.is_active,
        notes=db_card.notes,
        created_at=db_card.created_at,
        point_currency_name=db_card.point_currency.name if db_card.point_currency else None,
        category_rewards=rewards
    )


@router.delete("/{card_id}", status_code=204)
def delete_card(card_id: int, db: Session = Depends(get_db)):
    """Delete a card (hard delete)."""
    db_card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")

    db.delete(db_card)
    db.commit()
    return None


@router.get("/{card_id}/rewards", response_model=List[schemas.CategoryReward])
def get_card_rewards(card_id: int, db: Session = Depends(get_db)):
    """Get all category rewards for a card."""
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    result = []
    for reward in card.category_rewards:
        reward_dict = {
            "id": reward.id,
            "card_id": reward.card_id,
            "category_id": reward.category_id,
            "reward_rate": reward.reward_rate,
            "annual_cap": reward.annual_cap,
            "current_spend": reward.current_spend,
            "cap_reset_date": reward.cap_reset_date,
            "category_name": reward.category.name if reward.category else None
        }
        result.append(schemas.CategoryReward(**reward_dict))
    return result


@router.post("/{card_id}/rewards", response_model=schemas.CategoryReward, status_code=201)
def add_card_reward(
    card_id: int,
    reward: schemas.CategoryRewardCreate,
    db: Session = Depends(get_db)
):
    """Add a category reward to a card."""
    # Check if card exists
    card = db.query(models.Card).filter(models.Card.id == card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Check if category exists
    category = db.query(models.Category).filter(
        models.Category.id == reward.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check if reward already exists for this card/category
    existing = db.query(models.CategoryReward).filter(
        models.CategoryReward.card_id == card_id,
        models.CategoryReward.category_id == reward.category_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Reward for this card and category already exists"
        )

    db_reward = models.CategoryReward(card_id=card_id, **reward.dict())
    db.add(db_reward)
    db.commit()
    db.refresh(db_reward)

    return schemas.CategoryReward(
        id=db_reward.id,
        card_id=db_reward.card_id,
        category_id=db_reward.category_id,
        reward_rate=db_reward.reward_rate,
        annual_cap=db_reward.annual_cap,
        current_spend=db_reward.current_spend,
        cap_reset_date=db_reward.cap_reset_date,
        category_name=db_reward.category.name if db_reward.category else None
    )


@router.put("/{card_id}/rewards/{category_id}", response_model=schemas.CategoryReward)
def update_card_reward(
    card_id: int,
    category_id: int,
    reward_update: schemas.CategoryRewardUpdate,
    db: Session = Depends(get_db)
):
    """Update a reward rate or cap for a card's category."""
    db_reward = db.query(models.CategoryReward).filter(
        models.CategoryReward.card_id == card_id,
        models.CategoryReward.category_id == category_id
    ).first()
    if not db_reward:
        raise HTTPException(status_code=404, detail="Category reward not found")

    update_data = reward_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reward, field, value)

    db.commit()
    db.refresh(db_reward)

    return schemas.CategoryReward(
        id=db_reward.id,
        card_id=db_reward.card_id,
        category_id=db_reward.category_id,
        reward_rate=db_reward.reward_rate,
        annual_cap=db_reward.annual_cap,
        current_spend=db_reward.current_spend,
        cap_reset_date=db_reward.cap_reset_date,
        category_name=db_reward.category.name if db_reward.category else None
    )


@router.delete("/{card_id}/rewards/{category_id}", status_code=204)
def delete_card_reward(card_id: int, category_id: int, db: Session = Depends(get_db)):
    """Remove a category reward from a card."""
    db_reward = db.query(models.CategoryReward).filter(
        models.CategoryReward.card_id == card_id,
        models.CategoryReward.category_id == category_id
    ).first()
    if not db_reward:
        raise HTTPException(status_code=404, detail="Category reward not found")

    db.delete(db_reward)
    db.commit()
    return None
