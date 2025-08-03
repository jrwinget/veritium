from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.config import settings
from app.db.database import init_db

app = FastAPI(
    title="Veritium API",
    description="Scientific Article Verification System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await init_db()


app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Veritium API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
