from backend.database import SessionLocal, engine, Base
from backend import models
from datetime import datetime, date


def seed_categories():
    """Seed initial categories."""
    db = SessionLocal()

    categories = [
        {"name": "Gas - Pump", "description": "Automated fuel dispensers"},
        {"name": "Gas - Convenience Store", "description": "In-store purchases at gas stations"},
        {"name": "Groceries", "description": "Supermarkets, excludes Walmart/Target"},
        {"name": "Wholesale Clubs", "description": "Costco, Sam's Club, BJ's"},
        {"name": "Dining - Restaurants", "description": "Sit-down restaurants"},
        {"name": "Dining - Fast Food", "description": "Quick service restaurants"},
        {"name": "Travel - Airlines", "description": "Airline tickets and fees"},
        {"name": "Travel - Hotels", "description": "Hotel accommodations"},
        {"name": "Travel - Car Rental", "description": "Car rental services"},
        {"name": "Travel - Other", "description": "Other travel expenses"},
        {"name": "Streaming Services", "description": "Netflix, Spotify, etc."},
        {"name": "Online Shopping", "description": "Amazon, eBay, etc."},
        {"name": "Drugstores/Pharmacies", "description": "CVS, Walgreens, etc."},
        {"name": "Home Improvement", "description": "Home Depot, Lowe's, etc."},
        {"name": "Utilities", "description": "Electric, gas, water, internet"},
        {"name": "Transit", "description": "Rideshare, public transit, parking"},
        {"name": "Entertainment", "description": "Movies, concerts, events"},
        {"name": "Other/Default", "description": "Everything else"},
    ]

    for cat_data in categories:
        existing = db.query(models.Category).filter(
            models.Category.name == cat_data["name"]
        ).first()
        if not existing:
            category = models.Category(**cat_data)
            db.add(category)

    db.commit()
    print("✓ Categories seeded")
    db.close()


def seed_sample_data():
    """Seed sample point currencies and cards for demonstration."""
    db = SessionLocal()

    # Seed point currencies
    currencies = [
        {"name": "Cashback", "cpp_value": 1.0},
        {"name": "Chase UR", "cpp_value": 1.8},
        {"name": "Amex MR", "cpp_value": 1.5},
        {"name": "Citi TYP", "cpp_value": 1.5},
        {"name": "Capital One Miles", "cpp_value": 1.4},
    ]

    for curr_data in currencies:
        existing = db.query(models.PointCurrency).filter(
            models.PointCurrency.name == curr_data["name"]
        ).first()
        if not existing:
            currency = models.PointCurrency(**curr_data)
            db.add(currency)

    db.commit()
    print("✓ Point currencies seeded")

    # Seed sample cards
    cashback_id = db.query(models.PointCurrency).filter(
        models.PointCurrency.name == "Cashback"
    ).first().id
    chase_ur_id = db.query(models.PointCurrency).filter(
        models.PointCurrency.name == "Chase UR"
    ).first().id

    cards = [
        {
            "name": "Chase Freedom Flex",
            "issuer": "Chase",
            "last_four": "1234",
            "point_currency_id": chase_ur_id,
            "default_reward_rate": 1.0,
            "is_active": True,
            "notes": "5% rotating categories"
        },
        {
            "name": "Amex Blue Cash Preferred",
            "issuer": "American Express",
            "last_four": "5678",
            "point_currency_id": cashback_id,
            "default_reward_rate": 1.0,
            "is_active": True,
            "notes": "6% groceries and streaming"
        },
        {
            "name": "Citi Custom Cash",
            "issuer": "Citi",
            "last_four": "9012",
            "point_currency_id": cashback_id,
            "default_reward_rate": 1.0,
            "is_active": True,
            "notes": "5% on top category up to $500/month"
        },
        {
            "name": "Chase Sapphire Preferred",
            "issuer": "Chase",
            "last_four": "3456",
            "point_currency_id": chase_ur_id,
            "default_reward_rate": 1.0,
            "is_active": True,
            "notes": "2x dining and travel"
        },
    ]

    for card_data in cards:
        existing = db.query(models.Card).filter(
            models.Card.name == card_data["name"]
        ).first()
        if not existing:
            card = models.Card(**card_data)
            db.add(card)

    db.commit()
    print("✓ Sample cards seeded")

    # Seed category rewards
    amex_bcp = db.query(models.Card).filter(
        models.Card.name == "Amex Blue Cash Preferred"
    ).first()
    chase_ff = db.query(models.Card).filter(
        models.Card.name == "Chase Freedom Flex"
    ).first()
    chase_csp = db.query(models.Card).filter(
        models.Card.name == "Chase Sapphire Preferred"
    ).first()

    groceries = db.query(models.Category).filter(
        models.Category.name == "Groceries"
    ).first()
    streaming = db.query(models.Category).filter(
        models.Category.name == "Streaming Services"
    ).first()
    gas_pump = db.query(models.Category).filter(
        models.Category.name == "Gas - Pump"
    ).first()
    dining = db.query(models.Category).filter(
        models.Category.name == "Dining - Restaurants"
    ).first()
    drugstores = db.query(models.Category).filter(
        models.Category.name == "Drugstores/Pharmacies"
    ).first()

    if amex_bcp and groceries:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == amex_bcp.id,
            models.CategoryReward.category_id == groceries.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=amex_bcp.id,
                category_id=groceries.id,
                reward_rate=6.0,
                annual_cap=6000.0,
                current_spend=2450.0,
                cap_reset_date=date(2026, 12, 31)
            )
            db.add(reward)

    if amex_bcp and streaming:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == amex_bcp.id,
            models.CategoryReward.category_id == streaming.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=amex_bcp.id,
                category_id=streaming.id,
                reward_rate=6.0,
                annual_cap=None,
                current_spend=0.0
            )
            db.add(reward)

    if amex_bcp and gas_pump:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == amex_bcp.id,
            models.CategoryReward.category_id == gas_pump.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=amex_bcp.id,
                category_id=gas_pump.id,
                reward_rate=3.0,
                annual_cap=None,
                current_spend=0.0
            )
            db.add(reward)

    if chase_ff and dining:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == chase_ff.id,
            models.CategoryReward.category_id == dining.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=chase_ff.id,
                category_id=dining.id,
                reward_rate=3.0,
                annual_cap=None,
                current_spend=0.0
            )
            db.add(reward)

    if chase_ff and drugstores:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == chase_ff.id,
            models.CategoryReward.category_id == drugstores.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=chase_ff.id,
                category_id=drugstores.id,
                reward_rate=3.0,
                annual_cap=None,
                current_spend=0.0
            )
            db.add(reward)

    if chase_csp and dining:
        existing = db.query(models.CategoryReward).filter(
            models.CategoryReward.card_id == chase_csp.id,
            models.CategoryReward.category_id == dining.id
        ).first()
        if not existing:
            reward = models.CategoryReward(
                card_id=chase_csp.id,
                category_id=dining.id,
                reward_rate=2.0,
                annual_cap=None,
                current_spend=0.0
            )
            db.add(reward)

    db.commit()
    print("✓ Category rewards seeded")
    db.close()


def init_db():
    """Initialize database with tables and seed data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")

    # Seed data
    seed_categories()
    seed_sample_data()

    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    init_db()
