import pandas as pd
from census import Census

from config import *

def validate_api_key(api_key):
    try:
        c = Census(api_key)
        result = c.acs5.state(("NAME",), "01", year=2022)
        return bool(result)
    except Exception:
        return False

