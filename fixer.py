from datetime import datetime
from typing import List, TypeVar

import requests

BASE_URL = 'https://api.fixer.io/'
CURRENCY_CHOICE = ["EUR", "AUD", "BGN", "BRL", "CAD", "CHF", "CNY", "CZK",
                   "DKK", "GBP", "HKD", "HRK", "HUF", "IDR", "ILS",
                   "INR", "JPY", "KRW", "MXN", "MYR", "NOK", "NZD",
                   "PHP", "PLN", "RON", "RUB", "SEK", "SGD", "THB",
                   "TRY", "USD", "ZAR"]

D = TypeVar('D', datetime, str)


class Fixer(object):

    """
    class definining the api

        date:
                Either a date in "yyyy-mm-dd" format (available from 1999)
                either "latest" for latest date
                default = "latest"

        base:
                A currency in CURRENCY_CHOICE list.
                Will setup the base currency for conversion
                default = "EUR"

                Will raise a ValueError exception

    """

    def __init__(self, date: str = "latest", base: str = "EUR",
                 symbols: List[str] = None) -> None:
        super(Fixer, self).__init__()
        self.symbols_string = ''
        if self.currency_available(base, "Base currency"):
            self.base = base

        if symbols:
            self.symbols = []

            for cur in symbols:
                if self.currency_available(cur, "Symbols currency"):
                    self.symbols.append(cur)

            self.symbols_string = 'symbols={}'.format(','.join(self.symbols))

        self.check_date(date)

    def currency_available(self, cur: str, method: str = "") -> bool:
        if cur not in CURRENCY_CHOICE:
            # Raise a ValueError exception
            raise ValueError("Currency %s not available through this api" % cur,
                             method)
        else:
            return True

    def check_date(self, dt: D) -> None:
        if type(dt) == datetime:
            self.date = dt
        elif type(dt) == str:
            if dt == "latest":
                self.date = dt
            else:
                try:
                    self.date = datetime.strptime(dt, "%Y-%m-%d")
                except ValueError as e:
                    raise e

                if not self.date.year >= 1999:
                    raise ValueError("Data available from 1999, %s is to old" % self.date.strftime("%Y-%m-%d"))

                if self.date > datetime.now():
                    raise ValueError("%s is in the future, data cannot be found" % self.date.strftime("%Y-%m-%d"))
        else:
            raise ValueError("%s does not match required date format" % dt)

    def convert(self) -> str:
        url = '%s%s?%s&base=%s' % (BASE_URL, self.date, self.symbols_string, self.base)
        r = requests.get(url).json()

        if 'error' in r:
            raise ReferenceError(r['error'])
        return r
