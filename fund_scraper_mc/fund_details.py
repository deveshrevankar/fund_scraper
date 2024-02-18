# Necessary library imports
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException, WebDriverException, TimeoutException
from static_data.static_inputs import StaticFundData


class FundScraper:
    def __init__(self, df: pd.DataFrame, details: StaticFundData, funds_present: pd.DataFrame = None, **kwargs: dict):
        self.all_fund_categories = df
        self.missing_url_dict = details.urls_where_missing
        self.fund_name_correction = details.fund_name_correction
        self.existing_funds = funds_present
        self.params = {
            'driver': kwargs['driver'],
            'table': kwargs['table'],
            'name': kwargs['name'],
            'wait': kwargs['wait'] if kwargs.get('wait') is not None else 3
        }
        self.isin_locator = kwargs['isin']
        self.error_while_fetching_isin = None
        self.new_funds = None
        self.funds_final = None

    @staticmethod
    def __get_fund_list__(url, category_id, **kwargs):
        n = 0
        while n < 10:
            try:
                print(url)
                kwargs['driver'].get(url)
                _1 = WebDriverWait(kwargs['driver'], kwargs['wait']).until(
                    ec.presence_of_all_elements_located((By.XPATH, kwargs['table']))
                )
                _1 = [e.find_element(By.XPATH, kwargs['name']) for e in _1]
                _1 = {e.get_attribute('textContent'): [e.get_attribute('href'), category_id] for e in _1}
                n = 10
                return _1
            except KeyError:
                print(f"KeyError raised, trying again")
                n += 1
            except TimeoutException:
                print(f"TimeoutException raised, trying again")
                n += 1

    @staticmethod
    def __fetch_isin__(fund_dict: dict, driver, isin_locator):
        error_while_fetching_isin = dict()

        for category, funds in fund_dict.items():
            error_while_fetching_isin[category] = dict()
            for name, details in funds.items():
                n = 0
                while n < 2:
                    isin = None
                    try:
                        driver.get(details[0])
                        isin = WebDriverWait(driver, 10).until(
                            ec.presence_of_element_located((By.CSS_SELECTOR, isin_locator))
                        )
                        isin = isin.get_attribute('value')
                        details.append(isin)
                        n = 2
                    except InvalidArgumentException:
                        n += 1
                        print('Raised InvalidArgumentException')
                    except WebDriverException:
                        n += 1
                        print('Raised WebDriverException')
                    finally:
                        if n >= 2 and isin is None:
                            error_while_fetching_isin[category].update({name: details})

        return fund_dict, error_while_fetching_isin

    def get_funds_in_category(self):
        funds_in_category = {i['id']: self.__get_fund_list__(i['url'], i['id'], **self.params) for i in
                             self.all_fund_categories.to_dict(orient='records')}
        _tdict = dict()
        for fund_category, funds in funds_in_category.items():
            _tdict[fund_category] = dict()
            for fund_name, data in funds.items():
                if fund_name in self.fund_name_correction.get(fund_category).keys():
                    _tdict[fund_category][
                        self.fund_name_correction.get(fund_category).get(fund_name)] = funds_in_category.get(
                        fund_category).get(fund_name)
                else:
                    _tdict[fund_category][fund_name] = funds_in_category[fund_category][fund_name]

        funds_in_category = _tdict.copy()
        del _tdict
        print(funds_in_category)

        for x in funds_in_category:
            _2 = dict()
            for fund in funds_in_category[x]:
                if funds_in_category[x][fund][0] == '':
                    try:
                        funds_in_category[x][fund][0] = self.missing_url_dict.get(x).get(fund)
                    except AttributeError:
                        funds_in_category[x][fund][0] = None

        funds_1 = dict()
        for category_id, funds in funds_in_category.items():
            funds_1[category_id] = dict()
            for name, details in funds.items():
                if name not in list(self.existing_funds['name']):
                    funds_1[category_id][name] = details

        # print(funds_1)

        self.new_funds = funds_1

    def fetch_isin(self):
        self.funds_final, self.error_while_fetching_isin = self.__fetch_isin__(self.new_funds,
                                                                               self.params.get('driver'),
                                                                               self.isin_locator)

    @property
    def new_funds(self):
        return self.__new_funds

    @new_funds.setter
    def new_funds(self, new_funds):
        self.__new_funds = new_funds
