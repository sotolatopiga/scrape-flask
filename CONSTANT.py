OUTPUT_PICKLE_FILENAME  = "data/data.pickle"
OUTPUT_TEXT_FILENAME    = "data/parsed_HOSE_data.txt"
SAVE_INTERVAL = 10
SOMETHING_ELSE = 100
CACHE_FILE_NAME = "cached_indicator_DATE.json"
DATE = "29/10/2020"

#############################################################################################################

MARKET_START = 9 # MUST edit if not int. e.g 8.45 change date string below
MARKET_STARTS = int(MARKET_START * 3600)


def compute_i(hour, minute, second):
    return int(hour * 3600 + 60 * minute + second - MARKET_STARTS)