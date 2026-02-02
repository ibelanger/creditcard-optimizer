from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database import Base


class PointCurrency(Base):
    __tablename__ = "point_currencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    cpp_value = Column(Float, nullable=False, default=1.0)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cards = relationship("Card", back_populates="point_currency")


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    last_four = Column(String, nullable=True)
    point_currency_id = Column(Integer, ForeignKey("point_currencies.id"), nullable=False)
    default_reward_rate = Column(Float, nullable=False, default=1.0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    notes = Column(String, nullable=True)

    # Relationships
    point_currency = relationship("PointCurrency", back_populates="cards")
    category_rewards = relationship("CategoryReward", back_populates="card", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    # Relationships
    category_rewards = relationship("CategoryReward", back_populates="category")
    merchants = relationship("Merchant", back_populates="category")


class CategoryReward(Base):
    __tablename__ = "category_rewards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    reward_rate = Column(Float, nullable=False)
    annual_cap = Column(Float, nullable=True)
    current_spend = Column(Float, nullable=False, default=0.0)
    cap_reset_date = Column(Date, nullable=True)

    # Unique constraint
    __table_args__ = (UniqueConstraint('card_id', 'category_id', name='_card_category_uc'),)

    # Relationships
    card = relationship("Card", back_populates="category_rewards")
    category = relationship("Category", back_populates="category_rewards")


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # Relationships
    category = relationship("Category", back_populates="merchants")
