from whoosh.index import open_dir
from whoosh.query import And, Term
import logging
from .config import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", datefmt=None)
logger = logging.getLogger(__name__)

INDEX_PATH = settings.INDEX_PATH
LIMIT_CNT_RESULTS = settings.LIMIT_CNT_RESULTS
REPLACEMENT_PART = "/Users/vasiliy.samarin/Documents/gitlab_copy"


def get_path_by_docnum(docnum: int):
    ix = open_dir(INDEX_PATH)
    with ix.searcher() as searcher:
        return searcher.stored_fields(docnum)["path"]


def search(query: str) -> list:
    output = []
    ix = open_dir(INDEX_PATH)
    with ix.searcher() as searcher:
        query = And([Term("content", word.lower()) for word in query.split(" ")])
        results = searcher.search(q=query, limit=LIMIT_CNT_RESULTS)
        for result in results:
            output.append({"file_path": result["path"], "document_num": result.docnum})
    return sorted(output, key=lambda x: x['file_path'])


def prepare_results(query: str, raw_results: list, projects: list) -> list:
    results = {query: []}
    prepared_results = []
    for result in raw_results:
        results[query].append(result["file_path"])

    if len(results[query]) == 0:
        results[query].append("Not found")

    for path in results[query]:
        project_nm = "unknown"
        if "backup-dont-use" in path:
            continue
        clean_path = path.replace(REPLACEMENT_PART, "")
        for project in projects:
            if clean_path.startswith(project):
                project_nm = project
                break
        prepared_results.append(f"{query};{project_nm};{clean_path}")
    return prepared_results


def run_search(query: str):
    assert isinstance(query, str), "Your query must be a string"
    if len(query) < 4:
        return f"{query};Length of the query string must be more than 3 symbols"
    prepared_query = query.replace(".", " ")
    logger.info(prepared_query)
    raw_results = search(prepared_query)
    return raw_results
