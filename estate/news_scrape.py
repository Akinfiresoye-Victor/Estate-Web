import re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError





ue= UserAgent().random
url="https://www.nigeriahousingmarket.com/"
headers={"User-Agent": ue}
req= Request(url, headers=headers)
try:
    html1=urlopen(req)
except HTTPError:
    error= f"Error Retreiving data"
except URLError:
    error= "Server not found"
bs=BeautifulSoup(html1, 'lxml')
profile_headline= bs.find('h4', style="white-space:pre-wrap;")
profile_headline=profile_headline.text





headlines = [h.get_text(strip=True) for h in bs.find("h4")]
article_urls = []
for headline in headlines:
    slug = re.sub(r'[^a-z0-9]+', '-', headline.lower()).strip('-')
    full_url = f"https://www.nigeriahousingmarket.com/interviews-opinions/{slug}"
    article_urls.append(full_url)
    
for article in article_urls:
    url=article
    headers={"User-Agent":ue}
    req= Request(url,headers=headers)
try:
    html=urlopen(req)
except HTTPError:
    error= f"Error Retreiving data"
except URLError:
    error= "Server not found"
bs=BeautifulSoup(html, 'lxml')