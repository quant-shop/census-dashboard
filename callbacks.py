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

    # --- YEAR RANGE LABEL ------------------
    @app.callback(
        Output("year-range-label", "children"),
        Input("year-range-slider", "value"),
    )
    def update_year_label(year_range):
        """Update the year range comparison label when the slider changes."""
        if not year_range or len(year_range) < 2:
            return ""
        return f"Comparing {year_range[0]} vs {year_range[1]}"

    # --- FETCH DATA -------------------------
    @app.callback(
        Output("state-data-store", "data"),
        Output("state-data-start-store", "data"),
        Output("county-data-store", "data"),
        Output("county-data-start-store", "data"),
        Output("current-view-store", "data"),
        Output("drilldown-state-store", "data"),
        Output("status-text", "children"),
        Output("map-variable-dropdown", "options"),
        Output("map-variable-dropdown", "value"),
        Input("fetch-button", "n_clicks"),
        State("api-key-store", "data"),
        State("year-range-slider", "value"),
        State("state-dropdown", "value"),
        State("variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def fetch_data(n_clicks, api_key, year_range, state_fips, variables):
        """Fetch state and optional county data for the selected variables and year range."""
        if not api_key or not variables:
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                "Please enter an API key and select variables.",
                no_update, no_update,
            )

        if isinstance(variables, str):
            variables = [variables]

        start_year, end_year = year_range

        var_opts = [
            {"label": get_variable_label(v), "value": v} for v in variables
        ]

        try:
            state_end_df = fetch_all_states(api_key, variables, end_year)
            state_start_df = fetch_all_states(api_key, variables, start_year)

            state_end_json = state_end_df.to_json(orient="split")
            state_start_json = state_start_df.to_json(orient="split")

            county_end_json = None
            county_start_json = None
            view = "states"
            drilldown = None

            if state_fips:
                county_end_df = fetch_counties(api_key, variables, end_year, state_fips)
                county_start_df = fetch_counties(api_key, variables, start_year, state_fips)
                county_end_json = county_end_df.to_json(orient="split")
                county_start_json = county_start_df.to_json(orient="split")
                view = "county"
                drilldown = state_fips

            count = len(state_end_df)
            status = f"Loaded {count} states for {start_year}-{end_year}."
            if state_fips:
                county_count = len(county_end_df) if county_end_json else 0
                state_name = STATE_FIPS.get(state_fips, state_fips)
                status += f" {county_count} counties in {state_name}."

            return (
                state_end_json, state_start_json,
                county_end_json, county_start_json,
                view, drilldown,
                status, var_opts, variables[0],
            )
        except Exception as e:
            return (
                no_update, no_update, no_update, no_update, no_update, no_update,
                f"Error fetching data: {e}",
                no_update, no_update,
            )

        