from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service


class CD(Chrome):
    def __init__(self, headless=True):
        options = ChromeOptions()
        options.headless = headless
        super().__init__(options=options)
