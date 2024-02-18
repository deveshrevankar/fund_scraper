from selenium.webdriver import Chrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By


class EquityTable:
    def __init__(self, driver: Chrome, header_locator: str, rows_locator: str) -> None:
        self.driver = driver
        self.header_locator = header_locator
        self.rows_locator = rows_locator
        self.timeout = 10

        self.h = None
        self.r = None

    @staticmethod
    def __fetch_headers(driver: Chrome, timeout: int, header_locator: str):
        _c = WebDriverWait(driver, timeout).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, header_locator))
        )
        _c = [e.get_attribute('textContent') for e in _c]
        _c.append('Url')
        _c.insert(0, 'status')
        return _c

    @staticmethod
    def __fetch_rows(driver: Chrome, timeout: int, rows_locator: str):
        _r = WebDriverWait(driver, timeout).until(
            ec.presence_of_all_elements_located((By.CSS_SELECTOR, rows_locator))
        )
        return _r

    def get_headers(self):
        self.h = self.__fetch_headers(self.driver, self.timeout, self.header_locator)
        return self.h

    def get_rows(self):
        self.r = self.__fetch_rows(self.driver, self.timeout, self.rows_locator)
        self.r = [a for a in self.r if len([b.get_attribute('textContent') for b in a.find_elements(By.CSS_SELECTOR, 'td')]) > 1]
        # _r1 = [a for a in self.r if len([b.get_attribute('textContent') for b in a.find_elements(By.CSS_SELECTOR, 'td')]) > 1]
        _r2 = []

        for i in range(len(self.r)):
            _r3 = []
            _y3 = None
            for j in range(len(self.r[i].find_elements(By.CSS_SELECTOR, 'td'))):
                if j == 0:
                    _y1 = self.r[i].find_elements(By.CSS_SELECTOR, 'td')[j]
                    _y2 = _y1.find_elements(By.CSS_SELECTOR, 'span')
                    _y2 = [a.get_attribute('textContent') for a in _y2]
                    _y3 = _y1.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                    for l in _y2:
                        _r3.append(l)
                else:
                    _r3.append(self.r[i].find_elements(By.CSS_SELECTOR, 'td')[j].get_attribute('textContent'))
            _r3.append(_y3)
            _r2.append(_r3)

        for t in range(len(_r2)):
            if len(_r2[t]) == 10:
                _r2[t].insert(0, 'Exit')
        self.r = _r2
        # return _r2
        return self.r

