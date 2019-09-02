import contextlib
import tempfile

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


@contextlib.contextmanager
def temp_file_base_uri():
    # tempdirs in pytest are weird....
    with tempfile.TemporaryDirectory() as td:
        # TODO do we want any permission specifications?
        yield pathlib.Path(td).as_uri()
