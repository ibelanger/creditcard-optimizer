from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routers import cards, categories, currencies, merchants, recommend
import os

# Create FastAPI app
app = FastAPI(
    title="Card Optimizer API",
    description="Credit card optimization platform - Phase 1",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(currencies.router)
app.include_router(categories.router)
app.include_router(cards.router)
app.include_router(merchants.router)
app.include_router(recommend.router)


@app.on_event("startup")
async def startup_event():
    """Create database tables on startup if they don't exist."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create tables
    Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Card Optimizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "currencies": "/api/currencies",
            "categories": "/api/categories",
            "cards": "/api/cards",
            "merchants": "/api/merchants",
            "recommendations": "/api/recommend"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
