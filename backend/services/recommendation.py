from sqlalchemy.orm import Session
from backend import models, schemas
from typing import List, Optional


def get_recommendations(
    db: Session,
    category_id: int
) -> Optional[schemas.RecommendationResponse]:
    """
    Get ranked card recommendations for a given category.

    Args:
        db: Database session
        category_id: Category ID to get recommendations for

    Returns:
        RecommendationResponse with ranked cards or None if category not found
    """
    # Get category
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        return None

    # Get all active cards
    active_cards = db.query(models.Card).filter(models.Card.is_active == True).all()

    recommendations = []

    for card in active_cards:
        # Get point currency
        cpp = card.point_currency.cpp_value if card.point_currency else 1.0
        currency_name = card.point_currency.name if card.point_currency else "Unknown"

        # Check for category-specific reward
        category_reward = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == card.id,
            models.CategoryReward.category_id == category_id
        ).first()

        reward_rate = card.default_reward_rate
        cap_status = None
        cap_warning = False

        if category_reward:
            # Check if cap is exceeded
            if category_reward.annual_cap is not None and category_reward.current_spend >= category_reward.annual_cap:
                # Cap exceeded, use default rate
                reward_rate = card.default_reward_rate
                cap_status = f"${category_reward.current_spend:,.0f} of ${category_reward.annual_cap:,.0f} used (CAP EXCEEDED)"
                cap_warning = True
            else:
                # Use category reward rate
                reward_rate = category_reward.reward_rate
                if category_reward.annual_cap is not None:
                    cap_status = f"${category_reward.current_spend:,.0f} of ${category_reward.annual_cap:,.0f} used"
                    # Warning if over 80% of cap used
                    if category_reward.current_spend / category_reward.annual_cap >= 0.8:
                        cap_warning = True

        # Calculate effective value
        effective_value = reward_rate * cpp

        recommendations.append({
            "card_name": card.name,
            "effective_value": effective_value,
            "reward_rate": reward_rate,
            "currency": currency_name,
            "cpp": cpp,
            "cap_status": cap_status,
            "cap_warning": cap_warning
        })

    # Sort by effective value (descending)
    recommendations.sort(key=lambda x: x["effective_value"], reverse=True)

    # Add rank
    for i, rec in enumerate(recommendations, 1):
        rec["rank"] = i

    return schemas.RecommendationResponse(
        category=category.name,
        recommendations=[schemas.RecommendationCard(**rec) for rec in recommendations]
    )


def get_recommendations_by_merchant(
    db: Session,
    merchant_name: str
) -> Optional[schemas.RecommendationResponse]:
    """
    Get ranked card recommendations for a merchant (resolves to category).

    Args:
        db: Database session
        merchant_name: Merchant name to look up

    Returns:
        RecommendationResponse with ranked cards or None if merchant not found
    """
    # Look up merchant
    merchant = db.query(models.Merchant).filter(
        models.Merchant.name.ilike(f"%{merchant_name}%")
    ).first()

    if not merchant:
        return None

    return get_recommendations(db, merchant.category_id)


def get_simple_recommendation(
    db: Session,
    category_id: int
) -> Optional[schemas.SimpleRecommendationResponse]:
    """
    Get the top recommended card for a category (simple view).

    Args:
        db: Database session
        category_id: Category ID to get recommendation for

    Returns:
        SimpleRecommendationResponse with top card or None if category not found
    """
    recommendations = get_recommendations(db, category_id)

    if not recommendations or not recommendations.recommendations:
        return None

    top_card = recommendations.recommendations[0]

    details = f"{top_card.reward_rate}% {top_card.currency} (worth {top_card.effective_value:.1f}¢ per $)"
    if top_card.cap_status:
        details += f" - {top_card.cap_status}"

    return schemas.SimpleRecommendationResponse(
        category=recommendations.category,
        card_name=top_card.card_name,
        effective_value=top_card.effective_value,
        details=details
    )
