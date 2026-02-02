from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List


# Point Currency Schemas
class PointCurrencyBase(BaseModel):
    name: str
    cpp_value: float = 1.0


class PointCurrencyCreate(PointCurrencyBase):
    pass


class PointCurrencyUpdate(BaseModel):
    name: Optional[str] = None
    cpp_value: Optional[float] = None


class PointCurrency(PointCurrencyBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True


# Category Reward Schemas
class CategoryRewardBase(BaseModel):
    category_id: int
    reward_rate: float
    annual_cap: Optional[float] = None
    current_spend: float = 0.0
    cap_reset_date: Optional[date] = None


class CategoryRewardCreate(CategoryRewardBase):
    pass


class CategoryRewardUpdate(BaseModel):
    reward_rate: Optional[float] = None
    annual_cap: Optional[float] = None
    current_spend: Optional[float] = None
    cap_reset_date: Optional[date] = None


class CategoryReward(CategoryRewardBase):
    id: int
    card_id: int
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


# Card Schemas
class CardBase(BaseModel):
    name: str
    issuer: str
    last_four: Optional[str] = None
    point_currency_id: int
    default_reward_rate: float = 1.0
    is_active: bool = True
    notes: Optional[str] = None


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    last_four: Optional[str] = None
    point_currency_id: Optional[int] = None
    default_reward_rate: Optional[float] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class Card(CardBase):
    id: int
    created_at: datetime
    point_currency_name: Optional[str] = None
    category_rewards: List[CategoryReward] = []

    class Config:
        from_attributes = True


# Merchant Schemas
class MerchantBase(BaseModel):
    name: str
    category_id: int


class MerchantCreate(MerchantBase):
    pass


class MerchantUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None


class Merchant(MerchantBase):
    id: int
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


# Recommendation Schemas
class RecommendationCard(BaseModel):
    rank: int
    card_name: str
    effective_value: float
    reward_rate: float
    currency: str
    cpp: float
    cap_status: Optional[str] = None
    cap_warning: bool = False


class RecommendationResponse(BaseModel):
    category: str
    recommendations: List[RecommendationCard]


class SimpleRecommendationResponse(BaseModel):
    category: str
    card_name: str
    effective_value: float
    details: Optional[str] = None
