from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import engine
from models import Base
from routers import auth, products, cart, orders, favorites, admin, users, images, profile, messages, notifications, reviews, auth_verification, websocket
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
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
