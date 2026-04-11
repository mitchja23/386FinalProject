import os
import pandas as pd

DATA = os.path.join(os.path.dirname(__file__), '..', 'cleaned_data', 'master_crime_data.csv')

CATEGORY = {
    'Violent':  ['Assault', 'Robbery', 'Homicide', 'Sexual Assault',
                 'Kidnapping', 'Family Offense'],
    'Property': ['Theft', 'Breaking & Entering', 'Property Crime',
                 'Fraud', 'Alarm', 'Vehicle Theft'],
    'Drugs':    ['Drugs', 'Liquor'],
}

LON_MIN, LON_MAX = -114.2, -109.0
LAT_MIN, LAT_MAX =  36.8,   42.1


class DataLoader:
    def load(self) -> pd.DataFrame:
        print("Loading data…")
        df = pd.read_csv(DATA, low_memory=False)
        print(f"  {len(df):,} rows loaded")

        df = df.dropna(subset=['latitude', 'longitude'])
        df = df[
            df['longitude'].between(LON_MIN, LON_MAX) &
            df['latitude'].between(LAT_MIN, LAT_MAX)
        ]

        df['year'] = (
            pd.to_datetime(df['date'], format='%m/%d/%Y', errors='coerce')
            .dt.year
        )
        df = df.dropna(subset=['year'])
        df['year'] = df['year'].astype(int)
        df = df[df['year'].between(2007, 2019)]

        df['latitude']  = df['latitude'].round(4)
        df['longitude'] = df['longitude'].round(4)
        df['category']  = df['parent_incident_type'].map(self._assign)

        return df

    def _assign(self, parent_type):
        if pd.isna(parent_type):
            return 'Other'
        for cat, types in CATEGORY.items():
            if parent_type in types:
                return cat
        return 'Other'
