from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from tdameritrade_ext.client import TDClient
import time

if __name__ == '__main__':

    c = TDClient()
    data = c.options('AAPL', fromDate=time.strftime("%Y-%m-%d"))

    print(data)



