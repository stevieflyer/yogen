import abc
from typing import Type

from .connector_interface import ConnectorChildClass, ConnectionPool


class ConnectorBasedStorage(abc.ABC):
    """`ConnectorBasedStorage`(接口类) 是一个基于 `Connector` 的存储器

    你只需要 override: `_get_connector_class` 方法, 并且返回一个 `Connector` 的子类
    就可以实现一个 `ConnectorBasedStorage` 的子类，从而专心在内部实现对数据库的读写操作,
    而无需操心连接的细节。

    我们永远倡议使用 `with` 语句来使用 `ConnectorBasedStorage` 对象，例如:
    ```python
    with ConnectorBasedStorage() as storage:
        storage.write_or_read_something()
    ```
    """
    def __init__(self, **kwargs):
        connector_class = self._get_connector_class()
        self._connector = connector_class(**kwargs)

    # --------- attributes ---------
    @property
    def connector(self) -> ConnectorChildClass:
        """底层数据库连接器对象"""
        return self._connector

    @property
    def is_connected(self) -> bool:
        """是否已经连接到数据库"""
        return self._connector.is_connected

    def __enter__(self):
        self._connector.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connector.__exit__(exc_type, exc_val, exc_tb)
        return False

    # --------- abstract methods ---------
    @abc.abstractmethod
    def _get_connector_class(self) -> Type[ConnectorChildClass]:
        raise NotImplementedError


class PooledConnectorBasedStorage(abc.ABC):
    def __init__(self, pool: ConnectionPool):
        self._pool = pool
        self._connector = None

    def __enter__(self):
        self._connector.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connector.__exit__(exc_type, exc_val, exc_tb)
        return False


__all__ = [
    "ConnectorBasedStorage",
    "PooledConnectorBasedStorage",
]
