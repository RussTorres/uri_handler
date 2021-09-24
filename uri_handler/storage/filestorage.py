"""
filesystem-based uri utilities
"""
import errno
import os

import atomicwrites

from uri_handler.storage.basestorage import BaseUriHandler
from uri_handler.utils._compat import (
    urllib,
    pathlib)

import uri_handler.storage.custom_schemes

_file_create_modes = {
    "w", "a", "x",
    "w+", "a+", "x+",
    "w+b", "a+b", "x+b",
    "w+t", "a+t", "x+t",
    "wb", "ab", "xb",
    "wt", "at", "xt"}


def file_readbytes(fn):
    with open(fn, 'rb') as f:
        b = f.read()
    return b


def makedirs_safe(d):
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def atomic_file_writebytes(b, fn, overwrite=False):
    with atomicwrites.AtomicWriter(
            fn, mode='wb', overwrite=overwrite).open() as f:
        f.write(b)


def nonatomic_file_writebytes(b, fn, overwrite=False):
    m = 'wb' if overwrite else 'xb'

    with open(fn, m) as f:
        f.write(b)


def file_writebytes(b, fn, atomic=False, make_outdir=True, overwrite=True):
    if make_outdir:
        makedirs_safe(os.path.dirname(fn))

    if atomic:
        return atomic_file_writebytes(b, fn, overwrite=overwrite)
    else:
        return nonatomic_file_writebytes(b, fn, overwrite=overwrite)


def get_available_space_percentage(d):
    s = os.statvfs(d)
    return float(s.f_bavail) / float(s.f_blocks)


def get_used_space_percentage(d):
    return 1. - get_available_space_percentage(d)


def get_available_space_bytes(d):
    s = os.statvfs(d)
    return s.f_bavail * s.f_frsize


def uri_to_filename(uri):
    return urllib.parse.unquote(urllib.parse.urlparse(str(uri)).path)


def get_local_file_uri(uri):
    """get local file uri from custom scheme or query params"""
    p = urllib.parse.urlparse(uri)

    customschemeparams = uri_handler.storage.custom_schemes.custom_schemes.get(
        p.scheme, {}).get("scheme_params", {})

    scheme_path = customschemeparams.get("path_prefix", "/")

    new_path = os.path.join(scheme_path, p.path.lstrip("/"))

    file_uri = urllib.parse.urlunparse(
        urllib.parse.ParseResult(
            "file",
            "",
            new_path,
            "",
            "",
            "",
        ))
    return file_uri


def conform_uri_to_scheme(uri, target_scheme_like=None, target_scheme=None):
    """conform file uri to a custom scheme"""
    if target_scheme_like is None:
        if target_scheme is None:
            return uri
    else:
        target_scheme = urllib.parse.urlparse(target_scheme_like).scheme

    local_prefix = uri_handler.storage.custom_schemes.custom_schemes.get(
        target_scheme, {}).get("scheme_params", {}).get("path_prefix", "")
    local_path = urllib.parse.urlparse(uri).path

    new_path = (local_path[len(local_prefix):]
                if local_path.startswith(local_prefix)
                else local_path)
    new_uri = urllib.parse.urlunparse(urllib.parse.ParseResult(
        target_scheme,
        "",
        "/" + new_path.lstrip("/"),
        "",
        "",
        ""
    ))
    return new_uri


def filename_to_uri(fn):
    return pathlib.Path(fn).as_uri()


def listfiles_from_dir(d, full=True):
    if not full:
        raise NotImplementedError("relative path returns not implemented")
    for i in os.listdir(d):
        ifull = os.path.join(d, i)
        if os.path.isdir(i):
            # yield from listfiles_from_dir(ifull)
            for it in listfiles_from_dir(ifull):
                yield it
        else:
            yield ifull


def _canonical_file_listuris_from_prefix(uri):
    d = uri_to_filename(uri)
    fpaths = listfiles_from_dir(d, full=True)
    for fpath in fpaths:
        yield filename_to_uri(fpath)


def file_listuris_from_prefix(uri):
    local_prefix = get_local_file_uri(uri)
    for fpath in _canonical_file_listuris_from_prefix(local_prefix):
        yield conform_uri_to_scheme(fpath, uri)


def get_deep_directory_exists(d):
    if os.path.isdir(d):
        return d
    else:
        newd = os.dirname(d)
        # special values '/' and ''
        if newd == d:
            return newd
        else:
            return get_deep_directory_exists(newd)


def _canonical_file_validate_prefix(uri, check_writable=True, **kwargs):
    d = uri_to_filename(uri)

    # get deepest existing directory
    d_exist = get_deep_directory_exists(d)
    if check_writable:
        if not os.access(d_exist, os.W_OK | os.X_OK):
            return False
    return True


def file_validate_prefix(uri, *args, **kwargs):
    local_uri = get_local_file_uri(uri)
    return _canonical_file_validate_prefix(local_uri)


def file_uri_writebytes(b, uri, *args, **kwargs):
    local_uri = get_local_file_uri(uri)
    return file_writebytes(
        b, uri_to_filename(local_uri),
        *args, **kwargs)


def file_uri_readbytes(uri):
    local_uri = get_local_file_uri(uri)
    return file_readbytes(uri_to_filename(local_uri))


class FileUriHandler(BaseUriHandler):
    atomic = True
    make_outdir = True
    overwrite = True

    def save_bytes(self, b, uri):
        return file_uri_writebytes(
            b, uri,
            self.atomic, self.make_outdir, self.overwrite)

    def write_bytes(self, uri, b):
        return self.save_bytes(b, uri)

    def read_bytes(self, uri):
        return file_uri_readbytes(uri)

    def list_uris_prefix(self, uri_prefix):
        return file_listuris_from_prefix(uri_prefix)

    def validate_prefix(self, uri_prefix, **kwargs):
        return file_validate_prefix(uri_prefix)

    # FIXME currently python 3 specific kw-only arg
    def _smart_open_uri(self, uri, *args, parents=None, **kwargs):
        local_file_uri = get_local_file_uri(uri)
        parents = parents or self.make_outdir
        try:
            mode = args[0]
        except IndexError:
            mode = kwargs.get("mode")
        if parents and (mode in _file_create_modes):
            makedirs_safe(os.path.dirname(uri_to_filename(local_file_uri)))

        return super()._smart_open_uri(local_file_uri, *args, **kwargs)
