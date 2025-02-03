from fastapi import APIRouter
from src.api.v1 import documents, pages

main_router = APIRouter()
main_router.include_router(documents.router, prefix='/api/v1/documents', tags=['Documents'])
main_router.include_router(pages.router, prefix="", tags=["Frontend"])
