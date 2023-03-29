# eikon_api_wrapper
Easier and more reliable usage of the Eikon data terminal when querying company data.

## Usage
1. Clone or download this repository.
2. To use the Eikon API, create a file called `eikon_app_key.txt` with a valid eikon app key in the root directory of your local clone.
2. Start the Thomson Reuters Eikon Terminal in Front End and login (for that, you have to sit at a computer that has access Eikon).
3. Run `sample_extraction.py` to retrieve a sample data extract from Eikon.
4. The results will be stored locally in a subfolder called `data`.

You can imitate the sample functions for custom extractions. Check there definitions in the `functions.py` script.
