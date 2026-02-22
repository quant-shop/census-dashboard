from census_client import validate_api_key
from dotenv import load_dotenv
import os

load_dotenv()


key = os.getenv("CENSUS_KEY")
if key is None:
    print("No API key found. Please set CENSUS_KEY in your .env file.")
elif validate_api_key(key):
    print("Key is valid, good to go!")
else:
    print("Invalid key — check it at https://api.census.gov/data/key_signup.html")