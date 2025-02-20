from fastapi import FastAPI
from .routers import activity
from app.schemas import Tags

app = FastAPI(
    title='API SAG Insper',
    description='API of the automation resources created for Secretária acadêmica de Graduação do Insper (SAG-Insper)',
    openapi_tags=Tags.__metadata__
)

app.include_router(activity.router)