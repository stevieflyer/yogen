import os
import abc
from typing import Optional

from stevools.util_classes import OpenAIModelManager

from chatbot.base import ChatbotInterface


DEFAULT_MODEL_NAME = "gpt-3.5-turbo-1106"


class OpenAIChatbotInterface(ChatbotInterface, OpenAIModelManager, abc.ABC):
    def __init__(
        self,
        model_name: Optional[str] = None,
        user_role: Optional[str] = None,
        chatbot_role: Optional[str] = None,
    ):
        """
        :param model_name: (str) 底层使用的 openai Chat LLM 的名称, 默认为 `"gpt-3.5-turbo-0613"`
        :param user_role: (str) 用户的角色名称, 默认为 `"User"`
        :param chatbot_role: (str) chatbot 的角色名称, 默认为 `"AI"`
        """
        model_name = model_name if model_name is not None else DEFAULT_MODEL_NAME
        super().__init__(user_role=user_role, chatbot_role=chatbot_role, model_name=model_name)
        self._check_environment_variables()

    @staticmethod
    def _check_environment_variables():
        """检查 environment variables: OPENAI_API_KEY"""
        if not os.environ.get('OPENAI_API_KEY'):
            raise RuntimeError('OPENAI_API_KEY is not set in environment variables. Please specify it first.')


__all__ = [
    "OpenAIChatbotInterface",
]
