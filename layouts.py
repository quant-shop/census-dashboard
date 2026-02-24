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