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


def fetch_counties(api_key, variables, year, state_fips):
    """Fetch data for all counties in a state for the specified variables and year."""
    c = Census(api_key)
    fields = ["NAME"] + variables
    data = c.acs5.get(fields, {"for": "county:*", "in": f"state:{state_fips}"})
    df = pd.DataFrame(data)
    df['state'] = df['state'].astype(str).str.zfill(2)
    df['county'] = df['county'].astype(str).str.zfill(3)
    df['fips'] = df['state'] + df['county']
    df['county_name'] = df["NAME"].str.replace(r",.*$", "", regex=True)

    for var in variables:
        df[var] = pd.to_numeric(df[var], errors="coerce")
    return df


def get_variable_label(code):
    """Get the label for a given variable code."""
    return CENSUS_VARIABLES.get(code, {}).get("label", code)

def get_variable_format(code):
    """Get the format for a given variable code."""
    return CENSUS_VARIABLES.get(code, {}).get("format", ",")


def format_value(value, code):
    """Format a value based on the variable's specified format."""
    fmt = get_variable_format(code)
    if pd.isna(value):
        return "N/A"
    try:
        if fmt.startswith("$"):
            return f"${value:{fmt[1:]}}"
        return f"{value:{fmt}}"
    except (ValueError, TypeError):
            return str(value)