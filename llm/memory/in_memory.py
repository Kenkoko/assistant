from pydantic import BaseModel, Field

from llm.memory.utils import BaseMessage, get_buffer_string


class InMemoryHistory(BaseModel):
  """In memory implementation of chat message history."""

  messages: list[BaseMessage] = Field(default_factory=list)

  def add_messages(self, messages: list[BaseMessage]) -> None:
    """Add a list of messages to the store"""
    self.messages.extend(messages)

  def add_message(self, message: BaseMessage) -> None:
    self.messages.append(message)

  def add_user_message(self, content: str) -> None:
    self.add_message(BaseMessage("user", content))

  def add_ai_message(self, content: str) -> None:
    self.add_message(BaseMessage("assistant", content))

  def add_tool_message(self, content: str) -> None:
    self.add_message(BaseMessage("tool", content))

  def get_messages(self) -> list[BaseMessage]:
    return self.messages
  
  def get_messages_in_dict(self) -> list[dict]:
    message_in_dict = []
    for message in self.messages:
      message_in_dict.append(message.conver_to_dict())
    return message_in_dict

  def clear(self) -> None:
    self.messages = []

  def __str__(self) -> str:
    """Return a string representation of the chat history."""
    return get_buffer_string(self.messages)