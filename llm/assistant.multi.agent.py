from litellm import completion
from basic_tools import weatherTool
import json

PROMPT = """
In this conversation between a human and the AI, the AI is helpful and friendly, and when it does not know the answer it says "I don't know"
"""


system_prompt = {
    "role": "system",
    "content": PROMPT
}


questions = [
    'what is the weather in Oslo',
    'In what year did Qin Shi Huang unify the six states?',
    'Who was the founder of the Han Dynasty?',
    'Who was the last emperor of the Tang Dynasty?',
    'Who was the founding emperor of the Ming Dynasty?',
    'What did I asked you so far',
]

tools = [
  {
      "type": "function",
      "function": {
          "name": "weatherTool",
          "description": "Get the current weather in a given location",
          "parameters": {
              "type": "object",
              "properties": {
                  "location": {
                      "type": "string",
                      "description": "The city and state, e.g. San Francisco, CA",
                  },
              },
              "required": ["location"],
          },
      },
  }
]

messages = []
messages.append(system_prompt)

for question in questions:
  messages.append({
    "role": "user",
    "content": question,
  })
  response = completion(
      model="ollama/llama3.2", 
      messages=messages,
      # tools=tools,
      api_base="http://localhost:11434"
  )

  response_message = response.choices[0].message
  tool_calls = response_message.tool_calls

  if tool_calls:
    available_functions = {
        "weatherTool": weatherTool,
    }  # only one function in this example, but you can have multiple
    messages.append(response_message)
    for tool_call in tool_calls:
      function_name = tool_call.function.name
      function_to_call = available_functions[function_name]
      function_args = json.loads(tool_call.function.arguments)
      function_response = function_to_call(
          location=function_args.get("location"),
      )
      messages.append(
        {
            "tool_call_id": tool_call.id,
            "role": "ipython",
            "name": function_name,
            "content": function_response,
        }
      )  # extend conversation with function response
    second_response = completion(
        model="ollama/llama3.2", 
        messages=messages,
        api_base="http://localhost:11434"
    )  # get a new response from the model where it can see the function response
  answer = response.json()['choices'][-1]['message']['content']
  print(f"Answer: {answer}")

  messages.append({
    "role": "assistant",
    "content": answer,
  })