# more info on columns https://www.ncei.noaa.gov/data/global-summary-of-the-month/doc/GSOMReadme-v1.0.3.txt
# NOAA api documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
import requests
import pandas as pd


class NOAASource:
    """
    Class for interacting with NOAA (National Oceanic and Atmospheric Administration) data sources.

    Attributes:
    - API_URL: Base URL for NOAA API v2.
    - V1_API_URL: Base URL for NOAA API v1 (legacy api, may be unnecessary in the future).
    - STATIONS_LIMIT: Maximum number of stations to retrieve in a single request.
    - SUMMARY_STATIONS_LIMIT: Maximum number of stations to retrieve climate data in a single request.
    - SUMMARY_COLUMNS: List of columns of the GSOM dataset.

    Methods:
    - __init__: Constructor for the NOAASource class.
    - request: Send an HTTP GET request and return the JSON response.
    - get_stations: Retrieve information about NOAA weather stations.
    - get_stations_data: Retrieve weather data for a list of NOAA weather stations.
    """

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

    def __init__(self, noaa_token: str) -> None:
        """
        Constructor for the NOAASource class.

        Parameters:
        - ncdc_token: Token for accessing NOAA API (https://www.ncdc.noaa.gov/cdo-web/token).
        """

        self.token_header = {"token": noaa_token}

    def request(self, url) -> dict | None:
        """
        Send an HTTP GET request and return the JSON response.

        Parameters:
        - url: The URL for the HTTP GET request.

        Returns:
        The JSON response as a dictionary, or None if the request fails.
        """

        response = requests.get(url, headers=self.token_header)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def get_stations(self, dataset: str = "GSOM") -> pd.DataFrame:
        """
        Retrieve information about NOAA weather stations.

        Parameters:
        - dataset: The dataset ID for weather stations (default is "GSOM").

        Returns:
        A pandas DataFrame containing information about NOAA weather stations.
        """

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
        """
        Retrieve weather data for a list of NOAA weather stations.

        Parameters:
        - dataset: The dataset ID for weather data (default is "global-summary-of-the-month").
        - stations: List of NOAA weather station IDs.

        Returns:
        A pandas DataFrame containing weather data for the specified stations.
        """

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
