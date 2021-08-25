import json
import os


def _load_custom_schemes_file(scheme_fn=None):
    if scheme_fn is None:
        try:
            scheme_fn = os.environ["UH_CUSTOM_SCHEMES_FILE"]
        except KeyError:
            return {}
    with open(scheme_fn, "r") as f:
        custom_schemes = json.load(f)
    return custom_schemes


custom_schemes = _load_custom_schemes_file()

__all__ = ["custom_schemes"]
