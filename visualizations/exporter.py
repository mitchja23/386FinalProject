import os
import json
import pandas as pd

YEARS = [str(y) for y in range(2007, 2020)]
CATEGORIES = ['All', 'Violent', 'Property', 'Drugs']
MAX_HEAT_PTS = 5000
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'data', 'crime_data.json')


class Exporter:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def run(self):
        payload = {
            'heatmap':    self.heatmap(),
            'bar_charts': self.barCharts(),
            'stats':      self.stats(),
        }
        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        with open(OUTPUT_PATH, 'w') as f:
            json.dump(payload, f, separators=(',', ':'))

    def heatmap(self) -> dict:
        result = {}
        for cat in CATEGORIES:
            result[cat] = {}
            for year in YEARS:
                subset = self.subset(cat, int(year))
                if len(subset) > MAX_HEAT_PTS:
                    subset = subset.sample(MAX_HEAT_PTS, random_state=42)
                result[cat][year] = subset[['latitude', 'longitude']].values.tolist()
        return result

    def barCharts(self) -> dict:
        result = {}
        for year in YEARS:
            vc = (
                self.df[self.df['year'] == int(year)]['city']
                .value_counts()
                .head(10)
            )
            result[year] = {
                'cities': vc.index.tolist(),
                'counts': [int(v) for v in vc.values],
            }
        return result

    def stats(self) -> dict:
        result = {}
        for cat in CATEGORIES:
            result[cat] = {}
            prev_total = None
            for year in YEARS:
                subset = self.subset(cat, int(year))
                total = len(subset)

                pct_change = None
                if prev_total is not None and prev_total > 0:
                    pct_change = round((total - prev_total) / prev_total * 100, 1)

                year_all = self.df[self.df['year'] == int(year)]
                peak_city = (
                    year_all['city'].value_counts().idxmax()
                    if len(year_all) > 0 else '–'
                )

                result[cat][year] = {
                    'total':      total,
                    'pct_change': pct_change,
                    'peak_city':  str(peak_city) if pd.notna(peak_city) else '–',
                }
                prev_total = total
        return result

    def subset(self, cat: str, year: int) -> pd.DataFrame:
        mask = self.df['year'] == year
        if cat != 'All':
            mask &= self.df['category'] == cat
        return self.df[mask]
