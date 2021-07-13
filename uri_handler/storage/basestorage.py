import contextlib

try:
    import smart_open
    HAS_SMARTOPEN = True
except ImportError:
    HAS_SMARTOPEN = False


class BaseUriHandler:
    def save_bytes(self, b, uri):
        raise NotImplementedError

    def write_bytes(self, uri, b):
        raise NotImplementedError

    def read_bytes(self, uri):
        raise NotImplementedError

    def list_uris_prefix(self, uri_prefix):
        raise NotImplementedError

    def validate_prefix(self, uri_prefix, **kwargs):
        raise NotImplementedError

    def _smart_open_uri(self, uri, *args, **kwargs):
        return smart_open.open(uri, *args, **kwargs)

    @contextlib.contextmanager
    def smart_open_uri(self, uri, *args, **kwargs):
        if not HAS_SMARTOPEN:
            raise Exception("smart_open not available!")
        with self._smart_open_uri(uri, *args, **kwargs) as f:
            yield f
