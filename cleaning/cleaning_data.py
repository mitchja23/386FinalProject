import pandas as pd 
import os
import re


city_datasets = [
    "south_salt_lake_crime.csv",
    "south_jordan_crime.csv",
    "lehi_crime.csv",
    "orem_crime.csv",
    "pleasant_grove_crime.csv",
    "santaquin_crime.csv",
    "santaquin_crime_alt.csv",
    "woods_cross_crime.csv",
    "woods_cross_data.csv",
    "syracuse_crime.csv",
    "clinton_crime.csv",
    "roy_crime.csv",
    "south_ogden_crime.csv",
    "park_city_crime.csv",
    "tooele_crime.csv",
    "logan_crime.csv",
    "smithfield_crime.csv",
    "cache_county_sheriff.csv",
    "price_crime.csv",
    "lone_peak_crime.csv",
    "uvu_campus_crime.csv"
]

agency_datasets = [
    "slc_police_cases_2013.csv",
    "slc_police_cases_2014.csv"
]

slc_assault_2012 = 'slc_assault_2012.csv'

desired_cols = [
    'case_number',
    'city',
    'incident_type_primary',
    'parent_incident_type',
    'date',
    'time_of_day',
    'day_of_week',
    'latitude',
    'longitude',
    'address',
    'zip',
    'season'
]

def add_season(df, date_col='date'):
    """
    Adds a 'season' column to a DataFrame based on a date column.

    The function converts the specified date column to datetime format and assigns
    each row a season (Spring, Summer, Fall, Winter) based on the month.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing a date column.
        date_col (str): Name of the column containing date values.

    Returns:
        pd.DataFrame: A copy of the original DataFrame with an added 'season' column.
    """
    df = df.copy()

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

    def get_season(d):
        if pd.isna(d):
            return pd.NA

        month = d.month

        if month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        elif month in [9, 10, 11]:
            return "Fall"
        else:
            return "Winter"

    df["season"] = df[date_col].apply(get_season)

    return df


def clean_city_datasets(file_list):
    """
    Cleans and standardizes multiple city-level crime datasets.

    This function reads each CSV file, standardizes column formats, cleans
    incident descriptions, extracts date and time information, normalizes
    city names, and adds a season column. Only desired columns are retained.

    Parameters:
        file_list (list): List of file paths to city crime datasets.

    Returns:
        pd.DataFrame: A single concatenated DataFrame containing cleaned data
        from all input files.
    """
    cleaned_dfs = []
    
    for file in file_list:
        df = pd.read_csv(file)
        
        if 'incident_type_primary' in df.columns:
            df['incident_type_primary'] = df['incident_type_primary'].astype(str)
            df['incident_type_primary'] = df['incident_type_primary'].apply(
                lambda x: re.sub(r'^[^\]]*\]\s*', '', x)
            )
            df['incident_type_primary'] = df['incident_type_primary'].apply(
                lambda x: re.sub(r'[^A-Za-z0-9 ]+', '', x)
            )
            df['incident_type_primary'] = df['incident_type_primary'].str.title()
        
        if 'incident_datetime' in df.columns:
            df['incident_datetime'] = pd.to_datetime(
                df['incident_datetime'],
                format='%m/%d/%Y %I:%M:%S %p',
                errors='coerce'
            )
            df['date'] = df['incident_datetime'].dt.strftime('%m/%d/%Y')
            df['time_of_day'] = df['incident_datetime'].dt.strftime('%H:%M')
        
        if 'day_of_week' in df.columns:
            df['day_of_week'] = df['day_of_week'].str.capitalize()
        
        if 'address_1' in df.columns:
            df = df.rename(columns={'address_1': 'address'})
        
        if 'city' in df.columns:
            df['city'] = df['city'].str.title() 
            df['city'] = df['city'].replace({'S Salt Lake': 'South Salt Lake'})
        

        if 'date' in df.columns:
            df = add_season(df, 'date')
        
        cols_to_keep = [col for col in desired_cols if col in df.columns]
        df = df[cols_to_keep]
        
        cleaned_dfs.append(df)
    
    return pd.concat(cleaned_dfs, ignore_index=True)


def clean_assault_dataset(file):
    """
    Cleans and standardizes the Salt Lake City assault dataset.

    This function renames columns to match the standard schema, formats
    datetime fields, extracts date and time, converts numeric day-of-week
    values to names, extracts latitude and longitude from location strings,
    and adds a season column.

    Parameters:
        file (str): File path to the assault dataset CSV.

    Returns:
        pd.DataFrame: A cleaned DataFrame containing only the desired columns.
    """
    df = pd.read_csv(file)
    
    df = df.rename(columns={
        'CASE': 'case_number',
        'OFFENSE DESCRIPTION': 'incident_type_primary',
        'DAY OF WEEK': 'day_of_week',
        'REPORT DATE': 'incident_datetime',
        'Location 1': 'address'
    })
    
    df['incident_type_primary'] = df['incident_type_primary'].str.title()
    
    df['incident_datetime'] = pd.to_datetime(
        df['incident_datetime'], 
        format='%m/%d/%Y %I:%M:%S %p', 
        errors='coerce'
    )
    df['date'] = df['incident_datetime'].dt.strftime('%m/%d/%Y')
    df['time_of_day'] = df['incident_datetime'].dt.strftime('%H:%M')
    
    df = add_season(df, 'date')
    
    day_map = {
        1: "Monday", 2: "Tuesday", 3: "Wednesday",
        4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
    }
    df['day_of_week'] = df['day_of_week'].apply(
        lambda x: day_map.get(int(x)) if str(x).isdigit() else str(x).capitalize()
    )
    
    def extract_lat_lon(location_str):
        match = re.search(r'\(([^,]+), ([^)]+)\)', str(location_str))
        if match:
            lat, lon = match.groups()
            return float(lat), float(lon)
        return None, None
    
    df['latitude'], df['longitude'] = zip(*df['LOCATION'].apply(extract_lat_lon))
    
    df['city'] = 'Salt Lake City'
    
    for col in ['parent_incident_type', 'zip']:
        if col not in df.columns:
            df[col] = pd.NA
    
    return df[desired_cols]


def clean_slc_datasets(file_list):
    """
    Cleans and standardizes Salt Lake City police datasets.

    This function processes multiple SLC police CSV files by renaming columns,
    formatting datetime fields, extracting date and time, converting day-of-week
    values, assigning a fixed city name, and adding a season column. Missing
    columns are filled as needed to match the standard schema.

    Parameters:
        file_list (list): List of file paths to SLC police datasets.

    Returns:
        pd.DataFrame: A single concatenated DataFrame of cleaned SLC data.
    """
    cleaned_dfs = []
    
    day_map = {
        1: "Monday", 2: "Tuesday", 3: "Wednesday",
        4: "Thursday", 5: "Friday", 6: "Saturday", 7: "Sunday"
    }
    
    for file in file_list:
        df = pd.read_csv(file)
        
        df = df.rename(columns={
            'CASE': 'case_number',
            'UCR DESCRIPTION': 'incident_type_primary',
            'DAY OF WEEK': 'day_of_week',
            'REPORT DATE': 'incident_datetime',
            'Location 1': 'address'
        })
        
        df['incident_type_primary'] = df['incident_type_primary'].str.title()
        
        df['incident_datetime'] = pd.to_datetime(
            df['incident_datetime'],
            format='%m/%d/%Y %I:%M:%S %p',
            errors='coerce'
        )
        df['date'] = df['incident_datetime'].dt.strftime('%m/%d/%Y')
        df['time_of_day'] = df['incident_datetime'].dt.strftime('%H:%M')
        
        df = add_season(df, 'date')
        
        df['day_of_week'] = df['day_of_week'].apply(
            lambda x: day_map.get(int(x)) if str(x).isdigit() else str(x).capitalize()
        )
        
        df['latitude'] = pd.NA
        df['longitude'] = pd.NA
        
        df['city'] = 'Salt Lake City'
        
        for col in ['parent_incident_type', 'zip']:
            if col not in df.columns:
                df[col] = pd.NA
        
        df = df[desired_cols]
        
        cleaned_dfs.append(df)
    
    return pd.concat(cleaned_dfs, ignore_index=True)


def clean_city_column(df, city_col="city"):
    """
    Standardizes and cleans the city column in a DataFrame.

    This function normalizes city names by converting to lowercase, removing
    extra text (such as commas or parentheses), expanding directional
    abbreviations (e.g., 'N.' to 'north'), mapping known variations to
    consistent names, and grouping non-city or invalid entries into a
    common category. The final city names are formatted in title case.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing a city column.
        city_col (str): Name of the column representing city names.

    Returns:
        pd.DataFrame: A copy of the DataFrame with a cleaned and standardized
        city column.
    """
    df = df.copy()
    df[city_col] = df[city_col].astype(str).str.strip().str.lower()
    df[city_col] = df[city_col].apply(
        lambda x: re.sub(r",.*|\(.*?\)", "", x)
    )

    def expand_dirs(x):
        x = re.sub(r"^n\.?\s+", "north ", x)
        x = re.sub(r"^s\.?\s+", "south ", x)
        x = re.sub(r"^e\.?\s+", "east ", x)
        x = re.sub(r"^w\.?\s+", "west ", x)
        return x

    df[city_col] = df[city_col].apply(expand_dirs)

    alias_map = {
        "slc": "salt lake city",
        "salt lake cty": "salt lake county",
        "salt lake cnty": "salt lake county",
        "s salt lake": "south salt lake",
        "south salt lake city": "south salt lake",
        "w valley city": "west valley city",
        "west valley": "west valley city",
        "s jordan city": "south jordan",
        "south jordan city": "south jordan",
        "too": "tooele",
        "tooele army depot": "tooele",
        "tooele city": "tooele",
        "juab nephi": "nephi",
        "Juab Co Mon Gr": "juab county"
        
    }

    df[city_col] = df[city_col].replace(alias_map)

    other = { # the only county we are keeping is Cache because we have population data for it.
        "interstate",
        "county nw",
        "other",
        "byu campus",
        "temp",
        "q",
        "parleys canyon",
        "logan canyon",
        "weber canyon",
        "utah valley u",
        "salt lake county",
        "davis county",
        "summit county",
        "wasatch county",
        "tooele county",
        "juab county",
        "utah county",
        "emery county"
    }

    df.loc[df[city_col].isin(other), city_col] = "county/interstate/other"

    missing = df[city_col].isna()

    numeric = df[city_col].apply(
        lambda x: isinstance(x, (int, float)) or
                  (isinstance(x, str) and x.replace('.', '', 1).isdigit())
    )

    df.loc[missing | numeric, city_col] = "county/interstate/other"

    df[city_col] = (
        df[city_col]
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
        .str.title()
    )
    return df


if __name__ == "__main__":
    master_crime_df = clean_city_datasets(city_datasets)
    master_assault_df = clean_assault_dataset(slc_assault_2012)
    master_slc_df = clean_slc_datasets(agency_datasets)
    master_all_df = pd.concat([master_crime_df, master_assault_df, master_slc_df], ignore_index=True)
    master_all_df = clean_city_column(master_all_df)

    OUTPUT_DIR = "cleaned_data"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(OUTPUT_DIR, "master_crime_data.csv")
    master_all_df.to_csv(output_file, index=False)

    print(f"Master dataset saved to {output_file}")