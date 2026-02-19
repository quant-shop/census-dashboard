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
