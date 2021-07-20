import os
import pytest

import marshmallow.fields

import uri_handler.uri_functions
import uri_handler.storage.custom_schemes

from conftest import uribase_fixtures_to_test

# test smart_open if installed or explicitly asked for
TEST_SMART_OPEN = os.getenv("UH_TEST_SMART_OPEN")
if TEST_SMART_OPEN is None:
    try:
        import smart_open  # noqa: F401
        TEST_SMART_OPEN = True
    except ImportError:
        TEST_SMART_OPEN = False
TEST_SMART_OPEN = marshmallow.fields.Bool().deserialize(TEST_SMART_OPEN)


def test_tests():
    """dummy test"""


def test_uri_functions_decorator():
    pass


@pytest.mark.parametrize(
    "uri_base_fixture", uribase_fixtures_to_test)
def test_readwrite_uri(uri_base_fixture, request):
    uri = request.getfixturevalue(uri_base_fixture)

    test_str = "test"
    test_b = test_str.encode("UTF-8")

    test_uri = uri_handler.uri_functions.uri_join(
        uri, "test_data")

    uri_handler.uri_functions.uri_writebytes(
        test_uri, test_b)

    r = uri_handler.uri_functions.uri_readbytes(
        test_uri)

    assert r == test_b
    assert r.decode("UTF-8") == test_str


@pytest.mark.skipif(not TEST_SMART_OPEN, reason=(
    "smart_open is not installed or explicitly not being tested"))
@pytest.mark.parametrize(
    "uri_base_fixture", uribase_fixtures_to_test)
def test_smartopen_uri(uri_base_fixture, request):
    uri = request.getfixturevalue(uri_base_fixture)

    test_str = "test_so"
    test_b = test_str.encode("UTF-8")

    test_uri = uri_handler.uri_functions.uri_join(
        uri, "test_so_data")

    with uri_handler.uri_functions.uri_smart_open(test_uri, "wb") as sof:
        sof.write(test_b)

    with uri_handler.uri_functions.uri_smart_open(test_uri, "rb") as sof:
        r = sof.read()

    assert r == test_b
    assert r.decode("UTF-8") == test_str
