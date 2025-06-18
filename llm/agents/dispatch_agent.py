from litellm import completion
from llm.agents.basic_tools import weatherTool
from llm.agents.weather_agent import WeatherAgent
import json

PROMPT = """
You are an AI asistant. You are given questions and a set of possible functions or/and agents.
You always answer the questions by yourself and in the language that user asked.
You only use the function(s)/agent(s) when necessary.
If you do not know the answer, respond honestly by stating that you don't know!
"""

class DispatchAgent:
  def __init__(self, prompt: str = None, agents: list = None):
    if prompt is None:
      prompt = PROMPT
    self.system_prompt = {
        "role": "system",
        "content": prompt
    }
    if agents is not None:
      self.available_functions = {}
      for agent in agents:
        agent_name = agent['name']
        description = agent['description']
        if description is None:
          description = f"Ask agent '{agent_name}' for help"

        self.available_functions = {
            agent_name: agent['agent'].invoke
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
          }
        ]
    self.memory = [self.system_prompt]
  
  def invoke(self, request):
    messages_for_llm = self.memory.copy()
    reasonPrompt = """
This is the current question or request from user, you have to focus on it:
{question}

let's THINK step by step!
  """.format(question=request)

    messages_for_llm.append({
      "role": "user",
      "content": reasonPrompt,
    })
    response = completion(
        model="ollama/llama3.2", 
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
              "content": function_response,
          }
        )  # extend conversation with function response
      response = completion(
          model="ollama/llama3.2", 
          messages=messages_for_llm,
          api_base="http://localhost:11434"
      )
    answer = response.json()['choices'][-1]['message']['content']

    self.memory.append({
      "role": "user",
      "content": request,
    })
    self.memory.append({
      "role": "assistant",
      "content": answer,
    })

    return answer


questions = [
    'who is a dog',
    'what is a dog',
    "give me detail report about the weather in Moss",
    "How is the weather now in Lysaker",
    'what is the phonetic representation of the "hello" word',
    'How is the weather now in Mars',
    'what did I ask you so far?'
]
weather_agent = WeatherAgent()
agent = DispatchAgent(None, [{
  'name': 'weather_agent',
  'description': "Ask agent 'weather_agent' for weather information.",
  'agent': weather_agent
}])

for question in questions:
  answer = agent.invoke(question)
  print(f"Question: {question}")
  print(f"Answer: {answer}")

  print("============================================")