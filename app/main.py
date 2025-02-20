from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import activity, healthcheck
from app.metadata import Tags, ALLOWED_ORIGINS

app = FastAPI(
    title='API SAG Insper',
    description='API of the automation resources created for Secretária acadêmica de Graduação do Insper (SAG-Insper)',
    openapi_tags=Tags.__metadata__
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(healthcheck.router)
app.include_router(activity.router)