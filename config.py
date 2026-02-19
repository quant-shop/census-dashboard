CENSUS_VARIABLES = {
    # demographics
    "B01001_001E": {"label": "Total Population", "category": "Demographics", "format": ","},
    "B01002_001E": {"label": "Median Age", "category": "Demographics", "format": ".1f"},
    "B03002_001E": {"label": "Total Population (Race/Ethnicity)", "category": "Demographics", "format": ","},
    "B03002_003E": {"label": "White Alone, Not Hispanic", "category": "Demographics", "format": ","},
    "B03002_004E": {"label": "Black or African American Alone", "category": "Demographics", "format": ","},
    "B03002_012E": {"label": "Hispanic or Latino", "category": "Demographics", "format": ","},

    # we will add more variables later
}

VARIABLE_CODES = list(CENSUS_VARIABLES.keys())


VARIABLE_OPTIONS =[]
seen_categories = set()

for code, info in CENSUS_VARIABLES.items():
    category = info['category']
    if category not in seen_categories:
        seen_categories.add(category)
        VARIABLE_OPTIONS.append({
            "label": f"{category}",
            "value": f"_header_{category}",
            "disabled": True
        })
    
    VARIABLE_OPTIONS.append({
        "label": f"{    info['label']} ({code})",
        "value": code
    })

# years configuration
ACS5_YEARS = range(2023, 2008, -1)
MIN_YEAR = 2009
MAX_YEAR = 2023

# defult year & variable
DEFAULT_YEAR_RANGE = [2018, 2023]
DEFAULT_VARIABLES = ["B01001_001E", "B01002_001E"]

# FIPS code --> state name mapping
STATE_FIPS = {
    "01": "Alabama", "02": "Alaska", "04": "Arizona", "05": "Arkansas",
    "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
    "11": "District of Columbia", "12": "Florida", "13": "Georgia", "15": "Hawaii",
    "16": "Idaho", "17": "Illinois", "18": "Indiana", "19": "Iowa",
    "20": "Kansas", "21": "Kentucky", "22": "Louisiana", "23": "Maine",
    "24": "Maryland", "25": "Massachusetts", "26": "Michigan", "27": "Minnesota",
    "28": "Mississippi", "29": "Missouri", "30": "Montana", "31": "Nebraska",
    "32": "Nevada", "33": "New Hampshire", "34": "New Jersey", "35": "New Mexico",
    "36": "New York", "37": "North Carolina", "38": "North Dakota", "39": "Ohio",
    "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "44": "Rhode Island",
    "45": "South Carolina", "46": "South Dakota", "47": "Tennessee", "48": "Texas",
    "49": "Utah", "50": "Vermont", "51": "Virginia", "53": "Washington",
    "54": "West Virginia", "55": "Wisconsin", "56": "Wyoming",
}


# FIPS code --> state abbreviation mapping
FIPS_TO_ABBREV = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO",
    "09": "CT", "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI",
    "16": "ID", "17": "IL", "18": "IN", "19": "IA", "20": "KS", "21": "KY",
    "22": "LA", "23": "ME", "24": "MD", "25": "MA", "26": "MI", "27": "MN",
    "28": "MS", "29": "MO", "30": "MT", "31": "NE", "32": "NV", "33": "NH",
    "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND", "39": "OH",
    "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA",
    "54": "WV", "55": "WI", "56": "WY",
}

# state options for dropdowns
STATE_OPTIONS = sorted(
    [{"label": name, "value":fips} for fips, name in STATE_FIPS.items()],
    key=lambda x: x["label"],
)

