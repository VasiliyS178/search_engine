import os
from core.config import settings
from core.parsing import get_files_to_search


if __name__ == '__main__':
    test_path = "/Users/vasiliy.samarin/projects/cvm-airflow/scripts"
    files = get_files_to_search(test_path)
    print(1)
    for f in files:
        print(f)
    print(1)

