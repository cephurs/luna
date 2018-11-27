
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

defs = {
"milbull" : "\033[102m\033[1mMildly bullish\033[0m", 
"modbull" : "\033[102m\033[1mModerately bullish\033[0m",
"verbull" : "\033[42m\033[1m\033[5mVery bullish\033[0m",
"milbear" : "\033[43m\033[1mMildly bearish\033[0m",
"modbear" : "\033[41m\033[1mModerately bearish\033[0m",
"verbear" : "\033[101m\033[1m\033[5mVery bearish\033[0m",
"neutral" : "\033[104m\033[1mNeutral\033[0m"
}


def blacklist(text): 
    if "Please make sure your browser supports JavaScript and cookies" in text: 
        return True 
    if "zacks.com" in text: 
        return True
    else: 
        return False

def determine(score): 
    positive = 0.05
    negative = -0.05
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
    for score in scores: 
        compound.append(score["compound"])
    return mean(compound)


def fetch_urls(ticker):
    news_urls = ["https://news.google.com/news/rss/search/section/q/${}+news?ned=us&gl=US&hl=en", "https://feeds.finance.yahoo.com/rss/2.0/headline?s={}&region=US&lang=en-US"]
    total_links = []
    for news_url in news_urls: 
        news_url = news_url.format(ticker)
        Client=urlopen(news_url)
        xml_page=Client.read()
        Client.close()

        links = []
        soup_page=soup(xml_page,"xml")
        news_list=soup_page.findAll("item")
        for news in news_list:
            if blacklist(news.link.text) == True:
                pass 
            else:  
                links.append(news.link.text)
        total_links = total_links + links
    # removes duplicate URLs
    total_links = list(set(total_links))
    return total_links 

def get_content(link):
    config = Config()
    config.browser_user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
    config.memoize_articles = True 
    config.fetch_images = False 
    config.verbose = True #disable later
    config.https_success_only = False

    article = Article(url=link, config=config)
    sleep(1)
    article.download() 
    if article.download_state == 1 : #has the download failed? eg. due to 403 
        return None 
    else:
        article.parse()
        if len(article.text) < 200: #too short?
            return None
        else:
            print(link)
            print("="*80)
            return article.text

def get_text(links): 
    data = []
    print("There are {} links found for your ticker. Would you like to slice from this list? [Y/N]".format(len(links)))
    answer = input()
    if answer == "N" or answer == "n": 
        pass 
    if answer == "Y" or "answer" == "y": 
        start = int(input("Start from: "))
        end = int(input("End at: "))
        links = links[start:end]
    for i in links: 
        sleep(0.1)
        data.append(get_content(i))
    return data

def main(): 
    print("""\

 (                                     
 )\   (             )            (     
((_) ))\   (     ( /(     `  )   )\ )  
 _  /((_)  )\ )  )(_))    /(/(  (()/(  
| |(_))(  _(_/( ((_)_    ((_)_\  )(_)) 
| || || || ' \))/ _` | _ | '_ \)| || | 
|_| \_,_||_||_| \__,_|(_)| .__/  \_, | 
                         |_|     |__/
    """)

    ticker = sys.argv[1]
    links = fetch_urls(ticker)
    data = get_text(links)
    data = list(filter(None, data))
    compound_scores = []
    for text in data:
        if blacklist(text) == True: 
            pass
        else:  
            compound = analyze(text)
            compound_scores.append(compound)
            print("ARTICLE ANALYZED:")
            print("\033[1mSCORE: " + str(compound) + " " + defs[determine(compound)] + "\033[0m")
    print("\033[1mCOMPOUND POLARITY AVERAGE: " + "\033[104m\033[5m\033[1m" + str(mean(compound_scores)) + "\033[0m")
    print("\033[1mCURRENT MARKET SENTIMENT: " + defs[determine(mean(compound_scores))])
    exit()
main()

