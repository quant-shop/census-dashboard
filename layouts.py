from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc

from config import *

def build_api_key_modal():
    """Build a modal dialog prompting the user for their Census API key."""
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Census API Key Required"), close_button=False),
            dbc.ModalBody([
                html.P(
                    "Enter your free Census Bureau API key to get started. "
                    "Don't have one? ",
                    className="mb-2",
                ),
                html.A(
                    "Get a free API key here",
                    href="https://api.census.gov/data/key_signup.html",
                    target="_blank",
                    className="mb-3 d-block",
                ),
                dbc.Input(
                    id="api-key-input",
                    type="password",
                    placeholder="Paste your Census API key...",
                    className="mb-2",
                ),
                dbc.Alert(
                    id="api-key-error",
                    color="danger",
                    is_open=False,
                    children="Invalid API key. Please try again.",
                ),
            ]),
            dbc.ModalFooter(
                dbc.Button(
                    "Connect",
                    id="api-key-submit",
                    color="primary",
                    n_clicks=0,
                )
            ),
        ],
        id="api-key-modal",
        is_open=True,
        backdrop="static",
        keyboard=False,
    )


def build_sidebar():
    """Build the sidebar with year range, state, and variable controls."""
    return dbc.Card(
        dbc.CardBody([
            html.H5("Controls", className="mb-3 fw-bold"),

            dbc.Label("Year Range", className="fw-semibold"),
            dcc.RangeSlider(
                id="year-range-slider",
                min=MIN_YEAR,
                max=MAX_YEAR,
                step=1,
                value=DEFAULT_YEAR_RANGE,
                marks={y: {"label": str(y)} for y in range(MIN_YEAR, MAX_YEAR + 1, 2)},
                tooltip={"placement": "bottom", "always_visible": False},
                allowCross=False,
                className="mb-1",
            ),
            html.Div(
                id="year-range-label",
                className="text-center text-muted small mb-3",
                children=f"Comparing {DEFAULT_YEAR_RANGE[0]} vs {DEFAULT_YEAR_RANGE[1]}",
            ),

            dbc.Label("State", className="fw-semibold"),
            dcc.Dropdown(
                id="state-dropdown",
                options=STATE_OPTIONS,
                value=None,
                placeholder="All States",
                clearable=True,
                className="mb-3",
            ),

            dbc.Label("Variables", className="fw-semibold"),
            dcc.Dropdown(
                id="variable-dropdown",
                options=VARIABLE_OPTIONS,
                value=DEFAULT_VARIABLES,
                multi=True,
                placeholder="Select variables...",
                className="mb-2",
            ),

            dbc.Label("Add Custom Variable", className="fw-semibold small mt-1"),
            dbc.InputGroup([
                dbc.Input(
                    id="custom-var-input",
                    type="text",
                    placeholder="e.g. B19013_001E",
                    size="sm",
                ),
                dbc.Button(
                    "Add",
                    id="add-custom-var-button",
                    color="outline-secondary",
                    size="sm",
                    n_clicks=0,
                ),
            ], size="sm", className="mb-1"),
            html.Div(
                id="custom-var-feedback",
                className="small mb-3",
            ),

            dbc.Button(
                [html.I(className="fas fa-download me-2"), "Fetch Data"],
                id="fetch-button",
                color="primary",
                className="w-100 mb-3",
                n_clicks=0,
            ),

            html.Hr(),

            html.Div(id="status-text", className="text-muted small"),
        ]),
        className="sidebar-card h-100",
    )


def build_map_card():
    """Build the interactive choropleth map card with variable and year toggle controls."""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.H5("Interactive Map", className="fw-bold mb-0 pt-1"),
                    width="auto",
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="map-variable-dropdown",
                        options=[],
                        value=None,
                        clearable=False,
                        placeholder="Select variable to map...",
                        style={"minWidth": "280px"},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dcc.RadioItems(
                        id="map-year-toggle",
                        options=[
                            {"label": "Start Year", "value": "start"},
                            {"label": "End Year", "value": "end"},
                            {"label": "% Change", "value": "change"},
                        ],
                        value="end",
                        inline=True,
                        className="small",
                        inputClassName="me-1",
                        labelClassName="me-3",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        "Back to US Map",
                        id="back-button",
                        color="secondary",
                        size="sm",
                        style={"display": "none"},
                    ),
                    width="auto",
                ),
            ], align="center", className="mb-2 g-2", justify="start"),
            dcc.Loading(
                dcc.Graph(
                    id="map-figure",
                    config={"displayModeBar": True, "scrollZoom": True},
                    style={"height": "520px"},
                ),
                type="circle",
            ),
        ]),
        className="mb-3",
    )


def build_stats_cards():
    """Build the cards that will display key statistics and comparisons."""
    return dbc.Row(
        [
            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Regions", className="text-muted small mb-1"),
                html.H4(id="stat-count", children="--", className="fw-bold mb-0"),
            ])), md=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Mean", className="text-muted small mb-1"),
                html.H4(id="stat-mean", children="--", className="fw-bold mb-0"),
            ])), md=3),

            dbc.Col(dbc.Card(dbc.CardBody([
                html.P("Std Dev", className="text-muted small mb-1"),
                html.H4(id="stat-std", children="--", className="fw-bold mb-0"),
            ])), md=3), 
        ],
        className="mb-3 g-3",
    )

def build_charts_row():
    """Build the row containing the rankings bar chart and distribution histogram."""
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("Top / Bottom Rankings", className="fw-bold"),
                    dcc.Loading(
                        dcc.Graph(id="bar-chart",style={"height":"380px"}),
                        type="circle",
                    ),
                ])),
                lg=6,
                className="mb-3",
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("Distribution", className="fw-bold"),
                    dcc.Loading(
                        dcc.Graph(id="histogram-chart", style={"height": "380px"}),
                        type="circle",
                    ),
                ])),
                lg=6,
                className="mb-3",
            ),
        ],
        className="g-3",
    )


def build_secondary_charts_row():
    """Build the row with year-over-year scatter chart and change leaders pie chart."""
    return dbc.Row(
        [
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("Year-over-Year Comparison", className="fw-bold"),
                    dcc.Loading(
                        dcc.Graph(id="scatter-chart", style={"height": "380px"}),
                        type="circle",
                    ),
                ])),
                lg=6,
                className="mb-3",
            ),
            dbc.Col(
                dbc.Card(dbc.CardBody([
                    html.H6("Change Leaders", className="fw-bold"),
                    dcc.Loading(
                        dcc.Graph(id="pie-chart", style={"height": "380px"}),
                        type="circle",
                    ),
                ])),
                lg=6,
                className="mb-3",
            ),
        ],
        className="g-3",
    )


def build_data_table():
    """Build a sortable, filterable data table with CSV export button."""
    return dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col(
                    html.H6("Raw Data Table", className="fw-bold mb-0 pt-1"),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button(
                        [html.I(className="fas fa-file-csv me-2"), "Export CSV"],
                        id="export-csv-button",
                        color="outline-primary",
                        size="sm",
                    ),
                    width="auto",
                    className="ms-auto",
                ),
            ], align="center", className="mb-3"),
            dcc.Download(id="download-csv"),
            dash_table.DataTable(
                id="data-table",
                columns=[],
                data=[],
                page_size=15,
                sort_action="native",
                filter_action="native",
                style_table={"overflowX": "auto"},
                style_header={
                    "backgroundColor": "#f1f3f5",
                    "fontWeight": "600",
                    "textAlign": "left",
                    "padding": "10px 14px",
                    "fontSize": "13px",
                    "minWidth": "120px",
                    "borderBottom": "2px solid #dee2e6",
                },
                style_cell={
                    "textAlign": "left",
                    "padding": "8px 14px",
                    "fontSize": "13px",
                    "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
                    "minWidth": "120px",
                    "maxWidth": "300px",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis",
                },
                style_data={
                    "borderBottom": "1px solid #eee",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#f8f9fa",
                    },
                    {
                        "if": {"state": "active"},
                        "backgroundColor": "#e8f4fd",
                        "border": "1px solid #3498db",
                    },
                ],
            ),
        ]),
        className="mb-3",
    )


def build_layout():
    """Assemble the full dashboard layout with navbar, sidebar, charts, and data table."""
    return dbc.Container(
        [
            build_api_key_modal(),

            dcc.Store(id="api-key-store", storage_type="session"),
            dcc.Store(id="state-data-store"),
            dcc.Store(id="state-data-start-store"),
            dcc.Store(id="county-data-store"),
            dcc.Store(id="county-data-start-store"),
            dcc.Store(id="current-view-store", data="states"),
            dcc.Store(id="drilldown-state-store"),

            dbc.Navbar(
                dbc.Container([
                    dbc.NavbarBrand(
                        [html.I(className="fas fa-chart-bar me-2"), "Census Data Explorer"],
                        className="fw-bold fs-4"
                    ),
                    dbc.NavbarToggler(id="navbar-toggler"),
                    html.Span("US CENSUS BUREAU ACS 5-YEAR ESTIMATES", className="text-light opacity-75 small",
                    ),
                ], fluid=True),
                color="dark",
                className="mb-4",
            ),

            dbc.Row(
                [
                    dbc.Col(build_sidebar(), lg=3, md=4, className="mb-3"),
                    dbc.Col(
                        [
                            build_map_card(),
                            build_stats_cards(),
                            build_charts_row(),
                            build_secondary_charts_row(),
                            build_data_table(),
                        ],
                        lg=9,
                        md=8,
                    ),
                ],
                className="g-3"
            ),

            html.Footer(
                html.P("Data sourced from the US Census Bureau American Community. ",
                       className="text-center text-muted small py-3"
                ),
            ),
        ],
        fluid=True,
        className="px-4 pb-4",
    )