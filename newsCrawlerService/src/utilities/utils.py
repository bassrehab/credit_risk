import re
import datetime
import uuid

def get_uuid():
    return str(uuid.uuid4())

def cleanse(text):
    return re.sub('[^A-Za-z0-9]+', '', text)


def get_year_month_day():
    now = datetime.datetime.now()
    return now.year, now.month, now.day


def get_sentences(para):
    from nltk.tokenize.punkt import PunktSentenceTokenizer, PunktParameters
    punkt_params = PunktParameters()
    punkt_params.abbrev_types = set(['Mr', 'Mrs', 'Ms', 'LLC', 'Inc', 'i.e', 'e.g', 'al'])
    tokenizer = PunktSentenceTokenizer(punkt_params)
    tokens = tokenizer.tokenize(para)

    sentences = []
    for t in tokens:
        sentences.append(t)

    return sentences


def dateBeforeAfter(str_stamp, duration=50, before=True, date_format='%Y-%m-%d'):
    import datetime
    _dt = datetime.datetime.strptime(str_stamp, date_format)
    if before is False: duration *= -1
    d = datetime.timedelta(days=duration)
    return (_dt - d).strftime(date_format)


def nextSmallerElement(arr,n):
    orig = n
    curr_smallest = None
    for i in range(len(arr)):
        if curr_smallest is None:
            if arr[i] < n:
                curr_smallest = arr[i]
        else:
            if arr[i] > curr_smallest and arr[i] < n:
                curr_smallest = arr[i]
    return curr_smallest
# --------------------------------------------

if __name__ == "__main__":
    y, m, d = get_year_month_day()
    print(y, m, d)
    print(cleanse("j.c. penny"))

    print(get_sentences("It's very likely the JC Penney could not have been saved by anything short "
                        "of a presidential executive order that all mom jeans shall henceforth be "
                        "purchased from JC Penney. As I've written, department stores are in "
                        "secular decline for economic reasons (the non-recovery recovery), "
                        "demographic reasons (younger people are moving away from older suburbs), "
                        "and technological reasons (Amazon.com is a department store in every room "
                        "and Walmart wins every price war)."))
