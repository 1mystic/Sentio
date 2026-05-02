from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.assessments.router import router as assessments_router
from app.journal.router import router as journal_router
from app.community.router import router as community_router
from app.modules.router import router as modules_router
from .resources import router as resources_router
from .tools import router as tools_router
from .analytics import router as analytics_router
from .ml import router as ml_router
from app.config import settings
from app.database.connection import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Mindfluence Backend...")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Mindfluence Backend...")

app = FastAPI(
    title="Mindfluence API",
    description="FastAPI backend for Mindfluence mental health application",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={
            "status": "healthy",
            "message": "Mindfluence Backend is running",
            "version": "1.0.0"
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return JSONResponse(
        content={
            "message": "Welcome to Mindfluence API",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    )

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
app.include_router(journal_router, prefix="/journal", tags=["Journal"])
app.include_router(community_router, prefix="/community", tags=["Community"])
app.include_router(modules_router, prefix="/modules", tags=["Learning Modules"])
app.include_router(resources_router)
app.include_router(tools_router)
app.include_router(analytics_router)
app.include_router(ml_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
