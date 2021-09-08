# Created by Subhadip Mitra <dev@subhadipmitra.com>
import logging
import multiprocessing
import os
import time
from task_extract_article import get_news_article

PROCESSES = multiprocessing.cpu_count() - 1

def create_logger(pid):
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(f"../logs/process_{pid}.log")
    fmt = "%(asctime)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def process_tasks(task_queue, return_dict):
    proc = os.getpid()
    logger = create_logger(proc)
    while not task_queue.empty():
        try:
            url = task_queue.get()
            return_dict[proc] = get_news_article(url)
        except Exception as e:
            logger.error(e)
        logger.info(f"Process {proc} completed successfully")
    return True


def add_tasks(task_queue, urls):
    for url in urls:
        task_queue.put(url)
    return task_queue


def run(urls):
    """
    @param urls: list of news article urls
    @return: list of {text: ARTICLE_FULL_TEXT, title: ARTICLE_TITLE, authors:[AUTHOR_NM_1, AUTHOR_NM_2]}
    """
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    empty_task_queue = multiprocessing.Queue()
    full_task_queue = add_tasks(empty_task_queue, urls)
    processes = []
    print(f"Running with {PROCESSES} processes!")
    start = time.time()
    for w in range(PROCESSES):
        p = multiprocessing.Process(target=process_tasks, args=(full_task_queue, return_dict))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"Time taken = {time.time() - start:.10f}")

    return return_dict.values()

if __name__ == "__main__":
    urls = [
        "https://dealbook.nytimes.com/2012/11/12/a-dose-of-realism-for-the-chief-of-j-c-penney/"
        , "https://www.dividend.com/dividend-education/the-history-of-j-c-penneys-collapse/"
        , "https://news.yahoo.com/amphtml/news/penney-biggest-p-stock-loser-204005045.html"
        ,
        "https://seekingalpha.com/article/999271-update-j-c-penney-should-listen-to-its-customers?source=all_articles_title"
        , "https://www.dallasnews.com/business/retail/2012/11/13/j-c-penney-stock-falls-as-holiday-shopping-begins/"
        , "https://wwd.com/pmc-stock/kering/page/7870/?sub_action=error&sub_error=Missing%20Session%20Id"
        ,
        "https://wwd.com/pmc-stock/hermes-international-sca/page/7874/?sub_action=error&sub_error=Missing%20Session%20Id"
        , "https://strategyinsight.wordpress.com/tag/mcdonalds/"
        , "https://www.benzinga.com/news/12/07/2736007/can-dreamworks-indoor-theme-park-outshine-disney-world"
        , "https://www.mdpi.com/2071-1050/13/9/5254/htm"
    ]
    run(urls)