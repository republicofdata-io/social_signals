from google.cloud import bigquery
from google.oauth2 import service_account
import logging

# Configure the logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the BigQuery client
def init_client(credentials_path):
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
    )
    client = bigquery.Client(credentials=credentials)
    return client

def run_query(client, query, data_limit_gb=1):
    # Convert gigabytes to bytes for the dry run limit comparison
    data_limit_bytes = data_limit_gb * 2**30  # 1 GB in bytes

    # Create a JobConfig object and set the dry_run flag to True
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    # API request - starts the query, but doesn't run it because of the dry_run flag set to True
    query_job = client.query(query, job_config=job_config)

    # Check how much data the query will process
    estimated_data_bytes = query_job.total_bytes_processed
    estimated_data_gb = estimated_data_bytes / 2**30

    # Log the estimated data usage
    logging.info(f"Estimated data usage for query: {estimated_data_gb:.3f} GB.")

    # Check how much data the query will process
    if estimated_data_bytes > data_limit_bytes:
        raise ValueError(f"Query will process {estimated_data_gb:.3f} GB, which exceeds the limit of {data_limit_gb} GB")

    # If the data processed is under the limit, run the query for real
    job_config.dry_run = False
    query_job = client.query(query, job_config=job_config)

    # Wait for the query to finish
    articles_df = query_job.result().to_dataframe()

    return articles_df