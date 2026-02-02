# Card Optimizer

A self-hosted personal credit card optimization platform that helps you select the optimal credit card for any purchase based on reward rates, point valuations, spend caps, and categories.

## Features (Phase 1)

- **Smart Recommendations**: Get ranked card recommendations based on effective value (reward rate × CPP)
- **Category-Based Rewards**: Track different reward rates for different spending categories
- **Spend Cap Tracking**: Monitor your progress toward annual spending caps
- **Point Currency Valuation**: Set and update your cents-per-point (CPP) values
- **Merchant Mapping**: Map merchants to categories for quick lookups
- **Simple View**: Minimalist interface for quick "which card to use" queries
- **PWA Support**: Install on Android as a progressive web app

## Tech Stack

### Backend
- **Python 3.11+** with FastAPI
- **SQLite** database with SQLAlchemy ORM
- **Uvicorn** ASGI server

### Frontend
- **React 18** with Vite
- **React Router** for navigation
- **Axios** for API calls
- Minimal CSS styling

### Deployment
- **Docker** with docker-compose
- Designed for **Synology NAS** deployment
- **Cloudflare Tunnel** ready for external access

## Quick Start

### Option 1: Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd creditcard-optimizer
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

3. Access the application:
   - Frontend: http://localhost:8000
   - API docs: http://localhost:8000/docs

4. Initialize the database with seed data (runs automatically on first start):
   - Categories will be pre-populated
   - Sample currencies and cards will be added

### Option 2: Local Development

#### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python -m backend.seed_data
```

4. Run the backend server:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Access the frontend at http://localhost:3000

## Usage

### Admin View

The main interface includes:

1. **Dashboard**: Quick query interface to find the best card for a category
2. **Cards**: Manage your credit cards, add category-specific rewards
3. **Categories**: View and manage spending categories
4. **Merchants**: Map merchants to categories for quick lookups
5. **Settings**: Update point currency CPP values

### Simple View

Access `/simple` for a minimalist interface:
- Single search box for category selection
- Large, clear display of the best card to use
- Perfect for quick lookups

## API Endpoints

### Currencies
- `GET /api/currencies` - List all point currencies
- `POST /api/currencies` - Create new currency
- `PUT /api/currencies/{id}` - Update currency CPP value
- `DELETE /api/currencies/{id}` - Delete currency

### Categories
- `GET /api/categories` - List all categories
- `POST /api/categories` - Create new category
- `PUT /api/categories/{id}` - Update category
- `DELETE /api/categories/{id}` - Delete category

### Cards
- `GET /api/cards` - List all cards with rewards
- `POST /api/cards` - Create new card
- `PUT /api/cards/{id}` - Update card
- `DELETE /api/cards/{id}` - Delete card
- `GET /api/cards/{id}/rewards` - Get card rewards
- `POST /api/cards/{id}/rewards` - Add category reward
- `PUT /api/cards/{id}/rewards/{category_id}` - Update reward
- `DELETE /api/cards/{id}/rewards/{category_id}` - Delete reward

### Merchants
- `GET /api/merchants` - List all merchants
- `GET /api/merchants/search?q={query}` - Search merchants
- `POST /api/merchants` - Create merchant
- `PUT /api/merchants/{id}` - Update merchant
- `DELETE /api/merchants/{id}` - Delete merchant

### Recommendations
- `GET /api/recommend?category_id={id}` - Get ranked recommendations
- `GET /api/recommend?merchant={name}` - Get recommendations by merchant
- `GET /api/recommend/simple?category_id={id}` - Get top card only

## Deployment on Synology NAS

1. Open **Container Manager** on your Synology
2. Go to **Project** and create a new project
3. Upload your docker-compose.yml file
4. Start the project
5. Map `/app/data` to a persistent folder on your NAS for database backup

### Setting up Cloudflare Tunnel

1. Install cloudflared on your Synology or as a Docker container
2. Create a tunnel pointing to `http://localhost:8000`
3. Access your app externally via the Cloudflare URL

## Database

The SQLite database is stored at `data/cards.db`. This file contains all your:
- Credit cards
- Point currencies
- Categories
- Merchants
- Category rewards
- Spend tracking data

**Backup**: Simply copy `data/cards.db` to backup your entire configuration.

## Project Structure

```
card-optimizer/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── seed_data.py         # Database initialization
│   ├── routers/             # API route handlers
│   │   ├── cards.py
│   │   ├── categories.py
│   │   ├── currencies.py
│   │   ├── merchants.py
│   │   └── recommend.py
│   └── services/
│       └── recommendation.py # Recommendation logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── api/
│   │   │   └── client.js    # API client
│   │   └── pages/           # React pages
│   ├── public/
│   │   └── manifest.json    # PWA manifest
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── data/                    # SQLite database (gitignored)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Sample Data

The system includes sample data:

### Point Currencies
- Cashback (1.0 CPP)
- Chase UR (1.8 CPP)
- Amex MR (1.5 CPP)
- Citi TYP (1.5 CPP)
- Capital One Miles (1.4 CPP)

### Sample Cards
- Chase Freedom Flex (Chase UR, 1% default)
- Amex Blue Cash Preferred (Cashback, 1% default)
- Citi Custom Cash (Cashback, 1% default)
- Chase Sapphire Preferred (Chase UR, 1% default)

## Future Phases

- **Phase 2**: Promotion/deal tracker for temporary offers
- **Phase 3**: Spend cap monitoring with alerts
- **Phase 4**: Churning tracker (5/24 status, bonus eligibility)
- **Phase 5**: Transaction import from banking apps

## License

See LICENSE file for details.

## Contributing

This is a personal project. Feel free to fork and customize for your needs!
