import os
from os import PathLike
from typing import Optional, Union

import neo4j
from neomodel import config
from dotenv import load_dotenv
from neo4j import GraphDatabase

from storage.base.connector_interface import Connector


def init_neo4j_db():
    load_dotenv()
    db_url = os.getenv("NEO4J_CONNECTION_URL")
    # db_url = "bolt+s://neo4j:LuYyqLj8gAh9IiJE0IS1b9hSJ1eP1JBmGadCDa1jLrQ@d9d86e7b.databases.neo4j.io:7687"
    if db_url:
        config.DATABASE_URL = db_url
    else:
        raise ValueError("No NEO4J_CONNECTION_URL environment variable found.")


init_neo4j_db()


class Neo4jConnector(Connector):
    """Neo4j 数据库的连接器"""

    def __init__(self, dotenv_config_path: Optional[Union[str, PathLike[str]]] = None):
        # 调用父类方法
        super().__init__()
        # 加载环境变量
        load_dotenv(dotenv_path=dotenv_config_path)
        # 读取环境变量
        self._uri = os.getenv("NEO4J_CONNECTION_URL")
        # self._uri = "bolt+s://neo4j:LuYyqLj8gAh9IiJE0IS1b9hSJ1eP1JBmGadCDa1jLrQ@d9d86e7b.databases.neo4j.io:7687"
        self._client: Optional[neo4j.Driver] = None

    # 实现数据库的连接逻辑
    def _connect_impl(self) -> None:
        self._client = GraphDatabase.driver(self._uri)

    # 实现数据库的断开连接操作
    def _disconnect_impl(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    @property
    def client(self) -> neo4j.Driver:
        """内置的 neo4j.Driver 对象"""
        return self._client


class NeoModelConnector(Connector):
    """Neo4j 数据库的连接器"""

    def _connect_impl(self) -> None:
        pass

    def _disconnect_impl(self) -> None:
        pass


__all__ = [
    "Neo4jConnector",
    "NeoModelConnector",
]
