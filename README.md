# eikon_api_wrapper
Easier and more reliable usage of the Eikon data terminal when querying company data.
The API allows to create tables like in the Eikon Screener APP, but with arbitrary amount of rows and columns.

## Usage
1. Clone or download this repository.
2. To use the Eikon API, create a file called `eikon_app_key.txt` with a valid eikon app key in the root directory of your local clone.
More information for getting this Eikon App Key is available [here](https://developers.refinitiv.com/en/api-catalog/eikon/eikon-data-api/quick-start).
2. Start the Thomson Reuters Eikon Terminal in Front End and login (for that, you have to sit at a computer that has access Eikon).
3. Run `sample_extraction.py` to retrieve a sample data extract from Eikon.
4. The results will be stored locally in a subfolder called `data`.

You can imitate the sample functions for custom extractions. Check there definitions in the `functions.py` script.
