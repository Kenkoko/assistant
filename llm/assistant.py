
from langchain_ollama.chat_models import ChatOllama

from langchain_core.messages import SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.runnables import ConfigurableFieldSpec
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from pydantic import BaseModel
# from memory.in_memory import InMemoryHistory
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_tool_calling_agent
from dotenv import load_dotenv
from langchain_community.chat_message_histories import ChatMessageHistory
from llm.basic_tools import multiply, solve_quadratic_equation

load_dotenv()
class Assistant(BaseModel):

    def __init__(self):
        self._store: dict = {}
        self._chain: RunnableWithMessageHistory
        template_messages = [
            SystemMessage(content="You are a helpful assistant, Your name is Llama2"),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{text}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
        self._prompt_template = ChatPromptTemplate.from_messages(template_messages)

    def get_session_history(self, user_id: str, conversation_id: str) -> BaseChatMessageHistory:
        if (user_id, conversation_id) not in self._store:
            self._store[(user_id, conversation_id)] = ChatMessageHistory()
        return self._store[(user_id, conversation_id)]

    def init(self):

        def get_session_history(user_id: str, conversation_id: str) -> BaseChatMessageHistory:
            if (user_id, conversation_id) not in self._store:
                self._store[(user_id, conversation_id)] = ChatMessageHistory()
            return self._store[(user_id, conversation_id)]

        tools = [TavilySearchResults(max_results=1), multiply, solve_quadratic_equation]
        agent = create_tool_calling_agent(ChatOllama(model="llama3.2"), tools, self._prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools)
        self._chain = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="text",
            history_messages_key="history",
            history_factory_config=[
                ConfigurableFieldSpec(
                    id="user_id",
                    annotation=str,
                    name="User ID",
                    description="Unique identifier for the user.",
                    default="",
                    is_shared=True,
                ),
                ConfigurableFieldSpec(
                    id="conversation_id",
                    annotation=str,
                    name="Conversation ID",
                    description="Unique identifier for the conversation.",
                    default="",
                    is_shared=True,
                ),
            ],
        )

    def invoke(self, text: str, user_id: str = '123', conversation_id: str = "1"):
        answers = self._chain.invoke(
            {"text": text},
            config={"configurable": {"user_id": user_id, "conversation_id": conversation_id}}
        )['output']
        return answers

# assistant = Assistant()
# assistant.init()
# print("-----")
# print(assistant.invoke("Could you make two different plans to travel in Oslo and Moss for 14 days for two elders"))
# print("-----")
# print(assistant.invoke("Tell me more about second"))
# print("-----")
# print(assistant.invoke("What is the temperatur now in Moss"))
# print("-----")
# print(assistant.invoke("Summary what you have said so far"))
