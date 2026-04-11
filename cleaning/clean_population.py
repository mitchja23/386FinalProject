import os
import pandas as pd

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INPUT_DIR    = os.path.join(PROJECT_ROOT, "opendata_utah_csvs")
OUTPUT_DIR   = os.path.join(PROJECT_ROOT, "cleaned_data")
OUTPUT_FILE  = os.path.join(OUTPUT_DIR, "city_populations.csv")

DATE_CODE_TO_YEAR = {
    "2":  2010,
    "3":  2011,
    "4":  2012,
    "5":  2013,
    "6":  2014,
    "7":  2015,
    "8":  2016,
    "9":  2017,
    "10": 2018,
    "11": 2019,
}

# Maps our crime data city label to Census place name 
CITY_NAME_MAP = {
    "South Salt Lake": "South Salt Lake city",
    "South Jordan":    "South Jordan city",
    "Salt Lake City":  "Salt Lake City city",
    "Lehi":            "Lehi city",
    "Orem":            "Orem city",
    "Pleasant Grove":  "Pleasant Grove city",
    "Santaquin":       "Santaquin city",
    "Woods Cross":     "Woods Cross city",
    "Syracuse":        "Syracuse city",
    "Clinton":         "Clinton city",
    "Roy":             "Roy city",
    "South Ogden":     "South Ogden city",
    "Park City":       "Park City city",
    "Tooele":          "Tooele city",
    "Logan":           "Logan city",
    "Smithfield":      "Smithfield city",
    "Price":           "Price city",
}


def clean_places(df_raw: pd.DataFrame) -> pd.DataFrame:
    census_to_label = {v: k for k, v in CITY_NAME_MAP.items()}

    df = df_raw.copy()
    df["place_name"] = df["NAME"].str.split(",").str[0].str.strip()
    df = df[df["place_name"].isin(census_to_label)].copy()

    df["city"]       = df["place_name"].map(census_to_label)
    df["year"]       = df["DATE_CODE"].map(DATE_CODE_TO_YEAR)
    df["population"] = pd.to_numeric(df["POP"])
    df = df[df["year"].notna()]

    missing = set(CITY_NAME_MAP) - set(df["city"].unique())
    if missing:
        print(f"No data found for: {sorted(missing)}")

    return df[["city", "year", "population"]].sort_values(["city", "year"]).reset_index(drop=True)


def clean_county(df_raw: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df_raw.copy()
    df["city"]       = label
    df["year"]       = df["DATE_CODE"].map(DATE_CODE_TO_YEAR)
    df["population"] = pd.to_numeric(df["POP"])
    df = df[df["year"].notna()]
    return df[["city", "year", "population"]].sort_values("year").reset_index(drop=True)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_places = pd.read_csv(os.path.join(INPUT_DIR, "census_places_raw.csv"), dtype=str)
    raw_county = pd.read_csv(os.path.join(INPUT_DIR, "census_cache_county_raw.csv"), dtype=str)

    df_places = clean_places(raw_places)
    df_county = clean_county(raw_county, label="Cache County")

    df_all = (
        pd.concat([df_places, df_county], ignore_index=True)
        .sort_values(["city", "year"])
        .reset_index(drop=True)
    )

    df_all.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved {len(df_all)} rows to {OUTPUT_FILE}")
