import abc
import threading
from typing import Optional, List

from pydantic import BaseModel, Field

DEFAULT_CHATBOT_USER_ROLE = "User"
DEFAULT_CHATBOT_CHATBOT_ROLE = "AI"


class PromptTemplate:
    def __init__(self, content: str):
        self._content = content
        self._input_variables = self._parse_input_variables()

    def _parse_input_variables(self) -> List[str]:
        """Parse the input variables from the prompt content. i.e. all {} with inner variable name
        Notes:
            an empty {} should cause an error

        Returns:
            (List[str]) the input variables
        """
        self._input_variables = ["user_input"]
        return self._input_variables

    def format(self, **kwargs) -> str:
        """Format the prompt content with the given kwargs"""
        return self._content.format(**kwargs)

    def __str__(self) -> str:
        return self._content

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} content={self._content}>"


class Message(BaseModel):
    content: str
    additional_kwargs: dict = Field(default_factory=dict)


class ChatbotInterface(abc.ABC):
    """Chatbot Interface

    Chatbot 可以通过 `serve` 方法, 接收用户的消息, 并返回回复消息.
    """
    def __init__(self, user_role: Optional[str] = None, chatbot_role: Optional[str] = None, **kwargs):
        """
        :param user_role: (str) 用户角色的名称, 默认为 "User"
        :param chatbot_role: (str) chatbot 角色的名称, 默认为 "AI"
        """
        self.user_role = user_role if user_role is not None else DEFAULT_CHATBOT_USER_ROLE
        """用户角色的名称"""
        self.chatbot_role = chatbot_role if chatbot_role is not None else DEFAULT_CHATBOT_CHATBOT_ROLE
        """chatbot 角色的名称"""
        self._serve_lock = threading.Lock()
        """Chatbot 是否可用, 相当于是一个 mutex lock, 用于多线程环境下的 Chatbot"""

    def serve(self, timeout: float = -1., **kwargs) -> Message:
        """接收用户的消息, 并返回回复消息.

        :param timeout: (`int`) 超时时间, 单位为秒, -1 表示不超时
        :return: (`str`) 回复消息
        """
        # 尝试获取锁，如果设置了超时时间
        acquired = self._serve_lock.acquire(timeout=timeout)
        if not acquired:
            raise TimeoutError(f"Chatbot is not available after {timeout} seconds.")

        try:
            # 处理消息
            reply_message = self._serve(**kwargs)
            return reply_message
        finally:
            self._serve_lock.release()

    def serve_loop(self) -> None:
        """循环接收用户的消息, 并返回回复消息."""
        user_message_prefix = f"{self.user_role}: " if len(self.user_role) > 0 else ""
        chatbot_message_prefix = f"{self.chatbot_role}: " if len(self.chatbot_role) > 0 else ""
        while True:
            message_content = input(user_message_prefix)
            reply_message = self.serve(user_input=message_content)
            print(f"{chatbot_message_prefix}{reply_message}")

    # --------- abstract methods -----------
    @abc.abstractmethod
    def _serve(self, **kwargs) -> Message:
        """接收用户的消息, 并返回回复消息."""
        raise NotImplementedError()

    @abc.abstractmethod
    def reset(self) -> None:
        """重置聊天状态"""
        raise NotImplementedError()

    @property
    def chat_history(self) -> str:
        """对话的日志"""
        raise NotImplementedError(f"{self.__class__.__name__} does not implement `chat_history` property.")

    # --------- magic methods -----------
    def __str__(self):
        return f"{self.__class__.__name__}(name: {self.chatbot_role})"

    def __repr__(self):
        return self.__str__()
