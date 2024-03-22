import contextlib
import pathlib
from typing import List
import eikon as ek
import math
import pandas as pd
import time

# ek.set_log_level(1)


class EikonDataExtractor:

    eikon_app_key_filename = "eikon_app_key.txt"

    def __init__(
        self,
        isins: list,
        output_subfolder: str,
        eikon_columns: list,
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
        self.data_path = "data/"
        self.isins = isins
        self.output_folder = output_subfolder
        self.columns = eikon_columns
        self.frequency = frequency
        self.block_size = block_size
        self._precision = precision

        self.connect()

    @classmethod
    def connect(cls):
        with open(cls.eikon_app_key_filename, mode="r") as file:
            eikon_app_key = file.read()
        ek.set_app_key(eikon_app_key)

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
            df = self.get_data_chunk(self.isins, i, since)
            if df.shape[0] == 0:
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
            output_path = f"{self.data_path}{self.output_folder}"
            pathlib.Path(output_path).mkdir(exist_ok=True)
            df.to_csv(f"{output_path}/extract{i}.csv", index=False)
        return None

    def get_data_chunk(
        self, firms: List[str], block: int, edate: str = None
    ) -> pd.DataFrame:
        while True:
            with contextlib.suppress(ek.eikonError.EikonError):
                isin_block = firms[
                    self.block_size * block : self.block_size * (block + 1)
                ]
                edate = edate if edate is not None else 0
                conf = {
                    "SDate": 0,
                    "EDate": edate,
                    "FRQ": self.frequency,
                    "Curn": "USD",
                }
                df, err = ek.get_data(isin_block, self.columns, conf)
                df = df.drop_duplicates().dropna(how="all")
                return df.loc[
                    ~df[df.columns.difference(["Instrument", "Date"])]
                    .isnull()
                    .all(axis=1)
                ]
