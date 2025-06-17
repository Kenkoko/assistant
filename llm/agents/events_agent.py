from litellm import completion, function_call_prompt
from llm.agents.basic_tools import weatherTool
import json



questions = [
    'Give me a tour plan on 12 June 2025 in Moss for 2 people',
    'How about on 13 June 2025',
    'How about on 13 June 2027',
    'Okie so create a plan to visit moss',
    'what is a dog',
    'what is the phonetic representation of the "hello" word',
    "give me weather of Moss",
    'what did I ask you so far?'
]


tools = [
  {
    "name": "weatherTool",
    "description": "Get the current weather in a given location",
    "parameters": {
        "location": {
            "param_type": "string",
            "description": "The city or location",
            "required": True
        }
    }
  },
  {
    "name": "getEvents",
    "description": "Get events in the location on a specific day",
    "parameters": {
        "location": {
            "param_type": "string",
            "description": "The city or location",
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

PROMPT = """
You are an AI asistant. You are given a question and a set of possible functions. 

You always answer the question by yourself and in the language that user asked. You only use the function(s) when necessary.

"""

system_prompt = {
    "role": "system",
    "content": PROMPT
}

def getEvents(location: str, day: str):
    with open('.\\llm\\agents\\events.json') as f:
        events = json.load(f)
        day_events = events.get(location, {})
        if day in day_events:
            return day_events[day]
        return f"There is no information about special event on {day} at {location}"




conversations = []
conversations.append(system_prompt)

for question in questions:
  internal_response = conversations
  reasonPrompt = """
This is the current question or request from user, you have to focus on it:
{question}

let's think step by step!
  """.format(question=question)

  internal_response.append({
    "role": "user",
    "content": reasonPrompt,
  })
  response = completion(
      model="ollama/llama3.2", 
      messages=internal_response,
      tools=tools,
      api_base="http://localhost:11434"
  )

  response_message = response.choices[0].message
  tool_calls = response_message.tool_calls

  if tool_calls:
    available_functions = {
        "weatherTool": weatherTool,
        "getEvents": getEvents
    }  # only one function in this example, but you can have multiple
    internal_response.append(response_message)
    for tool_call in tool_calls:
      function_name = tool_call.function.name
      if function_name not in available_functions:
        internal_response.append(
           {
               "role": "tool",
               "content": f'There is no function named {function_name}',
           }
         )  # extend conversation with function response
        continue

      function_to_call = available_functions[function_name]
      function_args = json.loads(tool_call.function.arguments)
      print(function_args)
      function_response = function_to_call(
          **function_args
      )
      internal_response.append(
        {
            "role": "tool",
            "content": function_response,
        }
      )  # extend conversation with function response
    response = completion(
        model="ollama/llama3.2", 
        messages=internal_response,
        api_base="http://localhost:11434"
    )
  answer = response.json()['choices'][-1]['message']['content']
  print(f"Question: {question}")
  print(f"Answer: {answer}")

  conversations.append({
    "role": "user",
    "content": question,
  })

  conversations.append({
    "role": "assistant",
    "content": answer,
  })
  print("============================================")