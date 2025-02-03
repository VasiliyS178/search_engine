import os
from dotenv import load_dotenv


env_path = '.env'
load_dotenv(dotenv_path=env_path)


class Settings:
    APP_TITLE = "Knowledge Base API"
    PROJECT_VERSION = "0.0.2"

    # Cloning options
    GITLAB_HOST = os.getenv('GITLAB_HOST', "")
    GITLAB_TOKEN = os.getenv('GITLAB_TOKEN', "")
    REPOSITORIES_ROOT_DIR = os.getenv('REPOSITORIES_ROOT_DIR', "")
    GROUP_ID = os.getenv('GROUP_ID', "")
    CLONING_MODE = "http"

    # Indexing options
    LAST_INDEXED_DTTM = os.getenv('LAST_INDEXED_DTTM', "")
    LOGS_PATH = os.getenv('LOGS_PATH', "")
    KNOWLEDGE_BASE_PATH = os.getenv('KNOWLEDGE_BASE_PATH', "")
    INDEX_PATH = os.getenv('INDEX_PATH', "")
    CNT_JOBS = 8  # количество потоков для индексации. Максимум зависит от процессора в вашем комьютере
    BATCH_SIZE = 300  # количество файлов в обном батче
    START_BATCH = 1  # для пропуска обработанных батчей, если в процессе произошел сбой. Поменять перед продолжением
    MAX_FILE_SIZE_M = 2  # максимальный размер файлов для индексации в Мб
    TEXT_FORMATS = [
        "py", "java", "txt", "rtf", "md", "css", "yaml", "json", "yml", "sql", "ipynb", "log", "sh", "conf",
        "xml", "iml", "ts"
    ]
    CONVERTABLE_FORMATS = ["docx", "pptx", "html"]  # перечень может быть дополнен форматом xlsx
    GARBAGE_FILES = ["DS_Store", "__pycache__", "__init__", "Thumbs", "gitignore", "git", ""]

    # Searching options
    LIMIT_CNT_RESULTS = 100


settings = Settings()
