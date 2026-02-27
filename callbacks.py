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

    # --- MAP DRILL-DOWN -------------------------
    @app.callback(
        Output("map-figure", "figure"),
        Output("back-button", "style"),
        Output("county-data-store", "data", allow_duplicate=True),
        Output("county-data-start-store", "data", allow_duplicate=True),
        Output("current-view-store", "data", allow_duplicate=True),
        Output("drilldown-state-store", "data", allow_duplicate=True),
        Output("status-text", "children", allow_duplicate=True),
        Input("map-figure", "clickData"),
        Input("back-button", "n_clicks"),
        Input("state-data-store", "data"),
        Input("map-variable-dropdown", "value"),
        Input("map-year-toggle", "value"),
        State("state-data-start-store", "data"),
        State("county-data-store", "data"),
        State("county-data-start-store", "data"),
        State("current-view-store", "data"),
        State("drilldown-state-store", "data"),
        State("api-key-store", "data"),
        State("year-range-slider", "value"),
        State("variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_map(
        click_data, back_clicks, state_end_json, map_var, year_toggle,
        state_start_json, county_end_json, county_start_json,
        current_view, drilldown_state, api_key, year_range, variables,
    ):
        """Handle map clicks for state-to-county drill-down and back navigation."""
        triggered = ctx.triggered_id
        hide_back = {"display": "none"}
        show_back = {"display": "inline-block"}
        no_county = (no_update, no_update)

        if not state_end_json or not map_var:
            return (_empty_map(), hide_back, *no_county,
            no_update, no_update, no_update)

        start_year, end_year = year_range
        label = get_variable_label(map_var)

        # back button 
        if triggered == "back-button":
            fig = _build_map_for_toggle(
                state_end_json, state_start_json, None, None,
                map_var, label, year_toggle, start_year, end_year,
                "states", None,
            )
            return (fig, hide_back, None, None, "states", None,
            "Showing all states.")

        # click on map 
        if triggered == "map-figure" and click_data and current_view == "states":
            try:
                point = click_data["points"][0]
                clicked_location = point.get("location", "")
                clicked_fips = None
                for fips, abbrev in FIPS_TO_ABBREV.items():
                    if abbrev == clicked_location:
                        clicked_fips = fips
                        break

                if clicked_fips and api_key:
                    if isinstance(variables, str):
                        variables = [variables]
                    county_end_df = fetch_counties(api_key, variables, end_year, clicked_fips)
                    county_start_df = fetch_counties(api_key, variables, start_year, clicked_fips)
                    c_end_j = county_end_df.to_json(orient="split")
                    c_start_j = county_start_df.to_json(orient="split")
                    state_name = STATE_FIPS.get(clicked_fips, clicked_fips)

                    fig = _build_map_for_toggle(
                        state_end_json, state_start_json, c_end_j, c_start_j,
                        map_var, label, year_toggle, start_year, end_year, "county", clicked_fips,
                    )
                    status = f"Showing {len(county_end_df)} counties in {state_name}."

                    return (fig, show_back, c_end_j, c_start_j, "county", clicked_fips, status)
            except (KeyError, IndexError):
                pass
    
    # --- STATS CARDS -------------------------
    @app.callback(
        Output("stat-count", "children"),
        Output("stat-mean", "children"),
        Output("stat-std", "children"),
        Input("state-data-store", "data"),
        Input("county-data-store", "data"),
        Input("current-view-store", "data"),
        Input("map-variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_stats(state_json, county_json, view, map_var):
        """Update the summary stat cards (count, mean, std dev) for the active view."""
        if not map_var:
            return "--", "--", "--"

        df = None
        if view == "county" and county_json:
            df = pd.read_json(county_json, orient="split")
        elif state_json:
            df = pd.read_json(state_json, orient="split")

        if df is None or map_var not in df.columns:
            return "--", "--", "--"

        series = df[map_var].dropna()
        if series.empty:
            return "0", "--", "--"

        return (
            f"{len(series):,}",
            format_value(series.mean(), map_var),
            format_value(series.std(), map_var),
        )


    # --- BAR CHART -------------------------
    @app.callback(
        Output("bar-chart", "figure"),
        Input("state-data-store", "data"),
        Input("county-data-store", "data"),
        Input("current-view-store", "data"),
        Input("map-variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_bar_chart(state_json, county_json, view, map_var):
        """Render a horizontal bar chart showing top/bottom 10 regions."""
        if not map_var:
            return _empty_map()

        df, name_col = _get_active_df(state_json, county_json, view)
        if df is None or map_var not in df.columns:
            return _empty_map()

        label = get_variable_label(map_var)
        df_sorted = df.dropna(subset=[map_var]).sort_values(by=map_var, ascending=False)

        top = df_sorted.head(10)
        bottom = df_sorted.tail(10)
        combined = pd.concat([top, bottom]).drop_duplicates()
        combined = combined.sort_values(by=map_var, ascending=True)

        colors = [
            "#e74c3c" if val < combined[map_var].median() else "#2ecc71"
            for val in combined[map_var]
        ]
        fig = go.Figure(go.Bar(
            y=combined[name_col], x=combined[map_var],
            orientation="h",
            marker_color=colors,
            hovertemplate=f"<b>%{{y}}</b><br>{label}: %{{x:,.0f}}<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=label,
            yaxis=dict(autorange=True),
            height=380,
        )
        return fig

# -- HELPER FUNCTIONS -------------------------
def _get_active_df(state_json, county_json, view):
    """Return the active DataFrame and its name column based on current view."""
    if view == "county" and county_json:
        df = pd.read_json(county_json, orient="split")
        name_col = "county_name" if "county_name" in df.columns else "NAME"
        return df, name_col
    elif state_json:
        df = pd.read_json(state_json, orient="split")
        name_col = "state_name" if "state_name" in df.columns else "NAME"
        return df, name_col
    return None, None
