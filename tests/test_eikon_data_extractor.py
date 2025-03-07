import os
import pathlib
import tempfile
from unittest.mock import MagicMock, call, patch

import pandas as pd
import pytest

from eikon_api_wrapper.eikon_data_extractor import EikonDataExtractor


class TestEikonDataExtractor:
    @pytest.fixture
    def sample_isins(self):
        return [
            "US0378331005",
            "US5949181045",
            "US0231351067",
        ]  # Apple, Microsoft, Amazon

    @pytest.fixture
    def sample_columns(self):
        return ["TR.PriceClose", "TR.Volume", "TR.MarketCap"]

    @pytest.fixture
    def mock_eikon_data(self):
        # Create a sample dataframe that mimics Eikon API response
        data = {
            "Instrument": ["US0378331005", "US5949181045", "US0231351067"],
            "Date": ["2023-01-01", "2023-01-01", "2023-01-01"],
            "Price Close": [150.25, 240.50, 95.75],
            "Volume": [12345678.0, 9876543.0, 5432167.0],
            "Market Cap": [2500000000.0, 1800000000.0, 950000000.0],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def extractor(self, sample_isins, sample_columns):
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield EikonDataExtractor(
                isins=sample_isins,
                output_subfolder="test_data",
                eikon_columns=sample_columns,
                data_path=tmp_dir,
                frequency="D",
                block_size=2,
                precision=2,
            )

    def test_init(self, extractor, sample_isins, sample_columns):
        """Test initialization of the EikonDataExtractor class"""
        assert extractor.isins == sample_isins
        assert extractor.columns == sample_columns
        assert extractor.frequency == "D"
        assert extractor.block_size == 2
        assert extractor._precision == 2

    def test_round_df(self, extractor):
        """Test the round_df method"""
        # Create test dataframe with mixed types
        df = pd.DataFrame(
            {
                "Instrument": ["US0378331005"],
                "Date": ["2023-01-01"],
                "Price": [123.45678],
                "Volume": [987654.321],
            }
        )

        # Apply rounding
        result = extractor.round_df(df)

        # Check the result
        assert result["Price"].iloc[0] == 123.46
        assert result["Volume"].iloc[0] == 987654.32

        # Test with precision=0
        extractor._precision = 0

        # Create a new DataFrame with integer values to avoid conversion issues
        df_int = pd.DataFrame(
            {
                "Instrument": ["US0378331005"],
                "Date": ["2023-01-01"],
                "Price": [123.0],  # Use whole numbers for Int64 conversion
                "Volume": [987654.0],
            }
        )

        result = extractor.round_df(df_int)
        assert result["Price"].dtype.name == "Int64"
        assert result["Volume"].dtype.name == "Int64"

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_get_data_chunk(self, mock_ek, extractor, mock_eikon_data):
        """Test the get_data_chunk method"""
        # Configure the mock to return our sample data
        mock_ek.get_data.return_value = (mock_eikon_data, None)

        # Call the method
        result = extractor.get_data_chunk(0)

        # Check that Eikon API was called with correct parameters
        mock_ek.get_data.assert_called_once_with(
            extractor.isins[0:2],
            extractor.columns,
            {"SDate": 0, "EDate": 0, "FRQ": "D", "Curn": "USD"},
        )

        # Check the result
        assert isinstance(result, pd.DataFrame)
        assert not result.empty

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_get_data_chunk_with_sdate(self, mock_ek, extractor, mock_eikon_data):
        """Test the get_data_chunk method with a custom end date"""
        mock_ek.get_data.return_value = (mock_eikon_data, None)

        result = extractor.get_data_chunk(0, sdate="2023-12-31")

        mock_ek.get_data.assert_called_once_with(
            extractor.isins[0:2],
            extractor.columns,
            {"SDate": "2023-12-31", "EDate": 0, "FRQ": "D", "Curn": "USD"},
        )

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_download_data(self, mock_ek, extractor, mock_eikon_data, sample_isins):
        """Test the download_data method"""
        # Create a temporary directory for test data
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor.data_path = tmp_dir

            # Configure the mock to return our sample data
            mock_ek.get_data.return_value = (mock_eikon_data, None)

            # Call the method
            extractor.download_data()

            # Check that Eikon API was called correctly
            # Since block_size=2 and we have 3 ISINs, it should be called twice
            assert mock_ek.get_data.call_count == 2

            # Check that files were created
            output_path = pathlib.Path(f"{tmp_dir}/{extractor.output_folder}")
            assert output_path.exists()

            assert pathlib.Path(f"{output_path}/extract0.csv").exists()
            assert pathlib.Path(f"{output_path}/extract1.csv").exists()

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_download_data_single_isin_per_block(
        self, mock_ek, extractor, mock_eikon_data
    ):
        """Test downloading data with block_size=1"""
        # Create a temporary directory for test data
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor.data_path = tmp_dir
            extractor.block_size = 1

            # Configure the mock to return our sample data
            mock_ek.get_data.return_value = (mock_eikon_data, None)

            # Call the method
            extractor.download_data()

            # Check that Eikon API was called correctly (3 ISINs, block_size=1)
            assert mock_ek.get_data.call_count == 3

            # Check that files were created with ISIN as filename
            output_path = pathlib.Path(f"{tmp_dir}/{extractor.output_folder}")
            for isin in extractor.isins:
                assert pathlib.Path(f"{output_path}/{isin}.csv").exists()

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_download_data_empty_result(self, mock_ek, extractor):
        """Test downloading data that returns empty results"""
        # Create a temporary directory for test data
        with tempfile.TemporaryDirectory() as tmp_dir:
            extractor.data_path = tmp_dir

            # Configure the mock to return an empty dataframe
            empty_df = pd.DataFrame()
            mock_ek.get_data.return_value = (empty_df, None)

            # Capture log messages
            with patch("eikon_api_wrapper.eikon_data_extractor.log") as mock_log:
                extractor.download_data()

                # No warning for block_size > 1
                mock_log.warning.assert_not_called()

                # Set block_size to 1 and test again
                extractor.block_size = 1
                extractor.download_data()

                # Should log warnings for each ISIN
                assert mock_log.warning.call_count == 3

    @patch("eikon_api_wrapper.eikon_data_extractor.ek")
    def test_eikon_error_retry(self, mock_ek, extractor, mock_eikon_data):
        """Test retry behavior when Eikon API raises an error"""
        # Make the mock raise an error once, then succeed
        mock_ek.eikonError.EikonError = Exception
        mock_ek.get_data.side_effect = [
            Exception("API Error"),  # First call fails
            (mock_eikon_data, None),  # Second call succeeds
        ]

        # Call the method
        result = extractor.get_data_chunk(0)

        # Check that get_data was called twice
        assert mock_ek.get_data.call_count == 2

        # Check the result is the successful one
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
