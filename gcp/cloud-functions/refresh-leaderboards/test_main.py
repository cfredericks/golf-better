import main
import pytest

SECRET_PAYLOAD = b'secret-value'

@pytest.fixture
def mock_secret_manager(mocker):
    mock_client = mocker.patch('main.secretmanager.SecretManagerServiceClient')
    mock_instance = mock_client.return_value
    mock_response = mocker.Mock()
    mock_response.payload.data.decode.return_value = SECRET_PAYLOAD
    mock_instance.access_secret_version.return_value = mock_response
    return mock_instance

def test_get_gsm_secret_defaults(mock_secret_manager):
    secret_id = 'test-secret'
    secret = main.get_gsm_secret(secret_id)
    mock_secret_manager.access_secret_version.assert_called_once_with(name=f"projects/{main.DEFAULT_PROJECT_ID}/secrets/{secret_id}/versions/{main.DEFAULT_VERSION_ID}")
    assert secret == SECRET_PAYLOAD

def test_get_gsm_secret_overrides(mock_secret_manager):
    secret_id = 'test-secret'
    project_id = 'test-project-id'
    version_id = 'test-version-id'
    secret = main.get_gsm_secret(secret_id, project_id, version_id)
    mock_secret_manager.access_secret_version.assert_called_once_with(name=f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}")
    assert secret == SECRET_PAYLOAD

def test_refresh_leaderboards(mock_secret_manager, mocker):
    # TODO finish testing with asserts
    # Mock get_db_connection
    mock_db_connection = mocker.patch('main.get_db_connection')
    mock_pool = mock_db_connection.return_value
    mock_conn = mock_pool.connect.return_value.__enter__.return_value
    mock_execute = mock_conn.execute

    main.refresh_leaderboards(None)
