import logging
import traceback

from google.cloud import language_v1
import os
from src.utilities.nlputils import NLPUtils
import json
from transformers import pipeline


class SentimentClassifier:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SentimentClassifier, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.nu = NLPUtils()

    def getABSA(self, text_content, anchor_entity, text_id, text_type="PLAIN_TEXT",
                entity_similarity_threshold=0.2, salience_threshold=0.4):

        logging.info("Evaluation ABSA for id:{} , text: {}", format(text_id, text_content))

        client = language_v1.LanguageServiceClient()

        anchor_entity_results = {
            "status": "failed"
            , "_id": text_id
            , "max_salience": 0
            , "max_sentiment_score": -1
            , "max_sentiment_magnitude": 0
            , "lang": ""
            , "similar_entities": []
            , "related_entities": []
        }

        if text_type == "PLAIN_TEXT":
            type_ = language_v1.Document.Type.PLAIN_TEXT
        elif text_type == "HTML":
            type_ = language_v1.Document.Type.HTML
        else:
            type_ = language_v1.Document.Type.TYPE_UNSPECIFIED

        document = {"content": text_content, "type_": type_}

        # Available values: NONE, UTF8, UTF16, UTF32
        encoding_type = language_v1.EncodingType.UTF8
        response = client.analyze_entity_sentiment(request={'document': document, 'encoding_type': encoding_type})

        anchor_entity_results['lang'] = response.language

        # Loop through entities returned from the API
        for entity in response.entities:
            entity_similarity_score = self.nu.calculateCosineSimilarity([entity.name, anchor_entity])
            sentiment = entity.sentiment

            if entity_similarity_score > entity_similarity_threshold:
                # capture the similar entities
                _sim_entity = {'name': entity.name}

                # collect additional metadata for this similar entity.
                for metadata_name, metadata_value in entity.metadata.items():
                    _sim_entity[metadata_name] = metadata_value

                anchor_entity_results['similar_entities'].append(_sim_entity)

                if entity.salience > anchor_entity_results['max_salience']:
                    anchor_entity_results['max_salience'] = entity.salience

                if sentiment.score > anchor_entity_results['max_sentiment_score']:
                    anchor_entity_results['max_sentiment_score'] = sentiment.score

                if sentiment.magnitude > anchor_entity_results['max_sentiment_magnitude']:
                    anchor_entity_results['max_sentiment_magnitude'] = sentiment.magnitude


            # if the entity salience is atleast > 70% of anchor entity, else ignore
            else:
                comparative_salience = entity.salience / anchor_entity_results['max_salience']
                if comparative_salience > salience_threshold:
                    _temp = {"name": entity.name, "salience": entity.salience, "sentiment_score": sentiment.score,
                             "sentiment_magnitude": sentiment.magnitude}

                    for metadata_name, metadata_value in entity.metadata.items():
                        _temp[metadata_name] = metadata_value

                    anchor_entity_results['related_entities'].append(_temp)

        anchor_entity_results['status'] = "ok"
        return json.dumps(anchor_entity_results)

    def getSATransformers(self, text_content, text_id):
        logging.info("Evaluation SA for id:{} , text: {}", format(text_id, text_content))
        try:
            sentiment_analysis = pipeline('sentiment-analysis')
            result = sentiment_analysis(text_content)[0]
            return {'status': 'ok', 'id': text_id, 'label': result['label'], 'score': result['score']}

        except Exception as e:
            logging.error(traceback.format_exc())
            return {'status': 'failed'}

    # --------------------------------------------


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIAL"] ='/Users/subhadip/PycharmProjects/nlpService/gcp-key.json'
    sa = SentimentClassifier()
    txt = 'J.C. Penney Co. executives may be confident in the department-store chain\'s ' \
          'everyday pricing strategy, but investors are panicking. The company\'s stock fell ' \
          'nearly 11 percent on Monday — the biggest percentage decline among big companies in ' \
          'the S&P 500 for the day. The stock is trading at about $18.41, its lowest price since ' \
          'the middle of the recession in March 2009. The drop follows Standard & Poor\'s Ratings ' \
          'move to lower Penney\'s credit rating deeper into junk status on Friday. That came after ' \
          'the company reported its third consecutive quarter of big losses and sales declines ' \
          'since it decided earlier this year to get rid of hundreds of coupons and sales each' \
          ' year in favor of predictable low prices every day. It\'s the latest sign that ' \
          'Wall Street isn\'t any happier with Penney\'s pricing than Main Street is: ' \
          'Investors had pushed Penney stock up 24 percent to about $43 after the company' \
          ' announced the pricing plan in late January. But with Monday\'s drop, the ' \
          'company\'s stock has lost nearly half its value. Penney did not immediately ' \
          'return calls seeking comment on Monday afternoon. But during an investor ' \
          'meeting on Friday, executives assured investors that the company ' \
          'has enough money to continue with the strategy. And CEO Ron Johnson, ' \
          'who took the top job a year ago, reiterated his confidence in the plan ' \
          'and said returning the company to growth is \"Job. No. 1.\" \"The CEO ' \
          'was selling the hope, but now investors are looking at what the company ' \
          'will look like in the first half of the year,\" said Brian Sozzi, a chief ' \
          'equities analyst for research firm NBG Productions who follows the company. \"Investors ' \
          'are digesting the reality.\"'
    print(sa.getABSA(txt, "J.C. Penny", "12313123123"))

    #print(sa.getSATransformers(txt))
