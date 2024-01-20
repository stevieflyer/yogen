from typing import Type

import neo4j

from storage.vendor.neo4j.connector import NeoModelConnector
from storage.base.storage_interface import ConnectorBasedStorage
from storage.base.connector_interface import ConnectorChildClass


class Neo4jBasedStorage(ConnectorBasedStorage):
    """Neo4j-based Storage

    该类自动处理了与 Neo4j 之间的连接问题, 你可以专注地在 `Neo4jBasedStorage` 的子类中
    实现对 Neo4j 的读写操作, 而无需操心连接的细节。

    - `self.client`: `neo4j.Driver` 对象

    如需配置要使用哪个 database 或者连接信息, 请在项目根目录下的 `.env` 处修改
    """

    # ------------------- 接口实现 -------------------
    def _get_connector_class(self) -> Type[ConnectorChildClass]:
        return NeoModelConnector

    # ------------------- attributes -------------------
    @property
    def client(self) -> neo4j.Driver:
        """底层 neo4j client 对象"""
        return self._connector.client


__all__ = [
    'Neo4jBasedStorage',
]
