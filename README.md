# Census Data Explorer

An interactive web dashboard for exploring US Census American Community Survey (ACS) 5-year data at state and county levels. Visualize demographic, economic, housing, and education variables with choropleth maps, charts, and data tables.

## Features

- **Interactive choropleth map** — View data for all US states or drill down to counties by selecting a state
- **Year-over-year comparison** — Toggle between start year, end year, or % change views
- **32+ curated variables** across 7 categories: Demographics, Race/Ethnicity, Income/Poverty, Education, Employment, Housing, Rent Burden
- **Custom variable input** — Add any Census variable code (e.g. `B19013_001E`) for temporary exploration
- **Summary statistics** — Count, mean, and standard deviation for the active view
- **Charts** — Top/bottom rankings bar chart, distribution histogram, YoY comparison, change leaders
- **Raw data table** — Sortable, filterable table with CSV export

## Prerequisites

- Python 3.10+
- Free Census API key from [api.census.gov/data/key_signup.html](https://api.census.gov/data/key_signup.html)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd census_dashboard

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install dependencies
pip install dash dash-bootstrap-components pandas census plotly requests python-dotenv
```

## Configuration

Create a `.env` file in the project root with your Census API key:

```
CENSUS_API_KEY=your_api_key_here
```

Alternatively, you can enter your API key in the app modal when you first load the dashboard.

## Running the App

```bash
python app.py
```

Open [http://127.0.0.1:7070/](http://127.0.0.1:7070/) in your browser.

## Project Structure

| File | Description |
|------|-------------|
| `app.py` | Dash app entry point |
| `layouts.py` | UI layout components |
| `callbacks.py` | Dash callbacks and map/chart logic |
| `census_client.py` | Census API client (fetch states, counties, validate key) |
| `config.py` | Variables, year range, FIPS mappings, GeoJSON URL |
| `test/` | Test scripts for census_client |

## License

See [LICENSE](LICENSE) for details.
