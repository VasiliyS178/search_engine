from fastapi import APIRouter
import markdown2
from src.schemas.document import DocumentShow
from src.core.searching import search
from src.core.indexing import update_index, get_content


router = APIRouter()


@router.get('/get_documents', response_model=list[DocumentShow])
async def get_documents(query: str = None):
    if query is None:
        return [{"file_path": ""}]
    documents = search(query)
    return documents


@router.get('/view_document')
async def view_document(path: str):
    document = get_content(path)
    # Преобразование Markdown в HTML
    # doc_html = markdown2.markdown(document, extras=['fenced-code-blocks', 'tables'])
    doc_html = document.replace('\n', '<br>')
    return doc_html


@router.post('/add_documents_to_index')
async def add_documents_to_index(path: str):
    statistics = update_index()
    return statistics

