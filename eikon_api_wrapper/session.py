import eikon as ek

from eikon_data_extractor import EikonDataExtractor


class Session:

    def __init__(self, key, start_date=None, freq="D", **kwargs):
        ek.set_app_key(key)
        self.start_date = start_date
        self.freq = freq
        self.__dict__.update(kwargs)

    def __call__(self, *args, **kwargs):
        self.__dict__.update(kwargs)

    def get_stock_returns(self, isins):
        """
        :param isins: list of isins
        :param freq: "D" (daily) or "Mo" (monthly)
        :return:
        """
        freq = self.freq
        return_cols = [f"TR.TotalReturn1{freq}.Date", f"TR.TotalReturn1{freq}"]
        block_size = 10 if freq == "D" else 100
        extractor = EikonDataExtractor(
            isins,
            "stock_returns",
            return_cols,
            freq[0],
            block_size=block_size,
            precision=6,
        )
        return extractor.download_data(self.start_date)

    def get_bond_returns(self, isins):
        """
        :param isins: list of isins
        :return:
        """
        return_cols = [
            "TR.FiIssuerName",
            "TR.IssuerRating",
            "TR.IssuerRating.Date",
            "TR.FundLaunchDate",
        ]
        block_size = 10 if self.freq == "D" else 100
        extractor = EikonDataExtractor(
            isins,
            "bond_returns",
            return_cols,
            self.freq[0],
            block_size=block_size,
            precision=6,
        )
        return extractor.download_data(self.start_date)

    def get_market_cap_data(self, isins):
        market_cap_cols = ["TR.CompanyMarketCap.Date", "TR.CompanyMarketCap"]
        extractor = EikonDataExtractor(
            isins, "market_cap", market_cap_cols, "M", block_size=200, precision=0
        )
        return extractor.download_data(self.start_date)

    def get_climate_indicators(self, isins):
        indicator_cols = [
            "TR.TRESGScore.Date",
            "TR.TRESGScore",
            "TR.TRESGEmissionsScore",
            "TR.TRESGInnovationScore",
            "TR.TRESGResourceUseScore",
            "TR.CO2DirectScope1",
            "TR.CO2IndirectScope2",
            "TR.CO2IndirectScope3",
            "TR.TRESGManagementScore",
            "TR.TRESGShareholdersScore",
            "TR.TRESGCSRStrategyScore",
            "TR.TRESGWorkforceScore",
            "TR.TRESGHumanRightsScore",
            "TR.TRESGCommunityScore",
            "TR.TRESGProductResponsibilityScore",
        ]
        extractor = EikonDataExtractor(
            isins, "indicators", indicator_cols, "FY", block_size=1000, precision=2
        )
        return extractor.download_data(self.start_date)

    def get_cusips(self, isins):
        extractor = EikonDataExtractor(
            isins, "cusips", ["TR.CUSIPExtended"], frequency="FY", block_size=1000
        )
        return extractor.download_data(self.start_date)

    def get_business_sectors(self, isins):
        industry_sector_cols = [
            "TR.TRBCEconSectorCode",
            "TR.TRBCBusinessSectorCode",
            "TR.TRBCIndustryGroupCode",
            "TR.TRBCIndustryCode",
            "TR.TRBCActivityCode",
        ]
        extractor = EikonDataExtractor(
            isins, "trbc", industry_sector_cols, frequency="FY", block_size=1000
        )
        return extractor.download_data(self.start_date)

    def get_companies_from(self, country_code):
        u_string = "U(IN(Equity(active,public,primary))/*UNV:Public*/)"
        screen_string = (
            f'SCREEN({u_string}, IN(TR.HQCountryCode,"{country_code}"), CURN=USD)'
        )
        instrument_cols = [
            "TR.ISINCode",
            "TR.CommonName,TR.HeadquartersCountry,TR.CompanyMarketCap",
        ]
        ek.set_app_key("8682ab5b1f6b4832a1870ddefe5d1108b859562e")
        df, _ = ek.get_data(screen_string, instrument_cols)
        cleansed_df = df.drop_duplicates().dropna(how="all")
        return cleansed_df.rename(columns={"ISIN Code": "ISIN", "Instrument": "Ticker"})
