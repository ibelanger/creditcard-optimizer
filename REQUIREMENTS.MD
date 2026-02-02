# Card Optimizer - Requirements Document

## Project Overview

A self-hosted personal credit card optimization platform that helps users select the optimal credit card for any purchase based on reward rates, point valuations, spend caps, and temporary promotions.

### Primary Goals
1. **Phase 1:** "Which card to use" engine - query by merchant/category, get ranked card recommendations
2. **Phase 2:** Promotion/deal tracker (temporary offers that override defaults)
3. **Phase 3:** Spend cap monitor (track progress toward tiered reward thresholds)
4. **Phase 4:** Churning tracker (5/24 status, bonus eligibility, cancellation timing)

**This document covers Phase 1 only.**

---

## Technical Stack

### Backend
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Database:** SQLite (single file, easy backup)
- **ORM:** SQLAlchemy or raw SQL (developer preference)

### Frontend
- **Framework:** React (lightweight, PWA-capable)
- **Styling:** Tailwind CSS or minimal custom CSS
- **PWA:** Installable on Android, works in desktop browser

### Deployment
- **Container:** Docker (single container or docker-compose)
- **Host:** Synology DS224+ via Container Manager
- **External Access:** Cloudflare Tunnel (free tier, no domain required)

---

## Data Model

### Table: `point_currencies`
Stores point/mile programs and their cents-per-point (CPP) valuations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | TEXT | NOT NULL, UNIQUE | e.g., "Chase UR", "Amex MR", "Cashback" |
| cpp_value | REAL | NOT NULL, DEFAULT 1.0 | Cents per point valuation |
| updated_at | TIMESTAMP | NOT NULL | Last valuation update |

**Notes:**
- "Cashback" should have cpp_value = 1.0 (1% = 1 cent per dollar)
- User manually updates CPP values periodically

### Table: `cards`
Stores credit cards in the user's wallet.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | TEXT | NOT NULL | e.g., "Chase Freedom Flex", "Amex Blue Cash Preferred" |
| issuer | TEXT | NOT NULL | e.g., "Chase", "Amex", "Citi" |
| last_four | TEXT | NULLABLE | Last 4 digits for identification |
| point_currency_id | INTEGER | FK → point_currencies.id | Which points this card earns |
| default_reward_rate | REAL | NOT NULL, DEFAULT 1.0 | Catch-all reward rate (percentage) |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether card is in active use |
| created_at | TIMESTAMP | NOT NULL | When card was added |
| notes | TEXT | NULLABLE | User notes |

### Table: `categories`
Reference table of spending categories (based on merchant category codes).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | TEXT | NOT NULL, UNIQUE | e.g., "Gas - Pump", "Gas - Store", "Groceries" |
| description | TEXT | NULLABLE | Clarification of what qualifies |

**Seed Data (initial categories):**
- Gas - Pump (automated fuel dispensers)
- Gas - Convenience Store (in-store purchases at gas stations)
- Groceries (supermarkets, excludes Walmart/Target)
- Wholesale Clubs (Costco, Sam's Club, BJ's)
- Dining - Restaurants
- Dining - Fast Food
- Travel - Airlines
- Travel - Hotels
- Travel - Car Rental
- Travel - Other
- Streaming Services
- Online Shopping
- Drugstores/Pharmacies
- Home Improvement
- Utilities
- Transit (rideshare, public transit, parking)
- Entertainment
- Other/Default

### Table: `category_rewards`
Maps cards to their reward rates per category, including spend caps.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| card_id | INTEGER | FK → cards.id, NOT NULL | Which card |
| category_id | INTEGER | FK → categories.id, NOT NULL | Which category |
| reward_rate | REAL | NOT NULL | Reward percentage (e.g., 6.0 for 6%) |
| annual_cap | REAL | NULLABLE | Annual spend cap in dollars (NULL = unlimited) |
| current_spend | REAL | NOT NULL, DEFAULT 0.0 | Tracked spend toward cap (user updates manually or via import) |
| cap_reset_date | DATE | NULLABLE | When the cap resets (for annual caps) |

**Unique constraint:** (card_id, category_id) - one reward rate per card per category

### Table: `merchants`
Optional lookup table for quick merchant → category mapping.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, AUTO | Unique identifier |
| name | TEXT | NOT NULL, UNIQUE | e.g., "Costco Gas", "Circle K", "Whole Foods" |
| category_id | INTEGER | FK → categories.id | Default category for this merchant |

**Notes:**
- User-populated over time
- When user queries a merchant, system suggests the mapped category
- User can override at query time

---

## API Endpoints

### Point Currencies
- `GET /api/currencies` - List all point currencies with CPP values
- `POST /api/currencies` - Create new currency
- `PUT /api/currencies/{id}` - Update currency (primarily for CPP changes)
- `DELETE /api/currencies/{id}` - Delete currency (cascade warning)

### Cards
- `GET /api/cards` - List all cards (with their category rewards)
- `POST /api/cards` - Create new card
- `PUT /api/cards/{id}` - Update card details
- `DELETE /api/cards/{id}` - Soft delete (set is_active = false) or hard delete
- `GET /api/cards/{id}/rewards` - Get all category rewards for a card
- `POST /api/cards/{id}/rewards` - Add category reward to card
- `PUT /api/cards/{id}/rewards/{category_id}` - Update reward rate or cap
- `DELETE /api/cards/{id}/rewards/{category_id}` - Remove category reward

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create new category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category (cascade warning)

### Merchants
- `GET /api/merchants` - List all merchants
- `GET /api/merchants/search?q={query}` - Search merchants by name
- `POST /api/merchants` - Create merchant with category mapping
- `PUT /api/merchants/{id}` - Update merchant
- `DELETE /api/merchants/{id}` - Delete merchant

### Query (Core Feature)
- `GET /api/recommend?category_id={id}` - Get ranked cards for a category
- `GET /api/recommend?merchant={name}` - Get ranked cards for a merchant (resolves to category)
- `GET /api/recommend/simple?category_id={id}` - Returns only the top card (for wife's view)

---

## Recommendation Logic

### Input
- Category ID (directly selected) OR merchant name (resolved to category)

### Process
1. If merchant provided, look up category from `merchants` table
2. For each active card:
   a. Check if card has a specific reward for this category in `category_rewards`
   b. If yes, check if spend cap exists and if `current_spend >= annual_cap`
      - If cap exceeded, use `default_reward_rate` instead
      - If cap not exceeded, use category `reward_rate`
   c. If no specific reward, use `default_reward_rate`
   d. Look up `cpp_value` from card's `point_currency`
   e. Calculate effective value: `reward_rate × cpp_value`
3. Sort cards by effective value (descending)
4. Return ranked list with:
   - Card name
   - Effective value (cents per dollar)
   - Reward rate
   - Point currency name
   - Cap status (if applicable): "($X of $Y cap used)"

### Example Response
```json
{
  "category": "Groceries",
  "recommendations": [
    {
      "rank": 1,
      "card_name": "Amex Blue Cash Preferred",
      "effective_value": 6.0,
      "reward_rate": 6.0,
      "currency": "Cashback",
      "cpp": 1.0,
      "cap_status": "$2,450 of $6,000 used",
      "cap_warning": false
    },
    {
      "rank": 2,
      "card_name": "Chase Freedom Flex",
      "effective_value": 5.4,
      "reward_rate": 3.0,
      "currency": "Chase UR",
      "cpp": 1.8,
      "cap_status": null,
      "cap_warning": false
    }
  ]
}
```

---

## Frontend Views

### Admin View (Full Access)
Accessible to primary user. Includes:

1. **Dashboard**
   - Quick query interface (search box for merchant/category)
   - Recent queries
   - Cards approaching spend caps (warnings)

2. **Cards Management**
   - List all cards with summary info
   - Add/edit/remove cards
   - Per-card: edit category rewards, caps, current spend

3. **Categories Management**
   - List/add/edit categories

4. **Merchants Management**
   - List/add/edit merchant → category mappings

5. **Settings**
   - Point currency CPP values
   - Data export/backup

### Simple View (Wife's View)
Read-only, optimized for quick lookups:

1. **Single search box** - type merchant or select category
2. **Single result** - "Use [Card Name]" with large, clear display
3. **Optional:** tap to see why (effective value breakdown)

**Implementation options:**
- Separate route (`/simple`)
- URL parameter (`/?mode=simple`)
- PWA can be installed twice with different start URLs

---

## Docker Configuration

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  card-optimizer:
    build: .
    container_name: card-optimizer
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data  # SQLite database persistence
    restart: unless-stopped
    environment:
      - DATABASE_URL=sqlite:///data/cards.db
```

### Synology Deployment Notes
- Use Container Manager to import docker-compose
- Map `/app/data` to a persistent volume on the NAS
- Set up Cloudflare Tunnel via `cloudflared` container or Synology package

---

## Project Structure

```
card-optimizer/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── database.py             # SQLite connection and session management
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── routers/
│   │   ├── cards.py
│   │   ├── categories.py
│   │   ├── currencies.py
│   │   ├── merchants.py
│   │   └── recommend.py
│   ├── services/
│   │   └── recommendation.py   # Core ranking logic
│   └── seed_data.py            # Initial categories
├── frontend/
│   ├── public/
│   │   └── manifest.json       # PWA manifest
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Cards.jsx
│   │   │   ├── Categories.jsx
│   │   │   ├── Merchants.jsx
│   │   │   ├── Settings.jsx
│   │   │   └── SimpleView.jsx
│   │   └── api/
│   │       └── client.js       # API wrapper
│   └── package.json
├── data/                       # SQLite database (gitignored, volume mounted)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Phase 1 Acceptance Criteria

The system is complete when:

1. [ ] User can add/edit/remove credit cards with point currency assignment
2. [ ] User can set CPP values for point currencies
3. [ ] User can assign category reward rates to cards (with optional caps)
4. [ ] User can manually update current spend toward caps
5. [ ] User can add merchants with category mappings
6. [ ] User can query by category and receive ranked card list
7. [ ] User can query by merchant name (resolves to category)
8. [ ] Ranking correctly calculates `reward_rate × cpp_value`
9. [ ] Ranking correctly handles spend caps (falls back to default when exceeded)
10. [ ] Simple view returns only the top recommended card
11. [ ] PWA is installable on Android
12. [ ] App is accessible externally via Cloudflare Tunnel

---

## Future Phases (Out of Scope for Phase 1)

### Phase 2: Promotion Tracker
- Temporary deals that override default recommendations
- Deal expiration dates
- "Redeem once" vs "ongoing" deal types

### Phase 3: Spend Cap Monitor
- Dashboard showing progress toward all caps
- Alerts when approaching cap threshold (e.g., 80%)
- Historical spend tracking

### Phase 4: Churning Tracker
- 5/24 count monitoring
- Bonus eligibility dates
- Cancellation timing recommendations
- "Time since last bonus" per card family

### Phase 5: Transaction Import (Optional)
- Rocket Money or SoFi API integration (if secure APIs available)
- Automatic spend tracking
- "Wrong card used" alerts

---

## Open Questions / Decisions for Development

1. **Authentication:** None for Phase 1 (trusted network via Tunnel), or basic auth/PIN?
2. **Multi-user:** Single wallet (shared), or separate user accounts?
3. **Backup strategy:** Manual SQLite file copy, or automated export endpoint?

---

## Appendix: Sample Seed Data

### Point Currencies
| Name | CPP Value |
|------|-----------|
| Cashback | 1.0 |
| Chase UR | 1.8 |
| Amex MR | 1.5 |
| Citi TYP | 1.5 |
| Capital One Miles | 1.4 |

### Example Cards
| Card | Issuer | Currency | Default Rate |
|------|--------|----------|--------------|
| Chase Freedom Flex | Chase | Chase UR | 1% |
| Amex Blue Cash Preferred | Amex | Cashback | 1% |
| Citi Custom Cash | Citi | Cashback | 1% |
| Chase Sapphire Preferred | Chase | Chase UR | 1% |

### Example Category Rewards
| Card | Category | Rate | Cap |
|------|----------|------|-----|
| Amex Blue Cash Preferred | Groceries | 6% | $6,000/yr |
| Amex Blue Cash Preferred | Streaming | 6% | NULL |
| Amex Blue Cash Preferred | Gas - Pump | 3% | NULL |
| Chase Freedom Flex | Dining | 3% | NULL |
| Chase Freedom Flex | Drugstores | 3% | NULL |
| Citi Custom Cash | (user sets one) | 5% | $500/mo |
