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

def _empty_chart(message="No data available"):
    """Return a blank chart with a centered placeholder message."""
    fig = go.Figure()
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=20, b=20),
        annotations=[
            dict(
                text=message,
                xref="paper", yref="paper",
                x=0.5, y=0.5, 
                showarrow=False, 
                font=dict(size=14, color="#888"),
            )
        ],
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
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

        # default render based on current view
        fig = _build_map_for_toggle(
            state_end_json, state_start_json,
            county_end_json, county_start_json,
            map_var, label, year_toggle,
            start_year, end_year,
            current_view, drilldown_state,
        )
        back_style = show_back if current_view == "county" else hide_back
        return (fig, back_style, *no_county, no_update, no_update, no_update)
    
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


    # --- HISTOGRAM -------------------------
    @app.callback(
        Output("histogram-chart", "figure"),
        Input("state-data-store", "data"),
        Input("county-data-store", "data"),
        Input("current-view-store", "data"),
        Input("map-variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_histogram(state_json, county_json, view, map_var):
        """Render a histogram showing the distribution of the selected variable."""
        if not map_var:
            return _empty_chart()

        df, _ = _get_active_df(state_json, county_json, view)
        if df is None or map_var not in df.columns:
            return _empty_chart()
        label = get_variable_label(map_var)
        series = df[map_var].dropna()

        fig = px.histogram(
            series, nbins=25,
            labels={"value": label, "count": "Frequency"},
            color_discrete_sequence=["#3498db"],
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis_title=label,
            yaxis_title="Count",
            height=380,
        )

        return fig

    # --- YEAR_OVER_YEAR COMPARSISON CHART -------------------------
    @app.callback(
        Output("scatter-chart", "figure"),
        Input("state-data-store", "data"),
        Input("state-data-start-store", "data"),
        Input("county-data-store", "data"),
        Input("county-data-start-store", "data"),
        Input("current-view-store", "data"),
        Input("map-variable-dropdown", "value"),
        State("year-range-slider", "value"),
        prevent_initial_call=True,
    )
    def update_yoy_comparison(
        state_end_json, state_start_json,
        county_end_json, county_start_json,
        view, map_var, year_range,
    ):
        """Render a grouped bar chart comparing top regions across start and end years."""
        if not map_var:
            return _empty_chart()

        start_year, end_year = year_range
        df_end, name_col = _get_active_df(state_end_json, county_end_json, view)
        df_start, _ = _get_active_df(state_start_json, county_start_json, view)

        if df_end is None or df_start is None or map_var not in df_end.columns:
            return _empty_chart("Fetch data for both years first.")

        label = get_variable_label(map_var)
        top = df_end.dropna(subset=[map_var]).nlargest(12, map_var)
        names = top[name_col].tolist()

        start_vals = df_start.set_index(name_col).reindex(names)[map_var].tolist()
        end_vals = top.set_index(name_col).reindex(names)[map_var].tolist()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name=str(start_year), x=names, y=start_vals,
            marker_color="#3498db",
            hovertemplate=f"<b>%{{x}}</b><br>{start_year}: %{{y:,.0f}}<extra></extra>",
        ))
        fig.add_trace(go.Bar(
            name=str(end_year), x=names, y=end_vals,
            marker_color="#e74c3c",
            hovertemplate=f"<b>%{{x}}</b><br>{end_year}: %{{y:,.0f}}<extra></extra>",
        ))
        fig.update_layout(
            barmode="group",
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title=label,
            xaxis=dict(tickangle=-40, automargin=True),
            legend=dict(orientation="h", yanchor="top", y=1.0, x=0.5, xanchor="center"),
            height=380,
        )
        return fig

    # --- CHANGE LEADERS PIE CHART -------------------------
    @app.callback(
        Output("pie-chart", "figure"),
        Input("state-data-store", "data"),
        Input("state-data-start-store", "data"),
        Input("county-data-store", "data"),
        Input("county-data-start-store", "data"),
        Input("current-view-store", "data"),
        Input("map-variable-dropdown", "value"),
        State("year-range-slider", "value"),
        prevent_initial_call=True,
    )
    def update_change_leaders(
        state_end_json, state_start_json,
        county_end_json, county_start_json,
        view, map_var, year_range,
    ):
        """Render a bar chart of top gainers and decliners by percent change."""
        if not map_var:
            return _empty_chart()

        start_year, end_year = year_range
        df_end, name_col = _get_active_df(state_end_json, county_end_json, view)
        df_start, _ = _get_active_df(state_start_json, county_start_json, view)

        if df_end is None or df_start is None or map_var not in df_end.columns:
            return _empty_chart("Fetch data for both years first.")

        label = get_variable_label(map_var)
        merged = df_end[[name_col, map_var]].merge(
            df_start[[name_col, map_var]], on=name_col, suffixes=("_end", "_start"),
        )
        end_col = f"{map_var}_end"
        start_col = f"{map_var}_start"
        merged["pct_change"] = (
            (merged[end_col] - merged[start_col]) / merged[start_col].replace(0, float("nan"))
        ) * 100
        merged = merged.dropna(subset=["pct_change"])

        top_gainers = merged.nlargest(5, "pct_change")
        top_decliners = merged.nsmallest(5, "pct_change")
        combined = pd.concat([top_decliners, top_gainers]).drop_duplicates()
        combined = combined.sort_values(by="pct_change", ascending=True)

        colors = [
            "#e74c3c" if val < 0 else "#2ecc71" for val in combined["pct_change"]
        ]

        fig = go.Figure(go.Bar(
            x=combined["pct_change"], y=combined[name_col],
            orientation="h",
            marker_color=colors,
            hovertemplate=("<b>%{y}</b><br>% Change: %{x:.1f}%<extra></extra>"),
        ))
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=f"% Change in {label} ({start_year}-{end_year})",
            yaxis=dict(automargin=True),
            height=380,
        )

        return fig

    # --- DATA TABLE -------------------------
    @app.callback(
        Output("data-table", "columns"),
        Output("data-table", "data"),
        Input("state-data-store", "data"),
        Input("county-data-store", "data"),
        Input("current-view-store", "data"),
        State("variable-dropdown", "value"),
        prevent_initial_call=True,
    )
    def update_data_table(state_json, county_json, view, variables):
        """Populate the raw data table with readable column names for the active view."""
        if not variables:
            return [], []

        df, name_col = _get_active_df(state_json, county_json, view)
        if df is None:
            return [], []

        if isinstance(variables, str):
            variables = [variables]
        
        display_cols = [name_col] + [v for v in variables if v in df.columns]
        display_df = df[display_cols].copy()

        rename_map = {name_col: "Name"}
        for v in variables:
            if v in display_df.columns:
                rename_map[v] = get_variable_label(v)
        display_df = display_df.rename(columns=rename_map)

        columns = [{"name": c, "id": c} for c in display_df.columns]
        data = display_df.to_dict("records")
        return columns, data


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


def _build_map_for_toggle(
    state_end_json, state_start_json, county_end_json, county_start_json,
    map_var, label, year_toggle, start_year, end_year, current_view, drilldown_state,
):
    """Build a choropleth map for the selected year range and view."""
    is_county = current_view == "county" and county_end_json

    if year_toggle == "change":
        if is_county:
            df_end = pd.read_json(county_end_json, orient="split")
            df_start = pd.read_json(county_start_json, orient="split") if county_start_json else None
        else:
            df_end = pd.read_json(state_end_json, orient="split")
            df_start = pd.read_json(state_start_json, orient="split") if state_start_json else None
        
        if df_start is None:
            return _empty_map("Start-year data not available.")

        change_label = f"% Change in {label} ({start_year}-{end_year})"
        return _build_change_choropleth(
            df_end, df_start, map_var, change_label, is_county, drilldown_state
        )
    
    if year_toggle == "start":
        chosen_json = county_start_json if is_county else state_start_json
        suffix = f" ({start_year})"
    else:
        chosen_json = county_end_json if is_county else state_end_json
        suffix = f" ({end_year})"

    if not chosen_json:
        return _empty_map("No data for selected year.")

    df = pd.read_json(chosen_json, orient="split")

    if is_county:
        return _build_county_choropleth(df, map_var, label + suffix, drilldown_state)
    return _build_state_choropleth(df, map_var, label + suffix)


def _build_change_choropleth(df_end, df_start, var_code, label, is_county, state_fips):
    """Build a choropleth showing percent change between start and end year."""
    if is_county:
        merge_on = "fips"
        name_col = "county_name"
        loc_col = "fips"
    else:
        merge_on = "state"
        name_col = "state_name"
        loc_col = "state_abbrev"

    merged = df_end.merge(
        df_start[[merge_on, var_code]],
        on=merge_on, suffixes=("_end", "_start"),
    )

    end_col = f"{var_code}_end"
    start_col = f"{var_code}_start"
    merged["pct_change"] = (
        (merged[end_col] - merged[start_col]) / merged[start_col].replace(0, float("nan"))
    ) * 100

    if is_county:
        geojson = _get_county_geojson()
        filtered = [
            f for f in geojson["features"]
            if f["properties"]["STATE"] == state_fips
        ]
        filtered_geojson = {"type": "FeatureCollection", "features": filtered}
        fig = px.choropleth(
            merged, geojson=filtered_geojson,
            locations=loc_col, featureidkey="id",
            color="pct_change",
            hover_name=name_col,
            hover_data={"pct_change": ":.1f", loc_col: False},
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            labels={"pct_change": label},
        )
        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    else:
        fig = px.choropleth(
            merged,
            locations=loc_col, locationmode="USA-states",
            color="pct_change",
            hover_name=name_col,
            hover_data={"pct_change": ":.1f", loc_col: False},
            color_continuous_scale="RdYlGn",
            color_continuous_midpoint=0,
            labels={"pct_change": label},
            scope="usa",
        )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(
            title=dict(text=label, font=dict(size=10)),
            thickness=15, len=0.6,
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" + label + ": %{z:.1f}%<extra></extra>"
    )

    return fig


def _build_state_choropleth(df, var_code, label):
    """Build a state-level choropleth map for a single variable."""
    fig = px.choropleth(
        df,
        locations="state_abbrev",
        locationmode="USA-states",
        color=var_code,
        hover_name="state_name",
        hover_data={var_code: ":,.0f", "state_abbrev": False},
        color_continuous_scale="Viridis",
        labels={var_code: label},
        scope="usa",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)"),
        coloraxis_colorbar=dict(
            title=dict(text=label, font=dict(size=11)),
            thickness=15,
            len=0.6,
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" + label + ": %{z:,.0f}<extra></extra>"
    )

    return fig


def _build_county_choropleth(df, var_code, label, state_fips):
    """Build a county-level choropleth map filtered to a single state."""
    geojson = _get_county_geojson()

    filtered_features = [
        f for f in geojson["features"]
        if f["properties"]["STATE"] == state_fips
    ]
    filtered_geojson = {"type": "FeatureCollection", "features": filtered_features}

    fig = px.choropleth(
        df,
        geojson=filtered_geojson,
        locations="fips",
        featureidkey="id",
        color=var_code,
        hover_name="county_name",
        hover_data={var_code: ":,.0f", "fips": False},
        color_continuous_scale="Plasma",
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar=dict(
            title=dict(text=label, font=dict(size=11)),
            thickness=15,
            len=0.6,
        ),
    )

    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" + label + ": %{z:,.0f}<extra></extra>"
    )

    return fig