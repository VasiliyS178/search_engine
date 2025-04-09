import os
import re
import time
from datetime import datetime
from math import ceil
from markitdown import MarkItDown
from multiprocessing import Pool, Lock, Manager
import logging
from .config import settings
from .indexing import get_content


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s", datefmt=None)
logger = logging.getLogger(__name__)


def get_files_to_parse(root_path: str, last_parsed_dttm: str = None):
    results = {
        "unknown_files": [],
        "suitable_files": [],
        "too_big_files": [],
        "processed_files": []
    }
    allowed_formats = settings.TEXT_FORMATS + settings.CONVERTABLE_FORMATS

    if last_parsed_dttm is not None:
        last_indexed_dttm = datetime.strptime(last_parsed_dttm, "%Y-%m-%d %H:%M:%S")
    else:
        last_indexed_dttm = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    for root, dirs, files in os.walk(root_path):
        for file in files:
            file_name_parts = file.split(".")
            file_name = file_name_parts[0]
            file_ext = file_name_parts[-1]
            abs_path = os.path.join(root, file)

            if file_name in settings.GARBAGE_FILES:
                continue

            if file_ext in allowed_formats:
                last_modified = os.path.getmtime(abs_path)
                last_modified_dttm = datetime.strptime(
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_modified)), "%Y-%m-%d %H:%M:%S"
                )

                if last_modified_dttm <= last_indexed_dttm:
                    continue

                if os.path.getsize(abs_path) / 1024 / 1024 > settings.MAX_FILE_SIZE_M:
                    results["too_big_files"].append(abs_path)
                else:
                    results["suitable_files"].append(abs_path)
            else:
                results["unknown_files"].append(abs_path)
    return results


def parse_file(file_content: str):
    all_matches = []

    pyspark_pattern = r'\.table\(([^"\']+?)\)'
    all_matches.extend(re.findall(pyspark_pattern, file_content))

    spark_sql_pattern = r''

    return all_matches


def parse_project(project_path: str):
    results = []
    project_files = get_files_to_parse(project_path)
    for file_path in project_files["suitable_files"]:
        file_content = get_content(file_path)
        results.extend(parse_file(file_content))
    return results
