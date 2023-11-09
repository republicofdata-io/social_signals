from social_signals.gdelt.api import init_client, get_gkg_articles
from google.cloud import bigquery

def main():
    # Path to the service account key file
    credentials_path = 'path/to/your/service-account-file.json'

    # Initialize the BigQuery client
    bigquery_client = init_client(credentials_path)

    # Perform a query to fetch the latest articles
    gdelt_articles_df = get_gkg_articles(
        bigquery_client, 
        database_name = 'gdelt-bq', 
        dataset_name = 'gdeltv2', 
        articles_date = '20231109',
        primary_location_country = 'united states',
        theme='protest',
        data_limit_gb = 1)

    print(gdelt_articles_df)

if __name__ == '__main__':
    main()
