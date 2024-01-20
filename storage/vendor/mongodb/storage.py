from typing import Type

import pymongo
from pathlib import PurePosixPath, PureWindowsPath, WindowsPath
from pymongo.database import Database
from pymongo.collection import Collection

from storage.base.storage_interface import ConnectorBasedStorage
from storage.base.connector_interface import ConnectorChildClass
from .connector import MongoDBConnector, MongoDBPooledConnector, MongoDBConnectionPool


class MongoBasedStorage(ConnectorBasedStorage):
    """MongoDB-based Storage

    该类自动处理了与 MongoDB 之间的连接问题, 你可以专注地在 `MongoBasedStorage` 的子类中
    实现对 MongoDB 的读写操作, 而无需操心连接的细节。

    - `self.client`: `pymongo.MongoClient` 对象
    - `self.database`: `pymongo.database.Database` 对象

    如需配置要使用哪个 database 或者连接信息, 请在项目根目录下的 `.env` 处修改
    """
    collection_name = None

    # ------------------- 接口实现 -------------------
    def _get_connector_class(self) -> Type[ConnectorChildClass]:
        return MongoDBConnector

    # ------------------- attributes -------------------
    @property
    def collection(self) -> Collection:
        """底层 MongoDB collection 对象"""
        if self.collection_name is None:
            raise NotImplementedError(
                f"You must specify the collection name in the subclass: {self.__class__.__name__}")
        return self.database[self.collection_name]

    @property
    def client(self) -> pymongo.MongoClient:
        """底层 MongoDB client 对象"""
        return self._connector.client

    @property
    def database(self) -> Database:
        """底层 MongoDB database 对象"""
        return self._connector.database


class MongoPoolBasedStorage(ConnectorBasedStorage):
    collection_name = None

    def __init__(self, pool: MongoDBConnectionPool, **kwargs):
        """
        PoolBased Storage 必须要有一个 pool, 用来管理 MongoDB 的连接
        """
        super().__init__(pool=pool, **kwargs)

    # ------------------- 接口实现 -------------------
    def _get_connector_class(self) -> Type[MongoDBPooledConnector]:
        return MongoDBPooledConnector

    # ------------------- attributes -------------------
    @property
    def collection(self) -> Collection:
        """底层 MongoDB collection 对象"""
        if self.collection_name is None:
            raise NotImplementedError(f"You must specify the collection name in the subclass: {self.__class__.__name__}")
        return self.database[self.collection_name]

    @property
    def client(self) -> pymongo.MongoClient:
        """底层 MongoDB client 对象"""
        return self._connector.client

    @property
    def database(self) -> Database:
        """底层 MongoDB database 对象"""
        return self._connector.database


__all__ = [
    'MongoBasedStorage',
    'MongoPoolBasedStorage',
]
