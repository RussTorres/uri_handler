import contextlib
import shutil
import tempfile

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib


@contextlib.contextmanager
def temporarydir_23(*args, **kwargs):
    try:
        with tempfile.TemporaryDirectory(*args, **kwargs) as td:
            yield td
    except AttributeError:
        # python 2.7 version
        tdtf = tempfile.mkdtemp(*args, **kwargs)
        yield tdtf
        shutil.rmtree(tdtf)


@contextlib.contextmanager
def temp_file_base_uri():
    # tempdirs in pytest are weird....
    with temporarydir_23() as td:
        # TODO do we want any permission specifications?  # noqa: s1135
        # TODO this is a todo
        # TODO another one # noqa: python:S1135
        # TODO more # noqa
        # TODO yet another # noqa: S117
        yield pathlib.Path(td).as_uri()
