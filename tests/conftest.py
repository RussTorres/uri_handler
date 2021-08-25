import os

import marshmallow
import pytest

import uri_handler.storage.custom_schemes

from file_testing import temp_file_base_uri

# test s3 if boto3 configured
try:
    from s3_testing import mock_s3_base_uri
    can_s3 = True
except ImportError as e:
    if e == "boto3":
        can_s3 = False
    else:
        raise


# determine which components to test_test based on environment
b = marshmallow.fields.Boolean()
test_s3 = b.deserialize(os.environ.get("UH_TEST_S3", True))
test_file = b.deserialize(os.environ.get("UH_TEST_FILE", True))


@pytest.fixture(scope="function")
def s3_uri_fixture():
    with mock_s3_base_uri(include_query=False) as uri:
        yield uri


@pytest.fixture(scope="function")
def s3_uri_fixture_with_query():
    with mock_s3_base_uri(bucketname="qtest", include_query=True,
                          access_string="qtesting", modify_env=False) as uri:
        yield uri


custom_schemes_testing = {
    "testcustoms3": {
        "base_scheme": "s3",
        "scheme_params": {
            "aws_access_key_id": "cstest",
            "aws_secret_access_key": "cstest"
        }
    },
}

uri_handler.storage.custom_schemes.custom_schemes = custom_schemes_testing


@pytest.fixture(scope="function")
def s3_uri_fixture_custom_scheme():
    custom_scheme = "testcustoms3"
    access_string = custom_schemes_testing["testcustoms3"][
        "scheme_params"]["aws_access_key_id"]
    with mock_s3_base_uri(bucketname="cstest", include_query=False,
                          access_string=access_string,
                          scheme=custom_scheme, modify_env=False,
                          return_params=False) as uri:
        yield uri


@pytest.fixture(scope="module")
def file_uri_fixture():
    with temp_file_base_uri() as uri:
        yield uri


# this is a workaround for parametrizing fixtures
uribase_fixtures_to_test = (
    ["file_uri_fixture" if test_file else []] +
    ["s3_uri_fixture",
     "s3_uri_fixture_with_query",
     "s3_uri_fixture_custom_scheme",
     ] if (can_s3 or test_s3) else [])
