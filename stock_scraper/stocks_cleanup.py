import numpy as np
import pandas as pd


class AllStocks:
    def __init__(self, df: pd.DataFrame, field_qc: dict, stockwise_qc: dict, excl: list, fno: list):
        self.df = df
        self.field_qc = field_qc
        self.stockwise_qc = stockwise_qc
        self.cleaned_df = None
        self.excl = excl
        self.fno = fno

    @staticmethod
    def __get_list_index(list_to_check: list, position: int):
        try:
            return list_to_check[position].strip()
        except IndexError:
            return []

    @classmethod
    def _clean_stock_data(cls, df_raw: pd.DataFrame, f_qc: dict, st_qc: dict, excl: list, fno: list):

        df_raw = df_raw.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        df_raw.drop_duplicates(inplace=True)

        for i, replacements in f_qc.items():
            for j, k in replacements.items():
                df_raw[i].replace(j, k, inplace=True)

        for l, replacements in st_qc.items():
            for m, n in replacements.items():
                df_raw.loc[df_raw['Stock Invested in '].isin([m]), l] = n

        df_raw.drop_duplicates(inplace=True)

        df_raw_copy = df_raw.copy(deep=True)
        df_raw_copy.replace(np.NaN, '', inplace=True)
        df_raw_copy = df_raw_copy.groupby('Stock Invested in ')['Url'].apply(','.join)
        df_raw_copy = df_raw_copy.apply(lambda x: list(set(x.split(','))))
        df_raw_copy = df_raw_copy.apply(lambda x: max(x))
        df_raw_copy = df_raw_copy.reset_index()
        df_raw = df_raw.merge(df_raw_copy, on='Stock Invested in ')
        df_raw.drop('Url_x', axis=1, inplace=True)
        df_raw.columns = ['Stock Invested in ', 'Sector ', 'Url']

        df_raw.drop_duplicates(inplace=True)

        for i in fno:
            df_raw = df_raw.loc[df_raw['Stock Invested in '].isin([stock_name for stock_name in list(df_raw['Stock Invested in ']) if cls.__get_list_index(stock_name.split(':'), 1) != i])]
        df_raw = df_raw.loc[df_raw['Stock Invested in '].isin([stock_name for stock_name in list(df_raw['Stock Invested in ']) if stock_name not in excl])]
        # df_raw['Url'].replace('https://www.moneycontrol.com/india/indexfutures/nifty/9', '', inplace=True)

        return df_raw

    def get_cleaned_stocks(self):
        if all([True for g in self.df.columns if g in ['Stock Invested in ', 'Sector ', 'Url']]):
            self.cleaned_df = self._clean_stock_data(self.df, self.field_qc, self.stockwise_qc, self.excl, self.fno)
            return self.cleaned_df
        else:
            print('Dataframe passed is not a valid, please check columns and try again')
