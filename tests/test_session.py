import unittest
from unittest.mock import patch, MagicMock, call
import pytest
import pandas as pd
from datetime import datetime

# Import the module to test
from eikon_api_wrapper.session import Session, set_app_key


class TestSession(unittest.TestCase):
    """Test suite for Session class in eikon_api_wrapper.session module"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.api_key = "test_api_key"
        self.start_date = "2023-01-01"
        self.data_path = "/tmp/test_data"
        self.test_isins = ["US0378331005", "US5949181045"]  # Apple, Microsoft

    @patch("eikon_api_wrapper.session.ek")
    def test_init(self, mock_ek):
        """Test Session initialization"""
        session = Session(self.api_key, self.start_date, "D", self.data_path, custom_param="value")

        # Verify ek.set_app_key was called with the right key
        mock_ek.set_app_key.assert_called_once_with(self.api_key)

        # Verify attributes were set correctly
        self.assertEqual(session.start_date, self.start_date)
        self.assertEqual(session._data_path, self.data_path)
        self.assertEqual(session.freq, "D")
        self.assertEqual(session.custom_param, "value")

    @patch("eikon_api_wrapper.session.ek")
    def test_call_method(self, mock_ek):
        """Test __call__ method for updating attributes"""
        session = Session(self.api_key)
        session(new_param="new_value", freq="Mo")

        # Verify attributes were updated
        self.assertEqual(session.new_param, "new_value")
        self.assertEqual(session.freq, "Mo")

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_stock_returns_daily(self, mock_extractor_class):
        """Test get_stock_returns with daily frequency"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_stock_returns(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "stock_returns",
            ["TR.TotalReturn1D.Date", "TR.TotalReturn1D"],
            self.data_path,
            "D",
            block_size=10,
            precision=6
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_stock_returns_monthly(self, mock_extractor_class):
        """Test get_stock_returns with monthly frequency"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "Mo", self.data_path)
        result = session.get_stock_returns(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "stock_returns",
            ["TR.TotalReturn1Mo.Date", "TR.TotalReturn1Mo"],
            self.data_path,
            "M",
            block_size=100,
            precision=6
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_stock_returns_custom_block_size(self, mock_extractor_class):
        """Test get_stock_returns with custom block size"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method with custom block_size
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_stock_returns(self.test_isins, block_size=50)

        # Verify EikonDataExtractor was initialized with custom block_size
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "stock_returns",
            ["TR.TotalReturn1D.Date", "TR.TotalReturn1D"],
            self.data_path,
            "D",
            block_size=50,
            precision=6
        )

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_bond_returns(self, mock_extractor_class):
        """Test get_bond_returns method"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_bond_returns(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "bond_returns",
            [
                "TR.FiIssuerName",
                "TR.IssuerRating",
                "TR.IssuerRating.Date",
                "TR.FundLaunchDate",
            ],
            self.data_path,
            "D",
            block_size=10,
            precision=6
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_market_cap_data(self, mock_extractor_class):
        """Test get_market_cap_data method"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_market_cap_data(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "market_cap",
            ["TR.CompanyMarketCap.Date", "TR.CompanyMarketCap"],
            self.data_path,
            "M",
            block_size=200,
            precision=0
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_climate_indicators_default(self, mock_extractor_class):
        """Test get_climate_indicators method with default indicators"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_climate_indicators(self.test_isins)

        # Verify EikonDataExtractor was initialized with default indicators
        default_indicators = [
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
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "indicators",
            default_indicators,
            self.data_path,
            "FY",
            block_size=1000,
            precision=2
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_climate_indicators_custom(self, mock_extractor_class):
        """Test get_climate_indicators method with custom indicators"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create custom indicators
        custom_indicators = ["TR.TRESGScore", "TR.CO2DirectScope1"]

        # Create session and call method with custom indicators
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_climate_indicators(self.test_isins, custom_indicators)

        # Verify EikonDataExtractor was initialized with custom indicators
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "indicators",
            custom_indicators,
            self.data_path,
            "FY",
            block_size=1000,
            precision=2
        )

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_cusips(self, mock_extractor_class):
        """Test get_cusips method"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_cusips(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "cusips",
            ["TR.CUSIPExtended"],
            self.data_path,
            frequency="FY",
            block_size=1000
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.EikonDataExtractor")
    def test_get_business_sectors(self, mock_extractor_class):
        """Test get_business_sectors method"""
        # Setup mock
        mock_extractor = MagicMock()
        mock_extractor_class.return_value = mock_extractor
        mock_extractor.download_data.return_value = pd.DataFrame()

        # Create session and call method
        session = Session(self.api_key, self.start_date, "D", self.data_path)
        result = session.get_business_sectors(self.test_isins)

        # Verify EikonDataExtractor was initialized correctly
        mock_extractor_class.assert_called_once_with(
            self.test_isins,
            "trbc",
            [
                "TR.TRBCEconSectorCode",
                "TR.TRBCBusinessSectorCode",
                "TR.TRBCIndustryGroupCode",
                "TR.TRBCIndustryCode",
                "TR.TRBCActivityCode",
            ],
            self.data_path,
            frequency="FY",
            block_size=1000
        )

        # Verify download_data was called with start_date
        mock_extractor.download_data.assert_called_once_with(self.start_date)
        self.assertIsInstance(result, pd.DataFrame)

    @patch("eikon_api_wrapper.session.ek")
    def test_get_companies_from(self, mock_ek):
        """Test get_companies_from static method"""
        # Setup mock
        mock_df = pd.DataFrame({
            'Instrument': ['AAPL.O', 'MSFT.O'],
            'ISIN Code': ['US0378331005', 'US5949181045'],
            'Common Name': ['APPLE INC', 'MICROSOFT CORP'],
            'Headquarters Country': ['United States', 'United States'],
            'Company Market Cap': [2000000000000, 1800000000000]
        })
        mock_ek.get_data.return_value = (mock_df, None)

        # Call static method
        country_code = "US"
        result = Session.get_companies_from(country_code)

        # Verify ek.get_data was called correctly
        u_string = "U(IN(Equity(active,public,primary))/*UNV:Public*/)"
        expected_screen_string = f'SCREEN({u_string}, IN(TR.HQCountryCode,"{country_code}"), CURN=USD)'
        expected_instrument_cols = [
            "TR.ISINCode",
            "TR.CommonName,TR.HeadquartersCountry,TR.CompanyMarketCap",
        ]
        mock_ek.get_data.assert_called_once_with(expected_screen_string, expected_instrument_cols)

        # Verify result was properly processed
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(list(result.columns), ['Ticker', 'ISIN', 'Common Name', 'Headquarters Country', 'Company Market Cap'])
        self.assertEqual(list(result['ISIN']), ['US0378331005', 'US5949181045'])

    @patch("eikon_api_wrapper.session.ek")
    def test_set_app_key(self, mock_ek):
        """Test set_app_key function"""
        test_key = "another_test_key"
        set_app_key(test_key)
        mock_ek.set_app_key.assert_called_once_with(test_key)


if __name__ == "__main__":
    unittest.main()