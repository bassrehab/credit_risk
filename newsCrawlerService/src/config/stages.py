from enum import Enum
import platform


class Stages(Enum):
    # NOT_STARTED -> INITIATED -> SUCCEEDED/FAILED
    STAGE_0 = {}
    STAGE_1 = {"stage_id": "NCS1"
        , "stage_desc": "Search Google for entity news within specified dates"
        , "stage_status": "NON_STARTED"
        , "stage_start_time": -1
        , "stage_end_time": -1
        , "stage_processing_node": platform.node()
        , "hasErrors": False
        , "errors": []}

    STAGE_2 = {"stage_id": "NCS2"
        , "stage_desc": "Fetching articles from individual URLs"
        , "stage_status": "NON_STARTED"
        , "stage_start_time": -1
        , "stage_end_time": -1
        , "stage_processing_node": platform.node()
        , "hasErrors": False
        , "errors": []}

    STAGE_3 = {"stage_id": "NCS3"
        , "stage_desc": "Running NLP processes on individual articles"
        , "stage_status": "NON_STARTED"
        , "stage_start_time": -1
        , "stage_end_time": -1
        , "stage_processing_node": platform.node()
        , "hasErrors": False
        , "errors": []}

    STAGE_4 = {"stage_id": "NCS4"
        , "stage_desc": "Calculating aggregate NLP sentiment scores for entities"
        , "stage_status": "NON_STARTED"
        , "stage_start_time": -1
        , "stage_end_time": -1
        , "stage_processing_node": platform.node()
        , "hasErrors": False
        , "errors": []}


print(list(Stages))
