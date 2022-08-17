"""Client for Gever of the canton of Zurich"""

__version__ = "0.0.5"
__all__ = ["client", "errors", "response"]

from .errors import GoiferError, NoMoreRecordsError  # noqa
from .errors import GoiferWarning  # noqa
from .client import Client  # noqa


def indexes(instance, **kwargs):
    client_kwargs = kwargs
    client_kwargs["instance"] = instance

    c = Client(**client_kwargs)
    return c.indexes()


def search(instance, index, query, **kwargs):
    search_params = ["index", "query", "start_record"]
    search_kwargs = {k: v for k, v in kwargs.items() if k in search_params}
    search_kwargs["index"] = index
    search_kwargs["query"] = query

    # assume all others kwargs are for the client
    client_kwargs = {k: v for k, v in kwargs.items() if k not in search_params}
    client_kwargs["instance"] = instance

    c = Client(**client_kwargs)
    return c.search(**search_kwargs)


def file(instance, index, file_id, version, view, **kwargs):
    client_kwargs = kwargs
    client_kwargs["instance"] = instance

    c = Client(**client_kwargs)
    return c.file(index, file_id, version, view)


def schema(instance, index, **kwargs):
    # assume all others kwargs are for the client
    client_kwargs = kwargs
    client_kwargs["instance"] = instance

    c = Client(**client_kwargs)
    return c.schema(index)
