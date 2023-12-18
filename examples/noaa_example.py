from social_signals.noaa.source import NOAASource
import os

source = NOAASource(os.environ.get("NOAA_TOKEN"))

# get all stations for given dataset (default is GSOM, takes about 4 minutes to extract about 120k stations)
stations = source.get_stations(dataset="GSOM")
print(stations)

# get given stations climate data (limited to 20 stations)
stations["id"] = stations["id"].str.replace("GHCND:", "")
stations_data = source.get_stations_data(stations=stations["id"].values[0:20])
