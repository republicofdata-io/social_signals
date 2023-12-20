from social_signals.gdelt.source import GDELTSource

# Path to the service account key file
credentials_path = 'path/to/your/service-account-file.json'

# Initialize the GDELT source
source = GDELTSource(credentials_path=credentials_path)

# Perform a query to fetch the latest articles
gdelt_articles_df = source.get_gkg_articles(
    database_name = 'gdelt-bq', 
    dataset_name = 'gdeltv2', 
    articles_date = '20231109',
    primary_location_name_includes = 'united states',
    theme='protest',
    data_limit_gb = 1)

print(gdelt_articles_df)