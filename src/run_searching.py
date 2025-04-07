import os
from core.config import settings
from core.searching import run_search, prepare_results


QUERIES_FILE_NAME = "queries.txt"
PROJECTS_FILE_NAME = "projects.txt"


if __name__ == '__main__':
    results = []
    projects = []

    with open(os.path.join(settings.LOGS_PATH, QUERIES_FILE_NAME), "r", encoding="utf-8") as f:
        queries = f.readlines()

    with open(os.path.join(settings.LOGS_PATH, PROJECTS_FILE_NAME), "r", encoding="utf-8") as f:
        project_list = f.readlines()

    for project in project_list:
        project = project.replace("\n", "")
        projects.append(f'/{project.replace(";", "/")}')

    for query in queries:
        prepared_query = query.replace("\n", "")
        raw_results = run_search(prepared_query)
        prepared_results = prepare_results(prepared_query, raw_results, projects)
        results.extend(prepared_results)

    with open(os.path.join(settings.LOGS_PATH, "results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(results))
