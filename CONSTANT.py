OUTPUT_PICKLE_FILENAME  = "data/data.pickle"
OUTPUT_TEXT_FILENAME    = "data/parsed_HOSE_data.txt"
SAVE_INTERVAL = 10
SOMETHING_ELSE = 100
CACHE_FILE_NAME = "cached_indicator_DATE.json"
DATE = "29/10/2020"

#############################################################################################################

MARKET_START = 9 # MUST edit if not int. e.g 8.45 change date string below
MARKET_STARTS = int(MARKET_START * 3600)
MARKET_END = 14.75
MARKET_ENDS = int(MARKET_END *3600 + 2)
MARKET_DURATION = int(MARKET_ENDS - MARKET_STARTS)
MID = 150  # HARDCODED
AFTERNOON = 240  # HARDCODED
END = 330  # HARDCODED NO ATC

def compute_i(hour, minute, second):
    return int(hour * 3600 + 60 * minute + second - MARKET_STARTS)