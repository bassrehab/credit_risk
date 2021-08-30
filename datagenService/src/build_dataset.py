import json

import pandas as pd

from utilities.gcs import *
from utilities.utils import *
from config.params import *

class BuildDataset:
    base_dataset_bucket = params["base_dataset"]["bucket"]
    base_remote_file = params["base_dataset"]["remote_file"]
    base_local_file = params["base_dataset"]["local_file"]

    processed_dataset_bucket = params["processed_dataset"]["bucket"]
    processed_remote_file = params["processed_dataset"]["remote_file"]
    processed_local_file = params["processed_dataset"]["local_file"]

    DELTA_DAYS = params["delta_days"]

    def process(self):
        if download_gcs(self.base_dataset_bucket, self.base_remote_file, self.base_local_file):
            entity_dates = self.parseEntitiesAndBuildDates()
            self.writeLocalFile(entity_dates)
            upload_gcs(self.processed_dataset_bucket, self.processed_local_file, self.processed_remote_file)

    def parseEntitiesAndBuildDates(self):
        entity_dates = dict()
        df = pd.read_csv(self.base_local_file)

        for ind in df.index:
            _key = str(df['legal_entity_cleansed'][ind])
            _temp = dict()
            _temp['uuid'] = str(df['uuid'][ind])
            _temp['rating_date'] = str(df['rating_action_date'][ind])
            _temp['before_date'] = dateBeforeAfter(_temp['rating_date'], self.DELTA_DAYS, before=True)
            _temp['after_date'] = dateBeforeAfter(_temp['rating_date'], self.DELTA_DAYS, before=False)
            _temp['search_term_general'] = str(df['issuer_name_normalized'][ind])
            _temp['search_term_specific'] = str(df['issuer_name'][ind])

            if _key in entity_dates:
                entity_dates[_key].append(_temp)
            else:
                entity_dates.update({_key: [_temp]})

            # Sort reverse - newest data first
            entity_dates[_key].sort(key=lambda k: k['rating_date'], reverse=True)
        return entity_dates

    def writeLocalFile(self, entity_dates):
        try:
            with open(self.processed_local_file, 'w') as processed_file:
                processed_file.write(json.dumps(entity_dates))
        except Exception as e:
            logging.error(traceback.format_exc())
