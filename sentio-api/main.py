from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging
import os

load_dotenv()

from routers import auth, users, biases, assessments, journal, insights, therapists, ai, admin, community, socratic
from services.scheduler import start_scheduler, scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    # Pre-warm the sentence-transformer embedder in a thread so the first
    # /ai/chat request doesn't block waiting for model load.
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        from services.rag_service import _get_embedder
        await loop.run_in_executor(None, _get_embedder)
        logger.info("[Startup] RAG embedder ready")
    except Exception as e:
        logger.warning(f"[Startup] RAG embedder pre-warm skipped: {e}")
    yield
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Shut down")


app = FastAPI(
    title="Sentio API",
    description="Cognitive bias self-awareness platform backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(biases.router, prefix="/biases", tags=["biases"])
app.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
app.include_router(journal.router, prefix="/journal", tags=["journal"])
app.include_router(insights.router, prefix="/insights", tags=["insights"])
app.include_router(therapists.router, prefix="/therapists", tags=["therapists"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(community.router, prefix="/community", tags=["community"])
app.include_router(socratic.router, prefix="/socratic", tags=["socratic"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "sentio-api"}


@app.get("/")
async def root():
    return {
        "message": "Welcome to the Sentio API",
        "docs": "/docs",
        "health": "/health",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    # Starlette's ServerErrorMiddleware fires before CORSMiddleware can add headers
    # for 500s, so we add them manually here to prevent browser CORS blocks.
    origin = request.headers.get("origin", "")
    cors_headers = {}
    if origin and (origin in origins or "*" in origins):
        cors_headers["Access-Control-Allow-Origin"] = origin
        cors_headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred."},
        headers=cors_headers,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
