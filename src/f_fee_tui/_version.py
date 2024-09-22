__all__ = [
    "get_version",
]


def get_version():

    from importlib.metadata import version, PackageNotFoundError

    try:
        version = version("f_fee_tui")
    except PackageNotFoundError as exc:
        version = None

    return version
