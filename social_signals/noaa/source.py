# more info on columns https://www.ncei.noaa.gov/data/global-summary-of-the-month/doc/GSOMReadme-v1.0.3.txt
# NOAA api documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
import requests
import pandas as pd


class NOAASource:
    API_URL = "https://www.ncei.noaa.gov/cdo-web/api/v2"
    V1_API_URL = (
        "https://www.ncei.noaa.gov/access/services/data/v1"  # might be unecessary!
    )

    LIMIT = 1000
    MAX_STATIONS_LIMIT = 50

    def __init__(self, ncdc_token: str) -> None:
        self.token_header = {"token": ncdc_token}

    def request(self, url):
        response = requests.get(url, headers=self.token_header)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def get_stations(self, dataset: str = "GSOM") -> pd.DataFrame:
        url = f"{self.API_URL}/stations?datasetid={dataset}&limit={self.LIMIT}"
        data = self.request(url)
        stations_count = data["metadata"]["resultset"]["count"]
        stations_df = pd.DataFrame(data["results"])

        offset = self.LIMIT + 1
        while offset <= stations_count - self.LIMIT + 1:
            data = self.request(f"{url}&offset={offset}")
            if data:
                stations_df = pd.concat(
                    [stations_df, pd.DataFrame(data["results"])], ignore_index=True
                )
                offset += self.LIMIT

        return stations_df

    def get_monthly_data(self, stations):
        dataset_name = "global-summary-of-the-month"
        url = f"{self.V1_API_URL}?dataset={dataset_name}&startDate=0001-01-01&endDate=9996-12-31&format=json"

        station_data = self.request(f"{url}&stations={','.join(stations)}")
        return pd.DataFrame(station_data)
