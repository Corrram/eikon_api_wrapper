import contextlib
import logging
import math
import pathlib
import time
import warnings

import eikon as ek
import pandas as pd

# ek.set_log_level(1)
log = logging.getLogger(__name__)


class EikonDataExtractor:
    def __init__(
        self,
        isins: list,
        output_subfolder: str,
        eikon_columns: list,
        data_path="data",
        frequency: str = None,
        block_size: int = None,
        precision=None,
    ):
        """

        :param isins: List of company isins to query.
        :param output_subfolder:
        :param eikon_columns:
        :param frequency:
        :param block_size:
        :param precision:
        """
        self.data_path = data_path
        self.isins = isins
        self.output_folder = output_subfolder
        self.columns = eikon_columns
        self.frequency = frequency
        self.block_size = block_size
        self._precision = precision

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

    def download_data(self, since: str = None) -> None:
        start_time = time.time()
        if self.block_size is None:
            self.block_size = len(self.isins)
        chunk_no = math.ceil(len(self.isins) / self.block_size)
        for i in range(chunk_no):
            print(f"Iteration {i + 1} of {chunk_no}")
            df = self.get_data_chunk(i, since)
            if df.shape[0] == 0:
                if self.block_size == 1:
                    log.warning(f"No data found for {self.isins[i]}")
                continue
            if pd.notna(self._precision):
                df = self.round_df(df)
            df.columns = [col.replace(" ", "_") for col in df.columns]
            if "Date" in df:
                df.Date = df.Date.str[:10]
                df.sort_values(
                    ["Instrument", "Date"], ascending=[True, True], inplace=True
                )
            print(f"--- {time.time() - start_time} seconds ---")
            pathlib.Path(self.data_path).mkdir(exist_ok=True)
            output_path = f"{self.data_path}/{self.output_folder}"
            pathlib.Path(output_path).mkdir(exist_ok=True)
            if self.block_size == 1:
                filename = f"{output_path}/{self.isins[i]}.csv"
            else:
                filename = f"{output_path}/extract{i}.csv"
            df.to_csv(filename, index=False)
        return None

    def get_data_chunk(self, block: int, sdate: str = None) -> pd.DataFrame:
        while True:
            with contextlib.suppress(ek.eikonError.EikonError):
                isin_block = self.isins[
                    self.block_size * block : self.block_size * (block + 1)
                ]
                sdate = sdate if sdate is not None else 0
                conf = {
                    "SDate": sdate,
                    "EDate": 0,
                    "FRQ": self.frequency[-1],
                    "Curn": "USD",
                }
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df, err = ek.get_data(isin_block, self.columns, conf)
                df = df.drop_duplicates().dropna(subset=df.columns[1:], how="all")
                return df.loc[
                    ~df[df.columns.difference(["Instrument", "Date"])]
                    .isnull()
                    .all(axis=1)
                ]
