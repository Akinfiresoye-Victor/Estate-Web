from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError
import re



ue= UserAgent().random
url="https://www.nigeriahousingmarket.com/real-estate-news-nigeria/"
headers={"User-Agent": ue}
req= Request(url, headers=headers)
html=urlopen(req)
bs=BeautifulSoup(html, 'lxml')

article_headline_raw=bs.find("a", class_="summary-title-link")
article_headline= article_headline_raw.text

headlines = [h.get_text(strip=True) for h in bs.find("a", class_="summary-title-link")]
article_urls = []
for headline in headlines:
    slug = article_headline_raw['href']
    full_url = f"https://www.nigeriahousingmarket.com{slug}"
    article_urls.append(full_url)
for article in article_urls:
    url=article
    headers={"User-Agent":ue}
    req= Request(url,headers=headers)
html=urlopen(req)
bs=BeautifulSoup(html, 'lxml')


