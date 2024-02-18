import json

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidArgumentException, WebDriverException


class StockMetaInfo:
    def __init__(self, all_stocks_df: pd.DataFrame, locator: str, driver: webdriver):
        all_stocks_df['meta_info'] = np.NaN
        self.all_stocks_df = all_stocks_df.to_dict('records')
        self.locator = locator
        self.driver = driver
        self.all_stocks_meta = None

    @staticmethod
    def __stock_meta_info_scraper(all_stocks_df: list[dict], locator: str, driver: webdriver):
        for s_no, stock_dict in enumerate(all_stocks_df):
            n = 0
            if stock_dict.get('Url') in ('', 'NULL'):
                pass
            else:
                while n < 10:
                    try:
                        driver.get(stock_dict.get('Url'))

                        _t1 = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, locator))
                        ).get_attribute('textContent')

                        print(_t1)

                        stock_dict['meta_info'] = _t1
                        n = 10
                    except (TimeoutException, InvalidArgumentException, WebDriverException):
                        print('Fetch failed, trying again')
                        n += 1

        return pd.DataFrame(all_stocks_df)

    def get_stock_meta_info(self):
        self.all_stocks_meta = self.__stock_meta_info_scraper(self.all_stocks_df, self.locator, self.driver)
        # self.all_stocks_meta = self.all_stocks_meta.replace(np.NaN, 'NULL', inplace=True)
        self.all_stocks_meta['meta_info'] = self.all_stocks_meta['meta_info'].apply(lambda x: str(x).replace(r'\n', ''))
        return self.all_stocks_meta


class StockIdentifiers:
    def __init__(self, str_dict: str):
        if str_dict is None:
            print(str_dict)
            self.dict = dict()
        else:
            print(str_dict)
            str_dict = str_dict.replace('\n', '')
            str_dict = json.loads(str_dict)
            self.dict = str_dict

        def check_element_exists(__get_element):
            def inner(from_dict: dict, element_name: str):
                try:
                    return __get_element(from_dict, element_name)
                except AttributeError:
                    return 'NULL'

            return inner

        @check_element_exists
        def __get_element(from_dict: dict, element_name: str):
            return from_dict.get('data').get('details').get(element_name)

        self.isin = __get_element(self.dict, 'isinid')
        self.bse_id = __get_element(self.dict, 'bseId')
        self.nse_id = __get_element(self.dict, 'nseId')
        self.series = __get_element(self.dict, 'series')
