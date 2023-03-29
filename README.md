# eikon_api_wrapper
Easier and more reliable usage of the Eikon data terminal when querying company data.

1. To use the Eikon API, create a file called `eikon_app_key.txt` with a valid eikon app key in the root directory of this repository.
2. Start the Thomson Reuters Eikon Terminal in Front End and login (you have to sit a computer that has Eikon access).
3. Run `sample_extraction.py` to retrieve a sample data extract from Eikon.
4. The results will be stored locally in a subfolder called `data`.

You can imitate the sample functions for custom extractions.