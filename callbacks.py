import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import Input, Output, State, ctx, no_update

from census_client import *
from config import *

_county_geojson_cache: dict | None = None


def _get_county_geojson():
    """Fetch and cache the county-level GeoJSON used for choropleth maps."""

    global _county_geojson_cache
    if _county_geojson_cache is None:
        resp = requests.get(COUNTY_GEOJSON_URL, timeout=30)
        _county_geojson_cache = resp.json()
    return _county_geojson_cache



    