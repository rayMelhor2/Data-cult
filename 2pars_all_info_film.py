from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time
import re

headers = {
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
}

final_list_9k = []

csvtable = pd.read_csv('табла всех фильмов.csv')


for urls in range(len(csvtable['url'])):
    url = str(csvtable['url'][urls])
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    print(url)

    if soup.find('div', class_='text text_inline text_light_medium text_fixed valign_baseline p-movie-info__description-text') != None:
        info_film = soup.find('div', class_='text text_inline text_light_medium text_fixed valign_baseline p-movie-info__description-text')
        paragraphs = info_film.find_all('p')
        text_film = '\n'.join([p.get_text() for p in paragraphs])
    else:
        text_film = False

    if soup.find('span', class_='label label_restrict valign_top') != None:
        yo = soup.find('span', class_='label label_restrict valign_top')
        years_old = yo.get_text(strip=True)
    else:
        years_old = False

    if soup.find('h1', class_='text text_bold_giant color_white') != None:
        name = soup.find('h1', class_='text text_bold_giant color_white').get_text(strip=True)
    else:
        name = False

    if soup.find_all('span', class_='text text_bold_medium text_fixed') != []:
        imdb_rate = soup.find_all('span', class_='text text_bold_medium text_fixed')
        imdb_match = re.search(r'\d+\.\d+', str(imdb_rate))
        imdb_match = imdb_match.group(0)
    else:
        imdb_match = False

    if soup.find_all('span', class_='badge__text') != None:
        theme = soup.find_all('span', class_='badge__text')
        themes = [span.get_text(strip=True) for span in theme]
    else:
        themes = False

    if soup.find_all('span', class_='nowrap') != None:
        a = soup.find_all('span', class_='nowrap')
        year_published = re.search(r'\b\d{4}\b', str(a)).group(0)
    else:
        year_published = False

    print(text_film)
    print(years_old)
    print(name)
    print(imdb_match)
    print(themes)
    print(year_published)

    alphabetic = {'Url':url,'Name':name,'Description':text_film,'Theme':themes,'Published':year_published,'IMDb rate':imdb_match,'years old':years_old}
    final_list_9k.append(alphabetic)
    time.sleep(1)

df = pd.DataFrame(final_list_9k)
df.to_csv('dataset.csv')
