from dataclasses import dataclass

@dataclass
class BaseMessage:
  role: str
  content: str

  def get(self, key, default=None):
    return getattr(self, key, default)
  
  def conver_to_dict(self) -> dict:
    return {
      "role": self.role,
      "content": self.content
    }

def get_buffer_string(
    messages: list[BaseMessage]
) -> str:
    r"""Convert a sequence of Messages to strings and concatenate them into one string.

    Args:
        messages: Messages to be converted to strings.

    Returns:
        A single string concatenation of all input messages.

    Raises:
        ValueError: If an unsupported message type is encountered.
    """
    string_messages = []
    for m in messages:
        role = m.role
        message = f"{role}: {m.text()}"
        string_messages.append(message)

    return "\n".join(string_messages)