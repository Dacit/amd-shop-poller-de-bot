from _datetime import datetime
import logging
import sys
from typing import Dict

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from model import Model

logger = logging.getLogger('poll')
logger.setLevel(logging.INFO)


class Poller:
    base_url = 'https://www.amd.com'
    user_agent =\
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    def __init__(self, model: Model):
        self.model = model
        self.last_update = None
        # Configure browser
        options = Options()
        options.headless = True
        options.add_argument(f'user-agent={Poller.user_agent}')
        options.add_argument("--no-sandbox")
        chrome_path = chromedriver_autoinstaller.install()
        logger.info(f"Chrome at: {chrome_path}")
        # Start session
        self.browser = webdriver.Chrome(options=options)
        self.browser.get(Poller.base_url + '/de/direct-buy/de')

    def poll(self) -> Dict[str, bool]:
        new_avails = {}
        old_state = self.model.read_products()
        self.browser.refresh()
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        prods = soup.find_all('div', class_='direct-buy')
        if len(prods) == 0:
            raise ConnectionError(f'Could not get file: {soup}')
        for prod in prods:
            name = str(prod.find('div', class_='shop-title').text.strip())
            avail = 'Out of Stock' not in prod.find('div', class_='shop-links').text
            url = prod.find('div', class_='shop-full-specs-link').find("a", recursive=False).get('href')
            if avail and name not in old_state:
                logger.info('Found item: %s', name)
                new_avails[name] = Poller.base_url + url
                self.model.add_product(name)
            elif name in old_state and not avail:
                self.model.delete_product(name)
        self.last_update = datetime.now().strftime("%d %B, %Y %H:%M:%S")
        return new_avails


if __name__ == '__main__':
    if len(sys.argv) > 1:
        model = Model(sys.argv[1])
    else:
        model = Model('bot.sqlite')

    print(Poller(model).poll())
