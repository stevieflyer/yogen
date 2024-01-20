import warnings
from typing import Optional, List, Dict, Any

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory

from ..interface import OpenAIChatbotInterface


DEFAULT_SYSTEM_TEMPLATE_STR = """
Assistant is a large language model trained by OpenAI.
Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.
""".strip()

DEFAULT_SYSTEM_INPUT_VARIABLES = []

BASE_TEMPLATE_STR = """
{history}

Now you should reply to the following message:

{user_role}: {human_input}

{chatbot_role}:""".strip()

BASE_INPUT_VARIABLES = ["history", "human_input", "chatbot_role", "user_role"]

DEFAULT_MEMORY_WINDOW = 512


class SystemMessageChatbot(OpenAIChatbotInterface):
    """
    A Naive OpenAI Chatbot with customized System Prompt

    You can simply create a customized chatbot by:

    ```python
    from engine.models.base_chatbot import SystemMessageChatbot

    linux_terminal_pretender = SystemMessageChatbot(
        user_role="Desktop User",
        chatbot_role="Linux Terminal",
        sys_template_str="Please pretend to be the command line terminal for linux.",

    linux_terminal_pretender.serve("pwd")  # output: "/home/user/"
    ```
    """
    def __init__(
        self,
        user_role: Optional[str] = None,
        chatbot_role: Optional[str] = None,
        sys_template_str: Optional[str] = None,
        sys_input_vars: Optional[List[str]] = None,
        memory_window: Optional[int] = None,
        model_name: Optional[str] = None,
    ):
        """
        :param user_role: (str) 用户角色的名称, 默认为 `"User"`
        :param chatbot_role: (str) chatbot 角色的名称, 默认为 `"AI"`
        :param sys_template_str: (str) 系统消息的模板字符串
        :param sys_input_vars: (List[str]) 系统消息的模板字符串中的变量
        :param memory_window: (int) 记忆窗口的大小(消息的条数), 默认为 `512`
        :param model_name: (str) 底层 OpenAI Chat LLM 模型的名称, 默认为 `"gpt-3.5-turbo-0613"`
        """
        super().__init__(model_name=model_name, user_role=user_role, chatbot_role=chatbot_role)
        self.memory_window = memory_window if memory_window is not None else DEFAULT_MEMORY_WINDOW
        self._sys_template_str = sys_template_str
        self._sys_input_vars = sys_input_vars
        self._chain = None
        self._init_engine_chain()

    def _serve(self, message_content: str, **input_kwargs) -> str:
        input_var_dict = {
            "human_input": message_content,
            **self._check_input_vars(**input_kwargs),
        }
        return self._chain.predict(**input_var_dict)

    def reset(self) -> None:
        """重置聊天状态"""
        self._init_engine_chain()

    @property
    def chat_history_str(self) -> str:
        """返回当前的对话记录"""
        messages: List[Dict] = self.chain.memory.dict()['chat_memory']['messages']
        non_system_messages = [m for m in messages if m['example'] is False]
        for i, message in enumerate(non_system_messages):
            if i % 2 == 0:
                non_system_messages[i]['role'] = self.user_role
            else:
                non_system_messages[i]['role'] = self.chatbot_role

        message_strs = [f"{message['role']}: {message['content']}" for message in non_system_messages]
        chat_history_str = "\n".join(message_strs)
        return chat_history_str

    def load_history(self, messages: List[Dict[str, str]]):
        """
        加载历史消息
        """
        # the first message is assumed to be user message
        for i in range(0, len(messages), 2):
            user_message = messages[i]
            chatbot_message = messages[i + 1]
            if user_message['role'] != self.user_role or chatbot_message['role'] != self.chatbot_role:
                raise ValueError(
                    f"Failed to load history, {i}th message: {user_message} or {chatbot_message} does not match user_role: {self.user_role} or chatbot_role: {self.chatbot_role}")
            self._chain.memory.save_context(
                {"human_input": user_message['content']},
                {"output": chatbot_message['content']}
            )

        if len(messages) % 2 == 1:
            warnings.warn(f"[load history] Odd number of messages: {len(messages)}, the last message will be ignored.")

    # ---------------- attributes ----------------
    @property
    def chain(self) -> LLMChain:
        """LLMChain: tutorgpt engine 内部使用的 chain"""
        return self._chain

    # ---------------- private methods ----------------
    def _check_input_vars(self, **input_kwargs) -> Dict[str, Any]:
        """检查输入的 kwargs 是否包含所有需要的变量, 返回 input_variables_dict

        :param input_kwargs: (Dict[str, Any]) 输入的 kwargs
        :return: (Dict[str, Any])
        """
        input_var_dict = {
            "user_role": self.user_role,
            "chatbot_role": self.chatbot_role,
        }
        for input_var in self._custom_input_vars:
            try:
                input_var_dict[input_var] = input_kwargs[input_var]
            except KeyError:
                raise KeyError(f"input_variable: {input_var} is not provided in kwargs: {input_kwargs}")

        return input_var_dict

    def _init_engine_chain(self):
        """初始化用来生成回复消息的 LLMChain"""
        self._prompt_template = self._init_prompt_template(self._sys_template_str, self._sys_input_vars)
        self._custom_input_vars = [v for v in self._prompt_template.input_variables if v not in BASE_INPUT_VARIABLES]

        memory = ConversationBufferWindowMemory(k=self.memory_window, input_key="human_input")
        memory.ai_prefix = self.chatbot_role
        memory.human_prefix = self.user_role
        chat_chain = LLMChain(
            verbose=False,
            prompt=self._prompt_template,
            llm=ChatOpenAI(model_name=self.model_name),
            memory=memory,
        )
        self._chain = chat_chain

    def _init_prompt_template(
            self, 
            system_template_str: Optional[str],
            system_input_variables: Optional[List[str]]
        ) -> PromptTemplate:
        """初始化 LLM Chain 使用的 PromptTemplate

        :param system_template_str: (str) 系统消息的模板字符串
        :param system_input_variables: (List[str]) 系统消息的模板字符串中的变量
        :return: (PromptTemplate) 系统消息的模板
        """
        if system_template_str is None:
            system_template_str = DEFAULT_SYSTEM_TEMPLATE_STR
            system_input_variables = DEFAULT_SYSTEM_INPUT_VARIABLES
        if system_input_variables is None:
            system_input_variables = []
        for input_variable in system_input_variables:
            if input_variable in BASE_INPUT_VARIABLES:
                raise ValueError(f"input_variable: {input_variable} conflicts with BASE_INPUT_VARIABLES: {BASE_INPUT_VARIABLES}, please use another name.")
        system_prompt_str = "\n\n".join([system_template_str + BASE_TEMPLATE_STR])
        system_input_variables = system_input_variables + BASE_INPUT_VARIABLES
        return PromptTemplate(input_variables=system_input_variables, template=system_prompt_str)


__all__ = [
    'SystemMessageChatbot',
]
