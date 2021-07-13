from uri_handler.errors import UriHandlerException
from uri_handler.utils._compat import urllib

from uri_handler.storage.filestorage import FileUriHandler
from uri_handler.storage.s3storage import S3UriHandler

import uri_handler.storage.custom_schemes


scheme_uri_handler_classes = {
    "s3": S3UriHandler,
    "file": FileUriHandler
    }


def get_uri_base_scheme(uri):
    p = urllib.parse.urlparse(uri)
    try:
        return uri_handler.storage.custom_schemes.custom_schemes[
            p.scheme]["base_scheme"]
    except KeyError:
        return p.scheme


def get_uri_handler(uri):
    try:
        handler_class = scheme_uri_handler_classes[get_uri_base_scheme(uri)]
    except KeyError as e:
        raise UriHandlerException(
            "Unknown uri schema {}".format(
                e))
    return handler_class()


__all__ = ["get_uri_handler", "S3UriHandler", "FileUriHandler"]
