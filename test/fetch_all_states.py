import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from census_client import *

load_dotenv()
API_KEY = os.getenv("CENSUS_KEY")

def test_all():
    print("Validating API key...")
    assert validate_api_key(API_KEY), "API key is invalid!"
    print("API key is valid.\n")

    print("Fetching all states...")
    df = fetch_all_states(API_KEY, ["B01001_001E"], 2022)

    assert not df.empty, "DataFrame is empty!"
    print(f"Fetched {len(df)} states.\n")

    assert "state" in df.columns, "'state' column missing!"
    assert df["state"].str.len().eq(2).all(), "FIPS codes are not 2 digits!"
    print("All assertions passed.\n")

    print("Columns:", list(df.columns))
    print(f"\nFirst 10 rows:\n{df.head(10).to_string(index=False)}")
    print(f"\nSample state abbreviations: {df['state_abbrev'].head(5).tolist()}")

if __name__ == "__main__":
    test_all()
