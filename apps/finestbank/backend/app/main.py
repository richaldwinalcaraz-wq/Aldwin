from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.analyst import router as analyst_router
from app.api.health import router as health_router
from app.api.rollup import router as rollup_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router
from app.core.redis_client import close_redis, init_redis
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis(app, settings.redis_url)
    yield
    await close_redis(app)
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(rollup_router, prefix="/api/v1")
app.include_router(analyst_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(ws_router)


@app.get("/")
async def root():
    return {"message": f"{settings.app_name} v{settings.app_version}"}
