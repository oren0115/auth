"""Main application entry point untuk Authentication Service."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config.database import connect_db, disconnect_db
from app.config.env import settings
import app.modules.auth
from app.modules.auth.auth.router import router as auth_router  # type: ignore
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inisialisasi rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager untuk lifecycle aplikasi."""
    logger.info("Starting application...")
    await connect_db()
    yield
    logger.info("Shutting down application...")
    await disconnect_db()


app = FastAPI(
    title=settings.APP_NAME,
    description="Authentication Service - Modular and Scalable",
    version="1.0.0",
    lifespan=lifespan
)

# Setup rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set limiter untuk router (setelah app dibuat)
# Limiter di router harus menggunakan state yang sama dengan app
from app.modules.auth.auth.router import limiter as router_limiter
router_limiter.state = app.state

# Konfigurasi CORS dari environment variable
cors_origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint untuk informasi dasar API."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint untuk monitoring."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
