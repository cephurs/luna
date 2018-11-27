# Accuracy tester, please do not use 

from time import sleep
import requests
import newspaper
from statistics import mean

from newspaper import Article
from newspaper import Config
from newspaper import fulltext
from os import sys

import bs4
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer  

import luna_lexicon

words = luna_lexicon.words 

def determine(score): 
    positive = 0.5
    negative = -0.5
    if (score > 0) and (score < (positive/2)):
        return "milbull"
    if (score > 0) and (score > (positive/2)):
        return "modbull"
    if (score >= positive): 
        return "verbull"
    if (score < 0) and (score > (negative/2)):
        return "milbear"
    if (score < 0) and (score < (negative/2)): 
        return "modbear"
    if (score <= negative): 
        return "verbear"
    else: 
        return "neutral"


def analyze(text): 
    tokenized = nltk.sent_tokenize(text)
    sid = SentimentIntensityAnalyzer()
    sid.lexicon.update(words)
    scores = []
    compound = []
    for token in tokenized: 
        scores.append(sid.polarity_scores(token))
        print(token)
        print(sid.polarity_scores(token))
    for score in scores: 
        compound.append(score["compound"])
    return mean(compound)

def get_content(link): 
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    config.memoize_articles = False 
    config.fetch_images = False 
    config.verbose = True #disable later
    config.https_success_only = False

    article = Article(url=link, config=config)
    article.download() 
    article.parse()
    article.nlp()
    print("KEYWORDS:")
    print(article.keywords)
    return article.text

def main(): 
    defs = {
    "milbull" : "\033[102m\033[1mMildly bullish\033[0m", 
    "modbull" : "\033[102m\033[1mModerately bullish\033[0m",
    "verbull" : "\033[42m\033[1m\033[6mVery bullish\033[0m",
    "milbear" : "\033[43m\033[1mMildly bearish\033[0m",
    "modbear" : "\033[41m\033[1mModerately bearish\033[0m",
    "verbear" : "\033[101m\033[1m\033[6mVery bearish\033[0m",
    "neutral" : "\033[104m\033[1mNeutral\033[0m"
    }
    link = sys.argv[1]
    x = get_content(link)
    print(analyze(x))
    z = determine(analyze(x))
    print(defs[z])
main()