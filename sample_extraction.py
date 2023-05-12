from functions import *

# get list of company codes from custom text file
with open("sp500-isin-list.txt", 'r') as file:
    sp500_isins = file.read().split('\n')
    sp500_isins = [x for x in sp500_isins if x]

# fetch company codes for a given country from eikon
german_companies = get_companies_from("DE")
german_isins = list(german_companies.ISIN)

# sample data extracts using the two lists of isin codes and a given start date
start_date = "2019-01-01"
get_stock_returns(sp500_isins, start_date, "D")
get_market_cap_data(sp500_isins, start_date)
get_climate_indicators(sp500_isins, start_date)

get_business_sectors(german_isins, start_date)
get_cusips(german_isins, start_date)

get_bond_returns(["CH0031240127", "XS1614096425", "US099109017"], start_date)

exit()
