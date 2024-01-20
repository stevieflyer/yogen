import abc
import threading
from typing import List, TypeVar, Generic

T = TypeVar('T')


class Pool(abc.ABC, Generic[T]):
    """池, 例如: 连接池或对象池"""

    def __init__(self, init_pool_size: int, max_pool_size: int):
        """
        :param init_pool_size: (int) 池的初始对象数
        :param max_pool_size: (int) 池的最大对象数
        """
        self._init_pool_size = init_pool_size
        """池的初始对象数"""
        self._max_pool_size = max_pool_size
        """池的最大对象数"""
        self._avail_list: List[T] = []
        """池底层的空闲对象列表"""
        self._busy_list: List[T] = []
        """池底层的繁忙对象列表"""

        self._lock = threading.Lock()
        """多线程池的锁"""
        self._populate_initial_pool()

    @property
    def n_available(self) -> int:
        """池的空闲对象数"""
        return len(self._avail_list)

    @property
    def n_busy(self) -> int:
        """池的繁忙对象数"""""
        return len(self._busy_list)

    @property
    def n_total(self) -> int:
        """池的总对象数"""
        return self.n_available + self.n_busy

    def get(self, **kwargs) -> T:
        """从池中获取一个对象"""
        with self._lock:
            if not self._avail_list and len(self._busy_list) < self._max_pool_size:
                item = self._instantiate(**kwargs)
                self._busy_list.append(item)
                return item

            if self._avail_list:
                item = self._avail_list.pop()
                self._busy_list.append(item)
                return item

    def release(self, item: T):
        """释放池中的东西"""
        with self._lock:
            self._busy_list.remove(item)
            self._avail_list.append(item)

    def destroy(self, item: T, **kwargs):
        """摧毁池中的东西

        例如, 当处理数据库连接池时, destroy 可能意味着关闭连接。
        """
        with self._lock:
            if item in self._avail_list:
                self._avail_list.remove(item)
            if item in self._busy_list:
                self._busy_list.remove(item)
            self._destroy(item, **kwargs)

    def destroy_all(self):
        """摧毁池中的所有东西"""
        with self._lock:
            for item in self._avail_list:
                self._destroy(item)
            for item in self._busy_list:
                self._destroy(item)
            self._avail_list.clear()
            self._busy_list.clear()

    def _populate_initial_pool(self):
        for _ in range(self._init_pool_size):
            item = self._instantiate()
            self._avail_list.append(item)

    @abc.abstractmethod
    def _instantiate(self, **kwargs) -> T:
        """实例化一个新的连接对象"""
        raise NotImplementedError

    @abc.abstractmethod
    def _destroy(self, item: T, **kwargs):
        """
        销毁一个连接池内的对象。

        例如, 当处理数据库连接池时, destroy 可能意味着关闭连接。
        """
        raise NotImplementedError


__all__ = [
    "Pool",
]
