from datetime import datetime as dt
import numpy as np
import pandas as pd
from decimal import *


class AllPositions:
    def __init__(self, holdings: pd.DataFrame, field_qc: dict, stockwise_qc: dict, excl: list, fno: list,
                 stock_df: pd.DataFrame = None):
        holdings = holdings.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        self.holdings = holdings
        self.field_qc = field_qc
        self.stockwise_qc = stockwise_qc
        self.excl = excl
        self.fno = fno
        self.stock_df = stock_df

    @classmethod
    def _decimal_correction(cls, string: str):
        try:
            zero_dict = {
                'L': 100000,
                'k': 1000,
                'Cr': 10000000
            }
            split_string = str(string)
            split_string = split_string.split(' ')
            split_string = [zero_dict.get(a) if a in zero_dict.keys() else a for a in split_string]
            split_string = [Decimal(a) if isinstance(a, str) else a for a in split_string]
            return str(int(np.prod(split_string)))
        except (ValueError, InvalidOperation):
            return 'NULL'

    @classmethod
    def _date_parse(cls, string: str, dt_pattern: str = '%b %Y'):
        try:
            return dt.strptime(string, dt_pattern)
        except ValueError:
            return np.NaN

    @classmethod
    def _get_list_index(cls, list_to_check: list, position: int):
        try:
            return list_to_check[position].strip()
        except IndexError:
            return []

    def get_cleaned_positions(self):
        # Remove leading and trailing spaces from all str data types
        self.holdings = self.holdings.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        # Field correction replacements
        for i, replacements in self.field_qc.items():
            for j, k in replacements.items():
                self.holdings[i].replace(j, k, inplace=True)

        # Correction by individual stocks
        for l, replacements in self.stockwise_qc.items():
            for m, n in replacements.items():
                self.holdings.loc[self.holdings['Stock Invested in '].isin([m]), l] = n

        # Convert '1.2 k' string to 1200.00
        self.holdings[
            ['Quantity ', '1M Change in Qty ']
        ] = self.holdings[['Quantity ', '1M Change in Qty ']].applymap(lambda x: self._decimal_correction(x))

        # # Converting 'Value(Mn) ' numbers from Mn to '000s
        self.holdings['Value(Mn) '] = self.holdings['Value(Mn) '].apply(lambda x: str(x))
        self.holdings['Value(Mn) '] = self.holdings['Value(Mn) '].apply(lambda x: int(Decimal(x) * 1000))

        # Getting the second part of '11.72% (Jan 22)' by splitting the string by '(' character
        self.holdings['1Y Highest Holding (Month)'] = self.holdings['1Y Highest Holding '].apply(
            lambda x: x.split('(')[1] if len(x.split('(')) > 1 else x)
        self.holdings['1Y Lowest Holding (Month)'] = self.holdings['1Y Lowest Holding '].apply(
            lambda x: x.split('(')[1] if len(x.split('(')) > 1 else x)

        # Parsing the string 'Jan 22)' into datetime
        self.holdings[
            ['1Y Highest Holding (Month)', '1Y Lowest Holding (Month)']
        ] = self.holdings[['1Y Highest Holding (Month)', '1Y Lowest Holding (Month)']].applymap(
            lambda x: self._date_parse(x.replace(')', ''))
        )

        self.holdings[
            ['1Y Highest Holding (Month)', '1Y Lowest Holding (Month)']
        ] = self.holdings[['1Y Highest Holding (Month)', '1Y Lowest Holding (Month)']].applymap(
            lambda x: 'NULL' if pd.isnull(x) else x
        )

        # Retain only the first part of the string when you split the pattern 11.72% (Jan 22) by '(' character
        self.holdings[
            ['1Y Highest Holding ', '1Y Lowest Holding ']
        ] = self.holdings[['1Y Highest Holding ', '1Y Lowest Holding ']].applymap(
            lambda x: x.split('(')[0] if len(x.split('(')) > 1 else '-'
        )

        # Remove % sign from these columns
        self.holdings[
            ['1Y Lowest Holding ', '1Y Highest Holding ', '% of Total Holdings ', '1M Change ']
        ] = self.holdings[
            ['1Y Lowest Holding ', '1Y Highest Holding ', '% of Total Holdings ', '1M Change ']
        ].applymap(lambda x: x.replace('%', ''))

        # Convert these columns to decimal.Decimal
        self.holdings[
            ['1Y Lowest Holding ', '1Y Highest Holding ', '% of Total Holdings ', '1M Change ']
        ] = self.holdings[
            ['1Y Lowest Holding ', '1Y Highest Holding ', '% of Total Holdings ', '1M Change ']
        ].applymap(lambda x: Decimal(x) if x != '-' else 'NULL')

        # Converting Sector name to lowercase for mapping
        self.holdings['Sector '] = self.holdings['Sector '].apply(lambda x: x.lower())

        # Correcting status column by removing '-' and replacing empty spaces. '#' will become new
        self.holdings['status'] = self.holdings['status'].apply(
            lambda x: '' if isinstance(x, float) else x.replace('-', '')
        )
        self.holdings['status'] = self.holdings['status'].apply(
            lambda x: '' if isinstance(x, float) else x.replace(' ', '')
        )
        self.holdings['status'] = self.holdings['status'].apply(
            lambda x: '' if isinstance(x, float) else x.replace('#', 'New')
        )
        self.holdings['status'] = self.holdings['status'].apply(
            lambda x: 'NULL' if x == '' else x
        )

        # Excluding positions in short term instruments
        self.holdings = self.holdings[
            ~self.holdings['Stock Invested in '].isin(self.excl)
        ]

        # Excluding F&O positions from the data
        for fno in self.fno:
            self.holdings = self.holdings[
                self.holdings['Stock Invested in '].isin(
                    [stock_name for stock_name in list(self.holdings['Stock Invested in ']) if
                     self._get_list_index(stock_name.split(':'), 1) != fno]
                )
            ]

        # Industry ID mapping to positions dataframe
        self.holdings = self.holdings.merge(
            self.stock_df, how='left', left_on='Stock Invested in ', right_on='name'
        )

        # Drop duplicate rows from table
        self.holdings = self.holdings.drop_duplicates()

        # # Remove NaN
        # self.holdings = self.holdings.fillna('NULL')

        # Keep these columns
        self.holdings = self.holdings[['status', 'Stock Invested in ',
                                       'id',
                                       'Sector ', 'Value(Mn) ',
                                       '% of Total Holdings ', '1M Change ', '1Y Highest Holding ',
                                       '1Y Highest Holding (Month)',
                                       '1Y Lowest Holding ', '1Y Lowest Holding (Month)', 'Quantity ',
                                       '1M Change in Qty ', 'Url',
                                       'funds_category_id', 'funds_id', 'date']
        ]

        return self.holdings
