from social_signals.gdelt.source import GDELTSource

from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
import pytest
from unittest.mock import patch, Mock

# Mocking the service account credentials
@patch('google.oauth2.service_account.Credentials.from_service_account_file')
@patch('google.cloud.bigquery.Client')
def test_init_client(mock_bigquery_client, mock_service_account_credentials):
    # Set up the mock for the service account credentials
    mock_credentials = Mock(spec=service_account.Credentials)
    mock_service_account_credentials.return_value = mock_credentials
    
    # Set up the mock for the BigQuery Client
    mock_bigquery_instance = Mock(spec=bigquery.Client)
    mock_bigquery_client.return_value = mock_bigquery_instance
    
    # Call the init_client function with a dummy file path
    client = GDELTSource(credentials_path='dummy/credentials/path.json')
    
    # Assert that the mock was called with the dummy file path
    mock_service_account_credentials.assert_called_with('dummy/credentials/path.json')
    
    # Assert that the Client was called with the mock credentials
    mock_bigquery_client.assert_called_with(credentials=mock_credentials)
    
    # Assert the returned client is an instance of GDELTSource
    assert isinstance(client, GDELTSource)


@patch('google.cloud.bigquery.Client')
@patch('google.oauth2.service_account.Credentials.from_service_account_file', return_value=Mock())
def test_get_gkg_articles_under_limit(mock_credentials, mock_client):
    # Arrange
    database_name = 'gdelt_db'
    dataset_name = 'gdelt_dataset'
    data_limit_gb = 1  # 1 GB limit
    data_limit_bytes = data_limit_gb * 2**30

    # Create a mock query job for the dry run
    mock_dry_get_gkg_articles_job = Mock(spec=bigquery.QueryJob)
    mock_dry_get_gkg_articles_job.total_bytes_processed = data_limit_bytes - 1  # Mock bytes less than limit

    # Mock the client's query method to return our mock query job for the dry run
    mock_client().query.return_value = mock_dry_get_gkg_articles_job

    # Create an instance of GDELTSource
    gdelt_source = GDELTSource(credentials_path='mock_credentials_path')

    # Act & Assert
    try:
        result = gdelt_source.get_gkg_articles(database_name, dataset_name, data_limit_gb)
        assert result is not None  # Your function should return a DataFrame or similar
    except ValueError as e:
        pytest.fail(f"get_gkg_articles raised ValueError unexpectedly with message: {str(e)}")


@patch('google.cloud.bigquery.Client')
@patch('google.oauth2.service_account.Credentials.from_service_account_file', return_value=Mock())
def test_get_gkg_articles_over_limit(mock_credentials, mock_client):
    # Arrange
    database_name = 'gdelt_db'
    dataset_name = 'gdelt_dataset'
    data_limit_gb = 1  # 1 GB limit
    data_limit_bytes = data_limit_gb * 2**30

    # Create a mock query job for the dry run
    mock_dry_get_gkg_articles_job = Mock(spec=bigquery.QueryJob)
    mock_dry_get_gkg_articles_job.total_bytes_processed = data_limit_bytes + 1  # Mock bytes more than limit

    # Mock the client's query method to return our mock query job for the dry run
    mock_client().query.return_value = mock_dry_get_gkg_articles_job

    # Create an instance of GDELTSource
    gdelt_source = GDELTSource(credentials_path='mock_credentials_path')

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        gdelt_source.get_gkg_articles(database_name, dataset_name, data_limit_gb)
    assert f"exceeds the limit of {data_limit_gb}" in str(excinfo.value)