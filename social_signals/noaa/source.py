# more info on columns https://www.ncei.noaa.gov/data/global-summary-of-the-month/doc/GSOMReadme-v1.0.3.txt
# NOAA api documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
import requests
import pandas as pd


class NOAASource:
    API_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    V1_API_URL = (
        "https://www.ncei.noaa.gov/access/services/data/v1"  # might be unnecessary!
    )

    STATIONS_LIMIT = 1000

    SUMMARY_STATIONS_LIMIT = 50
    SUMMARY_COLUMNS = [
        "EMXP",
        "EMXT",
        "DYSD",
        "PRCP",
        "DP10",
        "DX90",
        "DX70",
        "EMNT",
        "DT32",
        "DYSN",
        "DX32",
        "TMAX",
        "EMSD",
        "STATION",
        "EMSN",
        "DSND",
        "SNOW",
        "CDSD",
        "DP01",
        "DYXP",
        "HTDD",
        "DT00",
        "DATE",
        "DYXT",
        "DP1X",
        "CLDD",
        "DSNW",
        "TAVG",
        "TMIN",
        "DYNT",
        "DYTS",
        "HDSD",
    ]

    def __init__(self, ncdc_token: str) -> None:
        self.token_header = {"token": ncdc_token}

    def request(self, url) -> dict | None:
        response = requests.get(url, headers=self.token_header)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def get_stations(self, dataset: str = "GSOM") -> pd.DataFrame:
        url = f"{self.API_URL}/stations?datasetid={dataset}&limit={self.STATIONS_LIMIT}"
        data = self.request(url)
        stations_count = data["metadata"]["resultset"]["count"]
        stations_df = pd.DataFrame(data["results"])

        offset = self.STATIONS_LIMIT + 1
        while offset < stations_count:
            data = self.request(f"{url}&offset={offset}")
            if data:
                stations_df = pd.concat(
                    [stations_df, pd.DataFrame(data["results"])], ignore_index=True
                )
                offset += self.STATIONS_LIMIT

        return stations_df

    def get_stations_data(
        self, *, dataset: str = "global-summary-of-the-month", stations: list[str]
    ) -> pd.DataFrame:
        url = f"{self.V1_API_URL}?dataset={dataset}&startDate=0001-01-01&endDate=9996-12-31&format=json"

        stations_data = pd.DataFrame(columns=self.SUMMARY_COLUMNS)

        offset = 0
        while offset < len(stations):
            data = self.request(
                f"{url}&stations={','.join(stations[offset:offset+self.SUMMARY_STATIONS_LIMIT])}"
            )
            if data:
                stations_data = pd.concat(
                    [stations_data, pd.DataFrame(data)], ignore_index=True
                )
                offset += self.SUMMARY_STATIONS_LIMIT

        return stations_data
