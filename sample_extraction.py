from functions import *

with open("sp500-isin-list.txt", 'r') as file:
    sp500_isins = file.read().split('\n')
    sp500_isins = [x for x in sp500_isins if x]


german_companies = get_companies_from("DE")
german_isins = list(german_companies.ISIN)

start_date = "2019-01-01"
#get_stock_returns(sp500_isins, start_date, "D")
#get_market_cap_data(sp500_isins, start_date)
#get_climate_indicators(sp500_isins, start_date)

get_business_sectors(german_isins, start_date)
get_cusips(german_isins, start_date)

exit()

