import pandas as pd
import os

OUTPUT_DIR = "opendata_utah_csvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_URL = "https://opendata.utah.gov/api/views/{}/rows.csv?accessType=DOWNLOAD"

datasets = {
    "south_salt_lake_crime": "5vqv-s2y7",
    "south_jordan_crime": "hk59-zfhg",
    "slc_police_cases_2014": "w3tk-jffw",
    "slc_police_cases_2013": "qzws-whfr",
    "slc_county_crime_by_city": "rkty-2cpr",
    "slc_assault_2012": "ezpq-caqa",
    "lehi_crime": "2wag-9dir", 
    "orem_crime": "52dt-95n9",
    "pleasant_grove_crime": "79pd-96z2",
    "santaquin_crime": "bqmw-t5wq",
    "santaquin_crime_alt": "vmwx-eahh",
    "woods_cross_crime": "p5ia-x66i",
    "woods_cross_data": "4pjj-r8a6",
    "syracuse_crime": "9pk9-3f6p",
    "clinton_crime": "mfwr-np3m",
    "roy_crime": "4vsb-pg3i",
    "south_ogden_crime": "r65x-476f",
    "park_city_crime": "gnrv-nqtq",
    "tooele_crime": "75qj-bajn",
    "logan_crime": "inki-w62p",
    "smithfield_crime": "vjx3-6jxv",
    "cache_county_sheriff": "5tai-5haw",
    "price_crime": "vna8-ubfu",
    "lone_peak_crime": "nvzw-m4zy",
    "uvu_campus_crime": "55c6-9cpm",
}


def download(name, dataset_id):
    url = BASE_URL.format(dataset_id)
    try:
        df = pd.read_csv(url, low_memory=False)

        filepath = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(filepath, index=False)

        print(f"{name}: {len(df)} rows saved")
        return True

    except Exception as e:
        print(f"{name}: FAILED: {e}")
        return False


if __name__ == "__main__":
    success = 0
    failed = 0
    failedList = []

    for name, dataset_id in datasets.items():
        if download(name, dataset_id):
            success += 1
        else:
            failed += 1
            failedList.append(name)

    print(f"{success} downloaded, {failed} failed")
    print(f"Files saved in: {OUTPUT_DIR}/")
    if failedList:
        print(f"\nFailed datasets:")
        for f in failedList:
            print(f"  - {f}")