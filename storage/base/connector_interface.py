import abc
from typing import TypeVar

from ..utils import Pool


class Connector(abc.ABC):
    """(接口类) `Connector` 可以管理与数据库的连接

    该接口具有以下特性:
    1. `Connector` 支持 `with` 语句来管理连接的生命周期

    e.g.
    ```python
    with Connector() as connector:
        # do something
    ```

    2. `Connector` 支持 read-only property: `is_connected` 来判断是否已经连接到数据库
    """

    def __init__(self, **kwargs):
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        """Whether the database is connected"""
        return self._is_connected

    def _connect(self) -> None:
        """Connects to the database."""
        if not self.is_connected:
            try:
                self._connect_impl()
                self._is_connected = True
            except Exception as e:
                raise ConnectionError(
                    f"An error occurred while connecting to database by {self.__class__.__name__}: {e}")

    def _disconnect(self) -> None:
        """Disconnects from the database."""
        if self.is_connected:
            try:
                self._disconnect_impl()
                self._is_connected = False
            except Exception as e:
                raise ConnectionError(
                    f"An error occurred while disconnecting from database by {self.__class__.__name__}: {e}")

    def __enter__(self):
        """Connects to the MongoDB database."""
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Disconnects from the MongoDB database."""
        self._disconnect()
        return False

    # --------- abstract methods ---------
    @abc.abstractmethod
    def _connect_impl(self) -> None:
        """本方法应当实现数据库的连接逻辑, 初始化类似于 `self._client` 等内置对象"""
        raise NotImplementedError

    @abc.abstractmethod
    def _disconnect_impl(self) -> None:
        """本方法应当实现数据库的断开连接操作, 并且将相关的数据库对象设置为 None"""
        raise NotImplementedError


ConnectorChildClass = TypeVar("ConnectorChildClass", bound=Connector)


class ConnectionPool(Pool[ConnectorChildClass], abc.ABC):
    """数据库连接池"""

    def _destroy(self, item: ConnectorChildClass, **kwargs):
        item.__exit__(None, None, None)

    # --------- abstract methods ---------
    @abc.abstractmethod
    def _instantiate(self, **kwargs) -> ConnectorChildClass:
        """创建一个新的连接器并且连接

        任何子类其实只需要:
        ```python
        return ConnectorChildClass(**kwargs).__enter__()
        ```
        即可。
        """
        raise NotImplementedError


__all__ = [
    "Connector",
    "ConnectionPool",
    "ConnectorChildClass",
]
