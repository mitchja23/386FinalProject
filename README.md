# Utah Crime Incident Rate Analysis

An analysis of crime incident rates across Utah municipalities from 2007 to 2019. This project investigates whether crime rates vary by **city**, **year**, or **season** using publicly available police report data and U.S. Census population estimates.

**Key finding:** City and year are statistically significant predictors of crime rates; season is not (two-way ANOVA, p > 0.05 for season).

## Links

- [Documentation & API Reference](https://mitchja23.github.io/386FinalProject/api)
- [Tutorial](https://mitchja23.github.io/386FinalProject/tutorial)
- [Technical Report](https://mitchja23.github.io/386FinalProject/report)
- [Streamlit App](https://mitchja23-386finalproject.streamlit.app)
- [GitHub Repo](https://github.com/mitchja23/386FinalProject)

## Dataset

- **Source:** 24 city-level crime datasets from the [Utah Open Data Portal](https://opendata.utah.gov) and 2 Salt Lake City police agency files
- **Population:** U.S. Census Bureau estimates via the Census API (Utah places + Cache County, 2007–2019)
- **Coverage:** ~20 Utah municipalities including Salt Lake City, Provo, Logan, Ogden, and surrounding cities
- **Output metric:** Incident rate per 100,000 residents, aggregated by city × season × year

The dataset is custom-assembled from raw government sources and not available as a pre-packaged dataset elsewhere.

## Installation

```bash
git clone https://github.com/mitchja23/386FinalProject.git
cd 386FinalProject
pip install -e .
```

## Usage

### Run the interactive web visualization

```bash
python run.py
```

Opens a Leaflet.js heatmap in your browser with year and crime-category filters.

### Run the Streamlit app locally

```bash
streamlit run streamlit_app.py
```

### Use cleaning functions in Python

```python
from cleaning import add_season, clean_city_column
import pandas as pd

df = pd.DataFrame({"date": ["03/15/2015", "07/04/2015", "12/25/2015"]})
df = add_season(df)
print(df["season"])  
```

### Reproduce the full data pipeline

```bash
# 1. Download raw data from Utah Open Data Portal
python scrapping/utahOpenportal.py
python scrapping/scrape_population.py   

# 2. Clean and merge datasets
python cleaning/cleaning_data.py        
python cleaning/clean_analysis_data.py  

# 3. Run ANOVA analysis
python Analysis/incident_rate_model.py
```

## Project Structure

```
386FinalProject/
├── cleaning/           # Data cleaning functions (importable package)
├── scrapping/          # Data collection scripts
├── Analysis/           # ANOVA analysis and results
├── visualizations/     # JavaScript heatmap visualization
├── docs/               # GitHub Pages documentation
├── tests/              # Pytest unit tests
├── streamlit_app.py    # Streamlit dashboard
├── run.py              # Web visualization launcher
└── pyproject.toml      # Package configuration
```

## Running Tests

```bash
pytest tests/
```
