import pandas as pd
from census import Census

from config import *

def validate_api_key(api_key):
    """Validate a Census API key by making a simple request."""
    try:
        c = Census(api_key)
        result = c.acs5.state(("NAME",), "01", year=2022)
        return bool(result)
    except Exception:
        return False


def fetch_all_states(api_key, variables, year):
    """Fetch data for all states for the specified variables and year."""
    c = Census(api_key)
    fields = ["NAME"] + variables
    data = c.acs5.get(fields, {"for": "state:*"})
    df = pd.DataFrame(data)
    df['state'] = df['state'].astype(str).str.zfill(2)
    df['state_abbrev'] = df['state'].map(FIPS_TO_ABBREV)
    df['state_name'] = df['state'].map(STATE_FIPS)

    for var in variables:
        df[var] = pd.to_numeric(df[var], errors="coerce")
    return df