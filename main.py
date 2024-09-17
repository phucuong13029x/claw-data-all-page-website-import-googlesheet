from bs4 import BeautifulSoup
import requests


def retext(text:str):
  return text.replace('\n', '').replace('\r', '').replace('  ','')


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
headers = {'User-agent': user_agent}
response = requests.get(url='https://www.nehnutelnosti.sk/okres-bratislava-i/predaj/', headers=headers)
main = BeautifulSoup(response.text, 'html.parser')
ul = main.find('ul', class_='component-pagination__items d-flex align-items-center')
li_items = ul.find_all('li') if ul else []
pagination = int(li_items[-2].text)

result = []
index = 0
try:
  for i in range(pagination):
    index = len(result)
    print(f'[-] Get data page {i + 1}')
    url_page = "https://www.nehnutelnosti.sk/okres-bratislava-i/predaj/?p[page]={page}".format(page=str(i))
    response = requests.get(url=url_page, headers=headers)
    main = BeautifulSoup(response.text, 'html.parser')
    select_id_main = main.select('div#inzeraty')
    get_all_item = select_id_main[0].select('div.advertisement-item')
    for j in get_all_item:
      item_result = {}
      # get thumbnail
      list_image = j.select('img')
      link_image = ""
      for k in list_image:
        link = k.get('src')
        if link[int(link.rfind('.')):] != '.svg':
          link_image = link
          break
      item_result['thumbnail'] = link_image
      # get title
      title = j.select('a.advertisement-item--content__title')[0].text
      item_result['title'] = title
      # get info
      info = j.select('div.advertisement-item--content__info')
      item_result['address'] = retext(info[0].text)
      # label
      labels = retext(info[1].text)
      if labels.find('•') != -1:
        labels = labels.split('•')
        item_result['label'] = labels[0]
        item_result['acreage'] = labels[1]
      else:
        item_result['label'] = labels
        item_result['acreage'] = None
      # description
      description = j.select('div.advertisement-item--content__text')[0].text
      item_result['description'] = retext(description)
      # price
      price = j.select('div.advertisement-item--content__price')[0]['data-adv-price']
      item_result['price'] = retext(price)
      try:
        if j.select('div.advertisement-item--content__price')[0].select('span'):
          item_result['unit'] = j.select('div.advertisement-item--content__price')[0].select('span')[0].text
        else:
          item_result['unit'] = None
      except Exception as e:
        print(f'[?] Error: {e}')
      result.append(item_result)
    print(f'[+] Total data page {i + 1}: {len(result) - index}')
except Exception as e:
  print(f'[?] Error: {e}')
print(f'[+] Total: {len(result)}')
print(f'[+] Result: {result}')


from google.colab import auth
import gspread
from google.auth import default

auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)
sh = gc.create('New spreadsheet')
worksheet = gc.open('New spreadsheet').sheet1
header = result[0].keys()
worksheet.insert_row(list(header))
for dict in result:
  values = list(dict.values())
  worksheet.insert_row(values, 2)
