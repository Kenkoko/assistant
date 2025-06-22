import traceback
from litellm import completion
from llm.agents.basic_tools import getTouristEvents
from llm.agents.weather_agent import WeatherAgent
import json

from llm.memory.in_memory import InMemoryHistory
from llm.memory.utils import BaseMessage

PROMPT = """
You are an AI asistant. You are given a question and a set of possible functions.
You always answer the question by yourself and in the language that user asked.
You only use the function(s) when necessary.
If you do not know the answer, respond honestly by stating that you don't know!
"""

class DispatchAgent:
  def __init__(self, prompt: str = None, agents: list = None):
    if prompt is None:
      prompt = PROMPT
    if agents is not None:
      self.available_functions = {}
      for agent in agents:
        agent_name = agent['name']
        description = agent['description']
        if description is None:
          description = f"Ask agent '{agent_name}' for help"

        self.available_functions = {
            agent_name: agent['agent'].invoke,
            'getTouristEvents': getTouristEvents
        }  # only one function in this example, but you can have multiple

        self.tools = [
          {
            "name": agent_name,
            "description": description,
            "parameters": {
                "request": {
                    "param_type": "string",
                    "description": f"the request you want to {agent_name} to execute",
                    "required": True
                }
            }
          },
          {
            "name": "nop",
            "description": """This function does nothing. 

Call this function if you notice that you have already called the same
tool multiple times or you have already called all the tools you need.
The message you return will be shown to the user as your response to their
request.""",
            "parameters": {
                "reason": {
                    "param_type": "string",
                    "required": True
                }
            }
          },
          {
            "name": "getTouristEvents",
            "description": "Get interesting tourist events or/and activities in a city on a specific day",
            "parameters": {
                "location": {
                    "param_type": "string",
                    "description": "The city or location. E.g: Moss",
                    "required": True
                },
                "day": {
                  "param_type": "string",
                  "description": "The day we want to know which events are happening in the location, the format should be DD/MM/YYYY",
                  "required": True
                }
            }
          }
        ]
    self.memory = InMemoryHistory()
    self.memory.add_message(BaseMessage("system", prompt))
  
  def invoke(self, request):
    messages_for_llm = self.memory.get_messages_in_dict()
    reasonPrompt = """
This is the current question:
{question}
you have to FOCUS on it, let's THINK step by step!
  """.format(question=request)

    messages_for_llm.append({
      "role": "user",
      "content": reasonPrompt,
    })
    response = completion(
        model="ollama/qwen3", 
        messages=messages_for_llm,
        tools=self.tools,
        api_base="http://localhost:11434"
    )

    tool_calls = response.choices[0].message.tool_calls
    if tool_calls:
      for tool_call in tool_calls:
        function_name = tool_call.function.name
        if function_name not in self.available_functions:
          messages_for_llm.append(
            {
                "role": "tool",
                "content": f'There is no function named {function_name}',
            }
          )  # extend conversation with function response
          continue
        function_to_call = self.available_functions[function_name]
        function_args = json.loads(tool_call.function.arguments)
        print(function_args)
        function_response = function_to_call(
            **function_args
        )
        print(function_response)
        messages_for_llm.append(
          {
              "role": "tool",
              "content": f'Information: \n {function_response}',
          }
        )  # extend conversation with function response
      response = completion(
          model="ollama/qwen3", 
          messages=messages_for_llm,
          api_base="http://localhost:11434"
      )
    answer = response.json()['choices'][-1]['message']['content']

    self.memory.add_user_message(request)
    self.memory.add_ai_message(answer)

    return answer


questions = [
    'what is a dog',
    'Give me a tour plan on 12 June 2025 in Moss for 2 people',
    "give me detail report about the weather in Moss",
    "How is the weather now in Lysaker",
    'what is the phonetic representation of the "hello" word',
    'How is the weather now in Mars',
    'Classify the text into neutral, negative or positive.\nText: I think the vacation is okay.\nSentiment:',
    'what did I ask you so far?'
]
weather_agent = WeatherAgent()
agent = DispatchAgent(None, [{
  'name': 'weather_agent',
  'description': "Ask agent 'weather_agent' for weather information.",
  'agent': weather_agent
}])

for question in questions:
  for x in range(6):
    try:
      answer = agent.invoke(question)
      print(f"Question: {question}")
      print(f"Answer: {answer}")

      print("============================================")
      break
    except Exception as e: 
      exception_trace_str = traceback.format_exc()
      print("Exception stack trace as string:\n", exception_trace_str)
      print("Retrying............")