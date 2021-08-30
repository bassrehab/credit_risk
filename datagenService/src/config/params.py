import os
_cwd = os.environ["CURRENT_WORKING_DIR"]
params = {
    "base_dataset": {
        "bucket": "data-ratings",
        "remote_file": "cleansed/base_normalized.csv",
        "local_file": _cwd + "/data/download.csv"
    },
    "processed_dataset": {
        "local_file": _cwd + "/data/processed_entities.json",
        "bucket": "data-ratings",
        "remote_file": "cleansed/processed_entities.json",
    },
    "delta_days": 50
}

