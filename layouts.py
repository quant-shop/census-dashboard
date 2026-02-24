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
                className="mb-3",
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