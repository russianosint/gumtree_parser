# -*- coding: utf-8 -*-
import pyfiglet
from colorama import init, Fore
import logging 
import fake_useragent
import collections
import csv

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('gumtree')

ParseResult = collections.namedtuple(
  'ParseResult',
  (
    'brand_name',
    'goods_name',
    'url',
    'price',
  ),
)

HEADERS = (
  'Бренд',
  'Товар',
  'Ссылка',
)

class Client:

  def __init__(self):
    self.session = requests.Session()
    self.session.headers = {
      'User-Agent': fake_useragent.UserAgent().random,
      'Accept-Language': 'us',
    }
    self.result = []

  def banner(self):
    banner = pyfiglet.figlet_format("Tg: @kohags")
    print(Fore.YELLOW + banner)

  def load_page(self):
    url = str(input('Введите ссылку(желательно раздел: For sale): '))
    res = self.session.get(url=url)
    res.raise_for_status()
    return res.text

  def parse_page(self, text: str):
    soup = BeautifulSoup(text, 'lxml')
    container = soup.select('article.listing-maxi')
    for block in container:
      self.parse_block(block=block)

  def parse_block(self, block):

    url_block = block.select_one('a.listing-link')
    if not url_block:
      logger.error('no url_block')
      return

    url = url_block.get('href')
    if not url:
      logger.error('no href')
      return

    name_block = block.select_one('div.listing-content')
    if not name_block:
      logger.error(f'no name_block of {url}')
      return

    brand_name = block.select_one('h2.listing-title')
    if not brand_name:
      logger.error(f'no brand_name of {url}')
      return
    
    # Wrangel
    brand_name = brand_name.text
    brand_name = brand_name.replace('/','').strip()

    goods_name = name_block.select_one('span.truncate-line')
    if not goods_name:
      logger.error(f'no goods_name on {url}')
      return
    
    goods_name = goods_name.text.strip()

    price_block = name_block.select_one('div.listing-price-posted-container')
    if not price_block:
      logger.error(f'no price_block on {url}')
      return

    price = price_block.select_one('strong.h3-responsive')
    if not price:
      logger.error(f'no price on {url}')
      return

    price = price.text.strip()

    self.result.append(ParseResult(
      url={'https://www.gumtree.com'+url},
      brand_name=brand_name,
      goods_name=goods_name,
      price=price,
    ))

    logger.debug('%s, %s, %s, %s', f'https://www.gumtree.com{url}', brand_name, goods_name, price)
    logger.debug('-' * 100)

  def save_result(self):
    path = 'output.csv'
    with open(path, 'w', encoding='utf-8') as f:
      writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
      writer.writerow(HEADERS)
      for item in self.result:
        writer.writerow(item)

  def run(self):
    self.banner()
    text = self.load_page()
    self.parse_page(text=text)
    self.save_result()
    logger.info(f'Получили {len(self.result)} элементов')




if __name__ == "__main__":
  parser = Client()
  parser.run()
