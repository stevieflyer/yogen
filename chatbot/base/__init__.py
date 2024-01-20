"""`engine.chatbot.base`

`base` module includes definitions of base classes, i.e. the interface classes.
Specifically, this module includes the following classes:

- `Chatbot`: The base class for all chatbots.
"""
from .chatbot import ChatbotInterface, PromptTemplate, Message
