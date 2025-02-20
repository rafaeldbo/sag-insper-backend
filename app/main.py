from fastapi import FastAPI
from .routers import activity, healthcheck
from app.schemas import Tags

app = FastAPI(
    title='API SAG Insper',
    description='API of the automation resources created for Secretária acadêmica de Graduação do Insper (SAG-Insper)',
    openapi_tags=Tags.__metadata__
)

app.include_router(healthcheck.router)
app.include_router(activity.router)