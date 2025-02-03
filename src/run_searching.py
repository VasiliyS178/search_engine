import os
from core.config import settings
from core.searching import run_search


if __name__ == '__main__':
    results = []

    queries = [
        "hive_cvm_acrm last_email_undelivered",
        "hive_cvm_acrm acrm_ma_customer_tc5"
    ]

    for query in queries:
        results.extend(run_search(query))

    with open(os.path.join(settings.LOGS_PATH, "results.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(results))
