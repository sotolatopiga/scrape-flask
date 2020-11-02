from pymongo import MongoClient

_SERVER_CONTEXT_DB = "server_context"
_DB_URI = "mongodb://sotola:na6pi3pi@13.212.108.204/?authSource=admin"

_DB_TODAY_DATA = "hose_2020_11_02_test"
COL_HOSE_RAW = "hose_raw"
COL_O_HISTORY = "o_history"
COL_O_INDICATORS = "o_indicators"
COL_O_PS_ORDERS = "o_ps_orders"
TEMP_PICKLE = "indicators.pickle"

client = MongoClient(_DB_URI)
db = client[_DB_TODAY_DATA]
