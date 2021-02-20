# script date: 20 February 2021
import re
import json
import csv
from io import StringIO
from bs4 import BeautifulSoup
from pip._vendor import requests

url_stats = 'https://finance.yahoo.com/quote/{}/key-statistics?p={}'
url_profile = 'https://finance.yahoo.com/quote/{}/profile?p={}'
url_financial = 'https://finance.yahoo.com/quote/{}/financials?p={}'

# put your stock name here
stock = 'ASII.JK'

response = requests.get(url_financial.format(stock, stock))

soup = BeautifulSoup(response.text, 'html.parser')

# cari /* -- Data -- */
# ketika script ini dibuat ada di line 58 dari view source
# yang dicari adalah tag --> /* -- Data -- */
pattern = re.compile(r'\s--\sData\s--\s')
script_data = soup.find('script', text=pattern).contents[0]

# beginning
script_data[:500]

# the end
script_data[-500:]

# tentukan posisi awal pengambilan data
# titik awal adalah dua karakter setelah "context" sedangkan titik akhir adalah sebelum 12 karakter terakhir
start = script_data.find("context")-2

# slice the json string
json_data = json.loads(script_data[start:-12])

# cari kata kunci di dalam tag "context"
json_data['context'].keys()
# output: dict_keys(['dispatcher', 'options', 'plugins'])

# dari output tersebut kemudian dicari lagi sub-keys untuk mendapatkan data detil
json_data['context']['dispatcher']['stores']['QuoteSummaryStore'].keys()
# output dari script tersebut
# dict_keys(['financialsTemplate', 'cashflowStatementHistory', 'balanceSheetHistoryQuarterly', 'earnings', 'price',
# 'incomeStatementHistoryQuarterly', 'incomeStatementHistory', 'balanceSheetHistory',
# 'cashflowStatementHistoryQuarterly', 'quoteType', 'summaryDetail', 'symbol', 'pageViews'])

# ekstrak data
# income statement
annual_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistory']['incomeStatementHistory']
quarterly_is = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['incomeStatementHistoryQuarterly']['incomeStatementHistory']

# cash flow statement
annual_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistory']['cashflowStatements']
quarterly_cf = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['cashflowStatementHistoryQuarterly']['cashflowStatements']

# balance sheet
annual_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistory']['balanceSheetStatements']
quarterly_bs = json_data['context']['dispatcher']['stores']['QuoteSummaryStore']['balanceSheetHistoryQuarterly']['balanceSheetStatements']

# there's a variety of  number formats provided
operating_income = annual_is[0]['operatingIncome']

# rapikan format untuk output dengan menggunakan fungsi perulangan 'for'
# ambil hanya data annual statement saja.
annual_is_stmts = []

# consolidate annual
for s in annual_is:
    statement = {}
    for key, val in s.items():
        try:
            statement[key] = val['raw']
        except TypeError:
            continue
        except KeyError:
            continue
    annual_is_stmts.append(statement)

# export to scv
# extract the csv data
file = StringIO(response.text)
reader = csv.reader(file)
data = list(reader)

# show the first 5 records
for row in data[:5]:
    print(row)
