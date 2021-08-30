from newspaper import Article
import sys

def get_news_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return {'text': article.text, 'title': article.title, 'authors': article.authors}

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
    get_news_article(urls)
