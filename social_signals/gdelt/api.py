from datetime import datetime
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

def get_gkg_articles(client, 
                     database_name='gdelt-bq', 
                     dataset_name='gdeltv2', 
                     articles_date=datetime.today().strftime('%Y%m%d'),
                     primary_location_country='united states',
                     theme='protest',
                     data_limit_gb=1):
    # Convert gigabytes to bytes for the dry run limit comparison
    data_limit_bytes = data_limit_gb * 2**30  # 1 GB in bytes

    # Define query
    query = f"""
        with s_articles as (

            select
                GKGRECORDID as gdelt_gkg_article_id,
                Documentidentifier as article_url,
                SourceCollectionIdentifier as source_collection_id,
                lower(Themes) as themes,
                lower(Locations) as locations,
                lower(Persons) as persons,
                lower(Organizations) as organizations,
                SocialImageEmbeds as social_image_url,
                SocialVideoEmbeds as social_video_url,
                parse_timestamp('%Y%m%d%H%M%S', cast(`DATE` as string)) as creation_ts,
                _PARTITIONTIME as bq_partition_id
            
            from `{database_name}.{dataset_name}.gkg_partitioned`

            where _PARTITIONTIME = parse_timestamp('%Y%m%d%H%M%S', concat('{articles_date}', '000000'))

        ),

        filter_source_collections as (

            select * from s_articles
            where source_collection_id = 1

        ),

        primary_locations as (

            select
                gdelt_gkg_article_id,
                article_url,
                themes,
                locations,
                (
                    select split_location 
                    from unnest(split(locations, ';')) as split_location
                    order by 
                        case substr(split_location, 1, 1)
                        when '3' then 1
                        when '4' then 2
                        when '2' then 3
                        when '5' then 4
                        when '1' then 5
                        else 6
                        end 
                    limit 1
                ) as primary_location,
                persons,
                organizations,
                social_image_url,
                social_video_url,
                creation_ts,
                bq_partition_id

            from filter_source_collections

        ),

        filter_locations as (

            select * from primary_locations
            where primary_location like '%{primary_location_country}%'

        ),

        filter_themes as (

            select * from filter_locations
            where (
                select true 
                from unnest(split(themes, ';')) theme with offset
                where offset < 10
                and theme = '{theme}'
                limit 1
            ) is not null

        )

        select *
        from filter_themes
        order by gdelt_gkg_article_id
    """

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