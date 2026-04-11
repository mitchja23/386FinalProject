import os
import requests
import pandas as pd

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "opendata_utah_csvs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

STATE_FIPS        = "49"
CACHE_COUNTY_FIPS = "005"

PEP_URL = "https://api.census.gov/data/2019/pep/population"


def fetch_places(state: str) -> pd.DataFrame:
    """Fetch raw population estimates for all places in a state."""
    params = {
        "get": "NAME,POP,DATE_CODE",
        "for": "place:*",
        "in":  f"state:{state}",
    }
    resp = requests.get(PEP_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return pd.DataFrame(data[1:], columns=data[0])


def fetch_county(state: str, county_fips: str) -> pd.DataFrame:
    """Fetch raw population estimates for a single county."""
    params = {
        "get": "NAME,POP,DATE_CODE",
        "for": f"county:{county_fips}",
        "in":  f"state:{state}",
    }
    resp = requests.get(PEP_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return pd.DataFrame(data[1:], columns=data[0])


def save(df: pd.DataFrame, filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")


if __name__ == "__main__":
    save(fetch_places(STATE_FIPS),              "census_places_raw.csv")
    save(fetch_county(STATE_FIPS, CACHE_COUNTY_FIPS), "census_cache_county_raw.csv")
