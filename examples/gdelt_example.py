from social_signals.gdelt.api import init_client
from google.cloud import bigquery

def fetch_latest_events(bigquery_client, dataset_name, table_name):
    # Define the query
    query = f"""
    SELECT * FROM `{dataset_name}.{table_name}`
    ORDER BY DATE DESC
    LIMIT 10
    """
    # Run the query on BigQuery
    query_job = bigquery_client.query(query)
    results = query_job.result()  # Wait for the query to finish

    # Process results
    for row in results:
        print(row)  # Placeholder for processing each row. You'd replace this with actual processing logic.

def main():
    # Path to the service account key file
    credentials_path = 'path/to/your/service-account-file.json'

    # Initialize the BigQuery client
    bigquery_client = init_client(credentials_path)

    # Perform a query to fetch the latest events
    dataset_name = 'your_dataset'  # Replace with your dataset name
    table_name = 'your_table'  # Replace with your table name
    fetch_latest_events(bigquery_client, dataset_name, table_name)

    print("Fetched latest events successfully.")

if __name__ == '__main__':
    main()
