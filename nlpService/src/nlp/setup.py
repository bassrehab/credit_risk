import pathlib
import aspect_based_sentiment_analysis as absa
from setuptools import setup
from setuptools import find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The README text
README = (HERE / "README.md").read_text()
description = 'TF based Aspect Based Sentiment Analysis'

setup(
    name='aspect-based-sentiment-analysis',
    version=absa.__version__,  # Semantic: MAJOR, MINOR, and PATCH
    url='https://github.com/bassrehab/nlpService',
    description=description,
    long_description=README,
    long_description_content_type="text/markdown",
    include_package_data=False,
    packages=find_packages(),
    install_requires=[
        'tensorflow==2.5',
        'transformers==4.8',
        'pytest',
        'scikit-learn',
        'ipython',
        'google-cloud-storage',
        'testfixtures',
        'optuna',
        'spacy'
    ],
    python_requires='==3.7.*',
)
