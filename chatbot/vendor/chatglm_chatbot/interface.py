import abc

from engine.chatbot.base import ChatbotInterface


class ChatGLMChatbot(ChatbotInterface, abc.ABC):
    """Chatbot Interface based on ChatGLM"""
    pass


__all__ = [
    "ChatGLMChatbot",
]
