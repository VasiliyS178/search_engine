import os
import time
from datetime import datetime
from math import ceil
from markitdown import MarkItDown
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, FileIndex, open_dir, EmptyIndexError
from whoosh.analysis import SpaceSeparatedTokenizer, LowercaseFilter
from multiprocessing import Pool, Lock, Manager
import logging
from .config import settings


CNT_JOBS = settings.CNT_JOBS
INDEX_PATH = settings.INDEX_PATH

results = {
    "unknown_files": [],
    "suitable_files": [],
    "too_big_files": [],
    "processed_files": []
}

logging.basicConfig(
    level=logging.INFO,
    # filename=os.path.join(settings.LOGS_PATH, 'indexing.log'),
    # filemode="a",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)


def get_or_create_index(path: str) -> FileIndex:
    try:
        ix = open_dir(path)
    except EmptyIndexError:
        os.makedirs(path)
        my_analyzer = SpaceSeparatedTokenizer() | LowercaseFilter()
        schema = Schema(
            path=ID(stored=True),
            content=TEXT(analyzer=my_analyzer)
        )
        ix = create_in(path, schema)
    return ix


def get_files_to_index(root_path: str, last_indexed_dttm: str = None):
    allowed_formats = settings.TEXT_FORMATS + settings.CONVERTABLE_FORMATS
    if last_indexed_dttm is not None:
        last_indexed_dttm = datetime.strptime(last_indexed_dttm, "%Y-%m-%d %H:%M:%S")
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


def get_content(path: str):
    content = None

    file_ext = path.split(".")[-1]
    if file_ext in settings.TEXT_FORMATS:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            logging.exception(f"Error opening file {path}.")
    else:
        try:
            md = MarkItDown()
            content = md.convert(path).text_content
        except Exception:
            logging.exception(f"Error converting file {path}.")
    return content


def add_file_to_index(index: FileIndex, path: str, locker: Lock):
    content = get_content(path)

    if content is None:
        logging.error(f"Empty content for file {path}")
        return

    clear_content = (
        content
        .replace("'", " ")
        .replace('"', " ")
        .replace(".", " ")
        .replace(",", " ")
        .replace("!", " ")
        .replace("?", " ")
        .replace(";", " ")
        .replace(":", " ")
        .replace("=", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("{", " ")
        .replace("}", " ")
        .replace("[", " ")
        .replace("]", " ")
        .replace("<", " ")
        .replace(">", " ")
        .replace("%", " ")
        .replace("#", " ")
        .replace("$", " ")
        .replace("^", " ")
        .replace("*", " ")
        .replace("`", " ")
        .replace("~", " ")
        .replace("|", " ")
        .lower()
    )

    # writer = AsyncWriter(ix)
    with locker:
        writer = index.writer()
        writer.add_document(path=path, content=clear_content)
        writer.commit()
    return path


def run_indexing(batch):
    manager = Manager()
    lock = manager.Lock()
    total_tasks = len(batch)
    ix = open_dir(INDEX_PATH)

    with Pool(processes=CNT_JOBS) as p:
        async_tasks = p.starmap_async(
            add_file_to_index,
            [(ix, file_path, lock) for file_path in batch]
        )
        while not async_tasks.ready():
            completed_tasks = total_tasks - async_tasks._number_left
            logging.info(f'{completed_tasks}/{total_tasks} files have been processed')
            time.sleep(5)

        processed_files = async_tasks.get()
    return processed_files


def update_index():
    get_files_to_index(settings.DIRECTORY_TO_INDEX, settings.LAST_INDEXED_DTTM)
    logging.info(f"Count files to index: {len(results['suitable_files'])}")

    _ = get_or_create_index(settings.INDEX_PATH)

    cnt_batches = ceil(len(results['suitable_files']) / settings.BATCH_SIZE)
    sorted_files = sorted(results['suitable_files'])
    for batch_number in range(cnt_batches):
        if batch_number + 1 < settings.START_BATCH:
            continue
        batch = sorted_files[batch_number * settings.BATCH_SIZE: (batch_number + 1) * settings.BATCH_SIZE]
        logging.info(f"Batch {batch_number + 1}/{cnt_batches} is being processed")
        processed_files = run_indexing(batch)
        indexed_files = [file for file in processed_files if file is not None]
        results["processed_files"].extend(indexed_files)
        logging.info(f"Count processed files: {len(indexed_files)}/{len(batch)}")

    for result in results:
        with open(os.path.join(settings.LOGS_PATH, f"{result}.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(results[result]))


if __name__ == '__main__':
    update_index()
