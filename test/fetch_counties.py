import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from census_client import *

load_dotenv()
API_KEY = os.getenv("CENSUS_KEY")

def test_fetch_counties():
    print("Validating API key...")
    assert validate_api_key(API_KEY), "API key is invalid!"
    print("API key is valid.\n")

    state_fips = "06"  # California
    print(f"Fetching counties for state FIPS '{state_fips}' (California)...")
    df = fetch_counties(API_KEY, ["B01001_001E"], 2022, state_fips)

    assert not df.empty, "DataFrame is empty!"
    print(f"Fetched {len(df)} counties.\n")

    assert "state" in df.columns, "'state' column missing!"
    assert "county" in df.columns, "'county' column missing!"
    assert "fips" in df.columns, "'fips' column missing!"
    assert "county_name" in df.columns, "'county_name' column missing!"

    assert df["state"].str.len().eq(2).all(), "State FIPS codes are not 2 digits!"
    assert df["county"].str.len().eq(3).all(), "County FIPS codes are not 3 digits!"
    assert df["fips"].str.len().eq(5).all(), "Combined FIPS codes are not 5 digits!"

    assert (df["state"] == state_fips).all(), "Not all rows match the requested state!"
    assert df["B01001_001E"].notna().all(), "Population column has NaN values!"

    print("All assertions passed.\n")

    print("Columns:", list(df.columns))
    print(f"\nFirst 10 rows:\n{df.head(10).to_string(index=False)}")
    print(f"\nSample county names: {df['county_name'].head(5).tolist()}")

if __name__ == "__main__":
    test_fetch_counties()
