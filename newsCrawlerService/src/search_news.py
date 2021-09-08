# Created by Subhadip Mitra <dev@subhadipmitra.com>
import logging
import time
import traceback

from config.queryShim import queryFragments
from config.params import params
import json
from utilities.utils import *
from utilities.gcs import *


class SearchNewsURLs:
    symbol = ''
    query = ''
    urls = []
    before = ''
    after = ''
    output = {}
    timestamp = ''
    local_outfile = ''
    remote_outfile = ''
    is_current = False
    is_timebound_search = True

    def __init__(self, symbol, after, before, is_current=False):
        self.symbol = symbol
        self.before = before
        self.after = after
        self.timestamp = str(time.time())
        self.is_current = is_current

        if after is None and before is None:
            self.is_timebound_search = False

    def prepareQueryParams(self):
        self.query = self.symbol
        if params['query']['enable_fragments']:
            for q in queryFragments:
                self.query += " OR " + self.symbol + " " + q
        if self.is_timebound_search:
            self.query += " " + self.after + " " + "before:" + self.before

        print("prepared Query: " + self.query)

    def findNews(self):
        self.prepareQueryParams()
        try:
            from googlesearch import search
        except ImportError:
            print("No module named 'google' found")

        for j in search(self.query, tld="com", num=params['search']['num_results_per_page'],
                        stop=params['search']['max_results'], pause=params['search']['throttle_secs']):
            print(j)
            self.urls.append(j)

    def writeOutputLocal(self):
        data = {"symbol": self.symbol,
                "query": {"before": self.before, "after": self.after, "query": self.query},
                "urls": self.urls}

        self.local_outfile = params['output']['local']['output_folder'] \
                             + "urls_" + cleanse(self.symbol) + "_" + self.timestamp + ".json"

        print("Writing " + str(len(self.urls)) + " to file " + self.local_outfile)

        with open(self.local_outfile, 'w') as f:
            json.dump(data, f)

        print('completed writing!')

    def writeOutputRemote(self):
        bucket_name = params['output']['remote']['gcs_bucket_name']

        if not self.is_current:
            remote_gcs_folder = params['output']['remote']['history']['base_folder_urls']
        else:
            remote_gcs_folder = params['output']['remote']['current']['base_folder_urls']

        if self.is_timebound_search:  # FROM_DATE - END_DATE
            remote_gcs_folder += cleanse(self.symbol) + "/" + self.after + ":" + self.before + "/"
        else:
            yy, mm, dd = get_year_month_day()
            remote_gcs_folder += cleanse(self.symbol) + "/" + str(yy) + "/" + str(mm) + "/" + str(dd) + "/"

        self.remote_outfile = remote_gcs_folder + \
                              self.local_outfile.replace(params['output']['local']['output_folder'], '')

        upload_gcs(bucket_name, self.local_outfile, self.remote_outfile)

    def process(self):
        try:
            self.findNews()
            self.writeOutputLocal()
            self.writeOutputRemote()  # TODO: Make async
            return {
                'status': 'ok'
                , 'urls': self.urls
                , 'local_file': self.local_outfile
                , 'remote_file': self.remote_outfile}

        except Exception as e:
            logging.error(traceback.format_exc())
            return {'status': 'failed'}


# --------------------------------------------

if __name__ == "__main__":
    search_news = SearchNewsURLs('j.c. penney', "2012-11-12", "2013-04-13")
    search_news.findhNews()
    search_news.writeOutputLocal()
