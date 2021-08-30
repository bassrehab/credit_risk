import Levenshtein as lv
import string
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from nltk.corpus import stopwords


class NLPUtils:
    _instance = None

    def __init__(self):
        try:
            if nltk.data.find('corpora/stopwords'):
                print('Found existing NLTK corpora/stopwords, skipping download..')
        except LookupError:
            nltk.download('stopwords')

        self.stopwords = stopwords.words('english')

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(NLPUtils, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def calculateLevenshteinSimilarity(self, text1, text2):
        return lv.distance(text1, text2)

    def calculateLevenshteinSimilarityBool(self, text1, text2, threshold=2):
        return lv.distance(text1, text2) > threshold

    def calculateCosineSimilarity(self, sentences=[]):
        cleaned = [self.cleanseString(sentence) for sentence in sentences]
        vectorizer = CountVectorizer().fit_transform(cleaned)
        vectors = vectorizer.toarray()
        return self.cosineSimVectors(vectors[0], vectors[1])

    def cosineSimVectors(self, vec1, vec2):
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)

        return cosine_similarity(vec1, vec2)[0][0]

    def cleanseString(self, text):
        text = ''.join([word for word in text if word not in string.punctuation])
        text = text.lower()
        text = ' '.join([word for word in text.split() if word not in self.stopwords])

        return text