import os

params = {
    "redis": {
        "host": 'localhost' if os.getenv("REDIS_HOSTNAME") is None else os.getenv("REDIS_HOSTNAME"),
        "port": '6379' if os.getenv("REDIS_PORT") is None else os.getenv("REDIS_PORT"),
    },
    "output": {
        "local": {"output_folder": "../output/"},
        "remote": {
            "history": {
                "base_folder_articles": "history/articles/",
                "base_folder_urls": "history/urls/"
            },
            "current": {
                "base_folder_articles": "current/articles/",
                "base_folder_urls": "current/urls/"
            },
            "gcs_bucket_name": "eep-news-crawler",
        }
    },

    "search": {
        "num_results_per_page": 10,
        "max_results": 10,
        "throttle_secs": 5.0
    },
    "query": {
        "enable_fragments": True
    },

    "gcp_credentials": "/Users/subhadip/PycharmProjects/newsCrawlerService/gcp-key.json"
}
