import logging
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


class Poller:
    base_url = 'https://www.amd.com'

    def __init__(self, executable_path='geckodriver'):
        options = Options()
        options.headless = True
        self.browser = webdriver.Firefox(executable_path=executable_path, options=options)
        self.browser.get(Poller.base_url + '/de/direct-buy/de')
        self.state = {}

    def poll(self):
        new_avails = {}
        self.browser.refresh()
        soup = BeautifulSoup(self.browser.page_source, "html.parser")
        prods = soup.find_all('div', class_='direct-buy')
        if len(prods) == 0:
            raise ConnectionError(f'Could not get file: {soup}')
        for prod in prods:
            name = str(prod.find('div', class_='shop-title').text.strip())
            avail = 'Out of Stock' not in prod.find('div', class_='shop-links').text
            url = prod.find('div', class_='shop-full-specs-link').find("a", recursive=False).get('href')
            if avail and not self.state.get(name):
                logger.info('Found item: %s', name)
                new_avails[name] = Poller.base_url + url
            self.state[name] = avail
        return new_avails


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python poll.py <GECKODRIVER_PATH>")
        exit(1)
    poller = Poller(sys.argv[1])
    print(poller.poll())
