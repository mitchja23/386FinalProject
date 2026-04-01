import pandas as pd 
from pathlib import Path
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
    'zip'
]


def clean_city_datasets(file_list):
    """
    Cleans multiple crime datasets and stacks them into one master DataFrame.
    
    Steps:
    - Cleans 'incident_type_primary': removes brackets, special characters, capitalizes words
    - Splits 'incident_datetime' into 'date' and 'time_of_day' in 24-hour format
    - Capitalizes 'day_of_week'
    - Drops 'location' column if present
    - Renames 'address_1' to 'address'
    - Standardizes city names
    - Keeps only the specified columns in order
    - Stacks all datasets into one master DataFrame
    """
    cleaned_dfs = []
    
    for file in file_list:
        df = pd.read_csv(file)
        name = Path(file).stem
        
        if 'location' in df.columns:
            df = df.drop(columns=['location'])
        
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
        
    
        cols_to_keep = [col for col in desired_cols if col in df.columns]
        df = df[cols_to_keep]
        
        cleaned_dfs.append(df)
    
    city_df = pd.concat(cleaned_dfs, ignore_index=True)
    
    return city_df


def clean_assult_dataset(file):
    """
    Cleans a single new-style crime dataset to match the master dataset format.
    All rows are assigned city = 'Salt Lake City'.
    
    Steps:
    - Maps columns to master dataset names
    - Converts numeric day_of_week to weekday names
    - Splits incident_datetime into date & time_of_day in 24-hour format
    - Extracts latitude & longitude from LOCATION
    - Capitalizes incident_type_primary
    - Renames address
    - Adds missing columns (city, parent_incident_type, zip)
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
    
    day_map = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
    }
    df['day_of_week'] = df['day_of_week'].apply(
        lambda x: day_map.get(int(x)) if str(x).isdigit() else str(x).capitalize()
    )
    
    def extract_lat_lon(location_str):
        match = re.search(r'\(([^,]+), ([^)]+)\)', str(location_str))
        if match:
            lat, lon = match.groups()
            return float(lat), float(lon)
        else:
            return None, None
    
    df['latitude'], df['longitude'] = zip(*df['LOCATION'].apply(extract_lat_lon))
    
    df['city'] = 'Salt Lake City'
    
    for col in ['parent_incident_type', 'zip']:
        if col not in df.columns:
            df[col] = pd.NA
    
    assult_df = df[desired_cols]
    
    return assult_df


def clean_slc_datasets(file_list):
    """
    Cleans multiple traffic-style crime datasets and stacks them into one DataFrame
    matching the master dataset format.
    
    Steps:
    - Maps columns to master dataset
    - Converts numeric day_of_week to weekday names
    - Splits REPORT DATE into date & time_of_day (24-hour format)
    - Capitalizes incident_type_primary
    - Renames Location 1 to address
    - Fills city with 'Salt Lake City'
    - Adds missing columns (parent_incident_type, zip)
    - Keeps latitude & longitude as NaN for compatibility
    """
    cleaned_dfs = []
    
    day_map = {
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday",
        7: "Sunday"
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
    
    slc_df = pd.concat(cleaned_dfs, ignore_index=True)
    
    return slc_df


master_crime_df = clean_city_datasets(city_datasets)
master_assult_df = clean_assult_dataset(slc_assault_2012)
master_slc_df = clean_slc_datasets(agency_datasets)


print(len(master_crime_df))
print(master_crime_df.info())
print(master_crime_df.head())

print(len(master_assult_df))
print(master_assult_df.info())
print(master_assult_df.head())

print(len(master_slc_df))
print(master_slc_df.info())
print(master_slc_df.head())

OUTPUT_DIR = "cleaned_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
master_all_df = pd.concat([master_crime_df, master_assult_df, master_slc_df], ignore_index=True)
output_file = os.path.join(OUTPUT_DIR, "master_crime_data.csv")
master_all_df.to_csv(output_file, index=False)
print(f"Master dataset saved to {output_file}")
