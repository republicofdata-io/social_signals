from social_signals.x.source import XSource
import os
from datetime import datetime, timedelta

# Create an instance of the XSource class
x_bearer_token = os.environ.get("X_BEARER_TOKEN")
source = XSource(x_bearer_token=x_bearer_token)

# Specify the search term
search_term = "#protest -is:retweet -is:reply lang:en"

# Calculate yesterday's date at midnight
yesterday = datetime.now() - timedelta(days=1)
start_time = yesterday.strftime('%Y-%m-%dT00:00:00Z')

# Get recent tweets based on the search term, limiting to 10 results
search_results = source.search(search_term, n_results=10, start_time=start_time)

# Convert the DataFrame to JSON and print it
print("Search results:")
print(search_results.to_json(orient="records", lines=True, indent=4))