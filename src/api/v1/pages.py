from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from src.api.v1.documents import get_documents, view_document, add_documents_to_index
from src.core.searching import get_path_by_docnum


router = APIRouter()
templates = Jinja2Templates(directory='src/templates')


@router.get('/')
async def get_index_html(
    request: Request
):
    return templates.TemplateResponse(
        name='index.html',
        context={'request': request}
    )


@router.get('/search')
async def get_documents_html(
    request: Request,
    query: str
):
    documents = await get_documents(query)
    return templates.TemplateResponse(
        name='documents.html',
        context={'request': request, "query": query, 'documents': documents}
    )


@router.get('/view_document')
async def view_document_html(
    request: Request,
    document_num: str
):
    path = get_path_by_docnum(int(document_num))
    document = await view_document(path)
    return templates.TemplateResponse(
        name='document.html',
        context={'request': request, 'path': path, 'document_num': document_num, 'document': document}
    )


@router.post('/add_documents_to_index')
async def add_documents_to_index_html(
    request: Request,
    indexed_document=Depends(add_documents_to_index)
):
    return templates.TemplateResponse(
        name='add_documents_to_index.html',
        context={'request': request, 'indexed_document': indexed_document}
    )
