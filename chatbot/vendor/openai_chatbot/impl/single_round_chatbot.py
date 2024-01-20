import abc

from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI

from ..interface import OpenAIChatbotInterface


class SingleRoundChatbot(OpenAIChatbotInterface, abc.ABC):
    @property
    @abc.abstractmethod
    def prompt_template(self) -> PromptTemplate:
        pass

    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        # check prompt template design, this is for code revise, not for production use
        super().__init__(model_name=model_name)
        self._chat_model = ChatOpenAI(model=model_name)
        """the underlying chat model"""

    def _serve(self, **kwargs) -> str:
        llm_kwargs = {}
        for input_variable in self.prompt_template.input_variables:
            value = kwargs.pop(input_variable, None)
            if value is None:
                raise ValueError(f"{input_variable} is not specified in kwargs, you must provide"
                                 f"it when chatting with {self.__class__.__name__}")
            llm_kwargs[input_variable] = value

        message = self.prompt_template.format(user_input=user_input, **llm_kwargs)
        response = self._chat_model.invoke(message, **kwargs)
        return response.content

    def chat_history_str(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} does not support conversation log.")

    def reset(self) -> None:
        """reset the chatbot

        `SingleRoundChatbot` has no state, so this method does nothing
        """
        pass


__all__ = [
    "SingleRoundChatbot",
]
