import os
from core.config import settings
from core.parsing import parse_project


if __name__ == '__main__':
    test_path = "/Users/vasiliy.samarin/projects/cvm-segmentator-datamart-update"
    tables = parse_project(test_path)
    print(1)

