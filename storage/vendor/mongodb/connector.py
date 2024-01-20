import traceback
from os import PathLike, getenv
from typing import Optional, Union

import pymongo
from dotenv import load_dotenv
from pymongo.database import Database

from storage.base.connector_interface import Connector, ConnectionPool


class MongoDBConnector(Connector):
    """Basic MongoDB Connector

    该类会从环境变量中读取 MongoDB 的连接信息, 并在初始化时连接到 MongoDB 数据库的特定 database.

    通过以下代码, 你可以轻松地获得一个 pymongo.MongoClient 对象:

    ```python

    from db.vendor.mongodb import MongoDBConnector

    with MongoDBConnector() as connector:
        client = connector.client
        # do something with client
    ```
    """
    def __init__(self, dotenv_config_path: Optional[Union[str, PathLike[str]]] = None) -> None:
        """Initializes the MongoDB connection using environment variables.

        :param dotenv_config_path: Path to the `.env` file. If `None`, defaults to the root `.env` file.
        """
        # 1. 先调用父类的构造函数
        super().__init__()

        # 2. 其余初始化逻辑
        load_dotenv(dotenv_path=dotenv_config_path)
        self._connection_url = str(getenv('MONGODB_CONNECTION_URL')).strip()
        # self._connection_url = "mongodb+srv://root:14PJj5sqi5UdV10j@cluster0.g5v8xg6.mongodb.net/?retryWrites=true&w=majority"
        self._database_name = str(getenv('MONGODB_DATABASE')).strip()
        self._client: Optional[pymongo.MongoClient] = None
        self._database: Optional[Database] = None

    # --------- attributes -----------
    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def connection_url(self) -> str:
        return self._connection_url

    @property
    def client(self) -> pymongo.MongoClient:
        """MongoDB client"""
        return self._client

    @property
    def database(self) -> Database:
        """MongoDB database"""
        return self._database

    # --------- 接口的实现 ---------
    def _connect_impl(self) -> None:
        """Connect to the MongoDB database."""
        try:
            self._client = pymongo.MongoClient(self.connection_url)
            self._database = self._client[self.database_name]
        except Exception as e:
            print(f"Failed to connect to MongoDB database: {self.database_name}, MongoDB uri: {self.connection_url}, error: {e}")
            traceback.print_exc()
            raise e

    def _disconnect_impl(self) -> None:
        """Disconnects from the MongoDB database."""
        self._client.close()
        self._database = None


class MongoDBConnectionPool(ConnectionPool[MongoDBConnector]):
    """MongoDB Connection Pool"""

    def _instantiate(self, **kwargs) -> MongoDBConnector:
        return MongoDBConnector(**kwargs).__enter__()


class MongoDBPooledConnector(Connector):
    """MongoDB Pooled Connector

    This class reads MongoDB connection information from environment variables,
    and connects to a specific MongoDB database using a connection pool.

    Example to get a pymongo.MongoClient object:

    ```python
    from db.vendor.mongodb import MongoDBPooledConnector

    with MongoDBPooledConnector() as connector:
        client = connector.client
        # do something with client
    ```
    """
    def __init__(self, pool: MongoDBConnectionPool, dotenv_config_path: Optional[Union[str, PathLike[str]]] = None) -> None:
        """Initializes the MongoDB connection using a connection pool.

        :param dotenv_config_path: Path to the `.env` file. If `None`, defaults to the root `.env` file.
        :param pool: The MongoDB connection pool to use.
        """
        super().__init__()
        load_dotenv(dotenv_path=dotenv_config_path)
        self._pool = pool
        self._database_name = getenv('MONGODB_DATABASE')
        self._client: Optional[pymongo.MongoClient] = None
        self._database: Optional[Database] = None

    @property
    def database_name(self) -> str:
        return self._database_name

    @property
    def client(self) -> pymongo.MongoClient:
        if self._client is None:
            raise ValueError("Database connection is not established.")
        return self._client

    @property
    def database(self) -> Database:
        if self._database is None:
            raise ValueError("Database connection is not established.")
        return self._database

    def _connect_impl(self) -> None:
        """Get an alive connection to the database using the connection pool."""
        self._connector = self._pool.get()
        self._client = self._connector.client
        self._database = self._client[self.database_name]

    def _disconnect_impl(self) -> None:
        """Releases the MongoDB database connection back to the pool."""
        if self._connector:
            self._pool.release(self._connector)
            self._connector, self._client, self._database = None, None, None


__all__ = [
    'MongoDBConnectionPool',
    'MongoDBConnector',
    'MongoDBPooledConnector',
]
