import pandas as pd
import os

master_crime = pd.read_csv("cleaned_data/master_crime_data.csv",low_memory=False)
population_data = pd.read_csv("cleaned_data/city_populations.csv")

desired_cols = ["crime_rate_per_100k", 
                "city" ,
                "season", 
                "year"]

master_crime["date"] = pd.to_datetime(master_crime["date"], errors="coerce")
master_crime["year"] = master_crime["date"].dt.year
master_crime["year"] = master_crime["year"].astype("Int64")
population_data["year"] = population_data["year"].astype("Int64")
valid_cities = set(population_data["city"].unique())
master_crime = master_crime[master_crime["city"].isin(valid_cities)]
master_crime = master_crime.dropna(subset=["season", "year"])
crime_summary = (master_crime.groupby(["city","season", "year"]).size().reset_index(name="crime_counts"))

valid_keys = population_data[["city", "year"]].drop_duplicates()

crime_summary = crime_summary.merge(
    valid_keys,
    on=["city", "year"],
    how="inner"
)

crime_summary = crime_summary.merge(
    population_data,
    on=["city", "year"],
    how="left"
)

crime_summary["crime_rate_per_100k"] = (
    crime_summary["crime_counts"] / crime_summary["population"] * 100000
)

print("years represented in master_crime:", master_crime["year"].unique())
print("\nyears represented in population_data:", population_data["year"].unique())

print("\nMaster_crime dataset missing values:\n", master_crime.isna().sum())
print("\nPopulation_dataset missing values:\n", population_data.isna().sum())

print("\ncounts of city-year pairs represented seasons \n ", crime_summary.groupby(["city", "year"])["season"].nunique().value_counts())
print("\nRows of crime_summary:", len(crime_summary))
print("\nMissing values of crime_summary:\n", crime_summary.isna().sum())

print("\ncrime_summary info:\n", crime_summary.info())

# getting ready for ANOVA

crime_summary = crime_summary[desired_cols].dropna()
crime_summary["year"] = crime_summary["year"].astype('category')
crime_summary["season"] = crime_summary["season"].astype('category')
crime_summary["city"] = crime_summary["city"].astype('category')

print("\ncrime_summary info:\n", crime_summary.info())


OUTPUT_DIR = "cleaned_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
crime_summary.to_csv(
    os.path.join(OUTPUT_DIR, "crime_summary.csv"),
    index=False
)