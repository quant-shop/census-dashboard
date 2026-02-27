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


def _empty_map(message="Select variable and click 'Fetch Data'"):
    """Return a blank US map with a centered placeholder message."""
    fig = go.Figure()
    fig.update_layout(
        geo=dict(scope="usa", bgcolor="rgba(0,0,0,0)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        annotations=[
            dict(
                text=message,
                xref="paper", yref="paper",
                x=0.6, y=0.5,
                showarrow=False,
                font=dict(size=16, color="#888"),
            )
        ],
    )

    return fig


def register_callbacks(app):
    """Register all Dash callbacks for the census dashboard."""

    # --- API KEY VALIDATION ------------------
    @app.callback(
        Output("api-key-store", "data"),
        Output("api-key-modal", "is_open"),
        Output("api-key-error", "is_open"),
        Input("api-key-submit", "n_clicks"),
        State("api-key-input", "value"),
        prevent_initial_call=True,
    )
    def handle_api_key(n_clicks, api_key):
        if not api_key or not api_key.strip():
            return no_update, True, True
        api_key = api_key.strip()
        if validate_api_key(api_key):
            return api_key, False, False
        return no_update, True, True

    