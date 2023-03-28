import contextlib
import pathlib
from typing import List
import eikon as ek
import math
import pandas as pd
import time


def get_stock_return_extractor(isins, freq="D"):
    """
        :param isins: list of isins
        :param freq: "D" (daily) or "Mo" (monthly)
        :return:
    """
    return_cols = [f"TR.TotalReturn1{freq}.Date", f"TR.TotalReturn1{freq}"]
    block_size = 10 if freq == "D" else 100
    return EikonDataExtractor(isins, "stock_returns", return_cols, freq[0], block_size=block_size, precision=6)


def get_market_cap_extractor(isins):
    market_cap_cols = ["TR.CompanyMarketCap.Date", "TR.CompanyMarketCap"]
    return EikonDataExtractor(isins, "market_cap", market_cap_cols, "M", block_size=200, precision=0)


def get_indicator_extractor(isins):
    indicator_cols = ["TR.TRESGScore.Date", "TR.TRESGScore", "TR.TRESGEmissionsScore", "TR.TRESGInnovationScore",
                      "TR.TRESGResourceUseScore", "TR.CO2DirectScope1", "TR.CO2IndirectScope2", "TR.CO2IndirectScope3",
                      "TR.TRESGManagementScore", "TR.TRESGShareholdersScore", "TR.TRESGCSRStrategyScore",
                      "TR.TRESGWorkforceScore", "TR.TRESGHumanRightsScore", "TR.TRESGCommunityScore",
                      "TR.TRESGProductResponsibilityScore"]
    return EikonDataExtractor(isins, "indicators", indicator_cols, "FY", block_size=1000, precision=2)


def get_cusip_extractor(isins):
    return EikonDataExtractor(isins, "cusips", ["TR.CUSIPExtended"], frequency="FY", block_size=1000)


def get_business_sector_extractor(isins):
    industry_sector_cols = ["TR.TRBCEconSectorCode", "TR.TRBCBusinessSectorCode", "TR.TRBCIndustryGroupCode",
                            "TR.TRBCIndustryCode", "TR.TRBCActivityCode"]
    return EikonDataExtractor(isins, "trbc", industry_sector_cols, frequency="FY", block_size=1000)


def get_isins(country, filename):
    u_string = "U(IN(Equity(active,public,primary))/*UNV:Public*/)"
    screen_string = f'SCREEN({u_string}, IN(TR.HQCountryCode,"{country}"), CURN=USD)'
    instrument_cols = ["TR.ISINCode", "TR.CommonName,TR.HeadquartersCountry,TR.CompanyMarketCap"]

    ec = EikonDataExtractor(r"G:/data/climate-risk/eikon/")
    df, _ = ek.get_data(screen_string, instrument_cols)
    cleansed_df = df.drop_duplicates().dropna(how="all")
    cleansed_df = cleansed_df.rename(columns={"ISIN Code": "ISIN", "Instrument": "Ticker"})
    cleansed_df["ISIN"].to_csv(f"{ec.data_path}/isins/{filename}.csv", index=False, header=False)
    cleansed_df.to_csv(f"{ec.data_path}/isins/{filename}_full_df.csv", index=False, header=False)


class EikonDataExtractor:

    col_name_dict = {
        "Instrument": "ISIN",
        "CUSIP (extended)": "CUSIP",
        "Daily Total Return": "returns",
        "Company Market Cap": "market_cap",
        "CO2 Equivalent Emissions Direct, Scope 1": "carbon_emissions_scope_1",
        "CO2 Equivalent Emissions Indirect, Scope 2": "carbon_emissions_scope_2",
        "CO2 Equivalent Emissions Indirect, Scope 3": "carbon_emissions_scope_3",
    }

    def round_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Rounds data columns returned from Eikon

        :param df: a dataframe with numeric columns
        :return: dataframe, where floats are rounded based on the EikonDataExtractor dictionary.
        """
        for key in df.select_dtypes(include=[float]):
            if self._precision == 0:
                df[key] = df[key].astype("Int64")
            else:
                df[key] = df[key].round(self._precision)
        return df

    def __init__(self, eikon_app_key: str, isin_filepath: str, output_folder: str, columns: List, frequency: str = None,
                 block_size: int = None, precision=None):
        self.output_folder = output_folder
        self.columns = columns
        self.frequency = frequency
        self.block_size = block_size
        self._precision = precision

        ek.set_app_key(eikon_app_key)

        with open(isin_filepath, 'r') as file:
            isins = file.read().split('\n')
            self.isins = [x for x in isins if x]

    def download_data(self, since: str = None) -> None:
        start_time = time.time()
        if self.block_size is None:
            self.block_size = len(self.isins)
        chunk_no = math.ceil(len(self.isins) / self.block_size)
        for i in range(chunk_no):
            print(f"Iteration {i + 1} of {chunk_no}")
            df = self.get_data_chunk(self.isins, i, since)
            if df.shape[0] == 0:
                continue
            if pd.notna(self._precision):
                df = self.round_df(df)
            df = df.rename(columns=EikonDataExtractor.col_name_dict)
            df.columns = [col.replace(" ", "_") for col in df.columns]
            if "Date" in df:
                df.Date = df.Date.str[:10]
                df.sort_values(['ISIN', 'Date'], ascending=[True, True], inplace=True)
            print(f"--- {time.time() - start_time} seconds ---")
            output_path = f"{self.data_path}{self.output_folder}"
            pathlib.Path(output_path).mkdir(exist_ok=True)
            df.to_csv(f"{output_path}/extract{i}.csv", index=False)
        return None

    def get_data_chunk(self, firms: List[str], block: int, edate: str = None) -> pd.DataFrame:
        while True:
            with contextlib.suppress(ek.eikonError.EikonError):
                isin_block = firms[self.block_size * block:self.block_size * (block + 1)]
                edate = edate if edate is not None else 0
                conf = {'SDate': 0, 'EDate': edate, 'FRQ': self.frequency, 'Curn': 'USD'}
                df, err = ek.get_data(isin_block, self.columns, conf)
                df = df.drop_duplicates().dropna(how="all")
                return df.loc[~df[df.columns.difference(["Instrument", "Date"])].isnull().all(axis=1)]


if __name__ == '__main__':
    start_date = "2006-01-01"
    my_isins = "sp500-isin-list.txt"
    # get_isins("SP500", "all_us_isins")
    get_stock_return_extractor(my_isins, "D").download_data(start_date)
    get_business_sector_extractor(my_isins).download_data()
    get_market_cap_extractor(my_isins).download_data(start_date)
    get_indicator_extractor(my_isins).download_data(start_date)
    get_cusip_extractor(my_isins).download_data()
    exit()
