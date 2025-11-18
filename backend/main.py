from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from database import engine
from models import Base
from routers import auth, products, cart, orders, favorites, admin, users, images, profile, messages, notifications, reviews, auth_verification, websocket
from routers import images_supabase
from utils.scheduler import start_background_tasks, stop_background_tasks

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    import asyncio
    asyncio.create_task(start_background_tasks())
    yield
    # Shutdown
    stop_background_tasks()

# Create FastAPI app
app = FastAPI(
    title="Student Marketplace API",
    description="A comprehensive API for the Student Marketplace application",
    version="1.0.0",
    lifespan=lifespan
)

# Get CORS origins from environment variable
# Defaults to "*" for development, but should be set in production
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
if cors_origins_str == "*":
    cors_origins = ["*"]
else:
    # Split by comma and clean up whitespace
    cors_origins = [origin.strip() for origin in cors_origins_str.split(",")]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(auth_verification.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(favorites.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(images_supabase.router)  # Supabase image upload endpoints
app.include_router(profile.router)
app.include_router(messages.router)
app.include_router(notifications.router)
app.include_router(reviews.router)
app.include_router(websocket.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Student Marketplace API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
