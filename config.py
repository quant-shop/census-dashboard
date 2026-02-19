CENSUS_VARIABLES = {
    # demographics
    "B01001_001E": {"label": "Total Population", "category": "Demographics", "format": ","},
    "B01002_001E": {"label": "Median Age", "category": "Demographics", "format": ".1f"},
    "B03002_001E": {"label": "Total Population (Race/Ethnicity)", "category": "Demographics", "format": ","},
    "B03002_003E": {"label": "White Alone, Not Hispanic", "category": "Demographics", "format": ","},
    "B03002_004E": {"label": "Black or African American Alone", "category": "Demographics", "format": ","},
    "B03002_012E": {"label": "Hispanic or Latino", "category": "Demographics", "format": ","},
}

VARIABLE_CODES = list(CENSUS_VARIABLES.keys())
print(VARIABLE_CODES)