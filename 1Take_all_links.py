from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

headers = {
    'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15'
}

sinema_url = []
sinema_photo = []

trashpath = 'https://kino.mail.ru/cinema/total/'
trashpage = requests.get(trashpath,headers=headers,timeout=1)
metasoup = BeautifulSoup(trashpage.text, "html.parser")
page_count_all = metasoup.find_all('a',class_='p-pager__list__item')[-1].text

for page in range(int(page_count_all)):
    path = 'https://kino.mail.ru/cinema/total/?page='+str(page)
    page = requests.get(path,headers=headers)
    soup = BeautifulSoup(page.text, "html.parser")
    bss = soup.find_all('a', class_='link link_inline color_black link-holder link-holder_itemevent link-holder_itemevent_small')
    image = soup.find_all('div', class_='cols__column cols__column_small_percent-100 cols__column_medium_percent-50 cols__column_large_percent-50')
    img_tag = soup.find_all('img', class_='picture__image')
    for i in range(len(bss)):
        sinema_url.append('https://kino.mail.ru'+bss[i]['href'])
        sinema_photo.append(img_tag[i]['src'])
    time.sleep(2)

print(sinema_photo,len(sinema_photo))
print(sinema_url,len(sinema_url))
data = {'Url': sinema_url, 'photo':sinema_photo}
df = pd.DataFrame(data)
df.to_csv('output.csv')
