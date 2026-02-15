"""
Main FastAPI application entry point.

This module creates the FastAPI application instance, configures middleware,
and includes all service routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import service routers
from api.auth.routes import router as auth_router
from api.farmer.routes import router as farmer_router
from api.customers.routes import router as customers_router
from api.products.routes import router as products_router
from api.orders.routes import router as orders_router
from api.shipments.routes import router as shipments_router
from api.cart.routes import router as cart_router
from api.analytics.routes import router as analytics_router
from api.payments.routes import router as payments_router

# Create FastAPI application instance
app = FastAPI(
    title="From Field to You API",
    description="Agricultural supply chain management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include service routers
app.include_router(
    auth_router,
    prefix="/api/auth",
    tags=["auth"]
)

app.include_router(
    farmer_router,
    prefix="/api/farmer",
    tags=["farmer"]
)

app.include_router(
    customers_router,
    prefix="/api/customers",
    tags=["customers"]
)

app.include_router(
    products_router,
    prefix="/api/products",
    tags=["products"]
)

app.include_router(
    orders_router,
    prefix="/api/orders",
    tags=["orders"]
)

app.include_router(
    shipments_router,
    prefix="/api/shipments",
    tags=["shipments"]
)

app.include_router(
    cart_router,
    prefix="/api",
    tags=["cart"]
)

app.include_router(
    analytics_router,
    prefix="/api",
    tags=["analytics"]
)

app.include_router(
    payments_router,
    prefix="/api/payments",
    tags=["payments"]
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "message": "Welcome to From Field to You API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)