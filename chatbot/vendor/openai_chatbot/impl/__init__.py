"""
This module should contain some chatbot with specific functions, like:

- SystemMessageChatbot: A chatbot that can configure a system message.
- OneMessageChatbot: A chatbot that only reply user's message without any memory.
"""
from .single_round_chatbot import SingleRoundChatbot
from .system_message_chatbot import SystemMessageChatbot


__all__ = [
    "SingleRoundChatbot",
    "SystemMessageChatbot",
]

