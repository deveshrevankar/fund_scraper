class Locators:
    stock_details_locator = 'div#company_info > div:nth-child(4)'


class FundLocator:
    funds_table = '/html/body/section[2]/div/div/div[2]/div/div[4]/div/div/table[@id="dataTableId"]/tbody/tr[@role="row"]'
    name = 'td[1]/a'
    isin_locator = 'input#sel_isin_id'
