import pandas as pd
import pytest
from cleaning.cleaning_data import add_season, clean_city_column


def make_df(dates):
    return pd.DataFrame({"date": dates})


class TestAddSeason:
    def test_spring(self):
        df = add_season(make_df(["03/15/2015"]))
        assert df["season"].iloc[0] == "Spring"

    def test_summer(self):
        df = add_season(make_df(["07/04/2015"]))
        assert df["season"].iloc[0] == "Summer"

    def test_fall(self):
        df = add_season(make_df(["10/31/2015"]))
        assert df["season"].iloc[0] == "Fall"

    def test_winter(self):
        df = add_season(make_df(["01/01/2015"]))
        assert df["season"].iloc[0] == "Winter"

    def test_missing_date(self):
        df = add_season(make_df([None]))
        assert pd.isna(df["season"].iloc[0])

    def test_does_not_mutate_input(self):
        original = make_df(["06/01/2015"])
        add_season(original)
        assert "season" not in original.columns


class TestCleanCityColumn:
    def _clean(self, city):
        df = pd.DataFrame({"city": [city]})
        return clean_city_column(df)["city"].iloc[0]

    def test_slc_alias(self):
        assert self._clean("slc") == "Salt Lake City"

    def test_west_valley_alias(self):
        assert self._clean("west valley") == "West Valley City"

    def test_south_jordan_alias(self):
        assert self._clean("south jordan city") == "South Jordan"

    def test_directional_expansion(self):
        assert self._clean("n. Salt Lake") == "North Salt Lake"

    def test_interstate_to_other(self):
        assert self._clean("interstate") == "County/Interstate/Other"

    def test_title_case_output(self):
        result = self._clean("logan")
        assert result == result.title()

    def test_strips_comma_suffix(self):
        result = self._clean("salt lake city, ut")
        assert "," not in result
