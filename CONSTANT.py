OUTPUT_PICKLE_FILENAME  = "data/data.pickle"
OUTPUT_TEXT_FILENAME    = "data/parsed_HOSE_data.txt"
SAVE_INTERVAL = 200
SOMETHING_ELSE = 100
CACHE_FILE_NAME = "cached_indicator_DATE.json"
DATE = "03/11/2020"
OVER_TIME  = False
#############################################################################################################

MARKET_START = 9 # MUST edit if not int. e.g 8.45 change date string below
MARKET_STARTS = int(MARKET_START * 3600)

EMPTY_SERVER_LIST = []
def compute_i(hour, minute, second):
    return int(hour * 3600 + 60 * minute + second - MARKET_STARTS)