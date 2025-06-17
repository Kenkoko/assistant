from litellm import completion
from llm.agents.basic_tools import weatherTool
import json

PROMPT = """
You are a helpful AI agent that can use tool to find weather information and summize the information.
You must report in this format:
**Current Weather:**

* Temperature: 22.5°C (air temperature)
* Humidity: 97.4% (relative humidity)
* Wind Speed: 3.3 m/s
* Wind Direction: 192.6° (from the northwest)

It's mostly cloudy with a cloud area fraction of 100%.

**Next 1 hour:**

* Weather Symbol: Cloudy
* Precipitation Amount: 0 mm

**Next 12 hours:**

* Weather Summary: Partly Cloudy Day
* Wind Speed and Direction: No information provided

**Next 6 hours:**

* Weather Summary: Partly Cloudy Night
* Precipitation Amount: 0 mm

If you do not know the answer, respond honestly by stating that you don't know!
"""

class WeatherAgent:
  def __init__(self, prompt: str = None):
    if prompt is None:
      prompt = PROMPT
    self.system_prompt = {
        "role": "system",
        "content": prompt
    }
    self.tools = [
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
      }
    ]
  
  def invoke(self, request):
    messages_for_llm = [self.system_prompt]
    messages_for_llm.append({
      "role": "user",
      "content": request,
    })
    response = completion(
        model="ollama/llama3.2", 
        messages=messages_for_llm,
        tools=self.tools,
        api_base="http://localhost:11434"
    )

    tool_call = response.choices[0].message.tool_calls[0]
    if tool_call:
      if tool_call.function.name != 'weatherTool':
        print(f"Invalid function name: {tool_call.function.name} not found")
      else:
        function_args = json.loads(tool_call.function.arguments)
        function_response = weatherTool(
            **function_args
        )
        if type(function_response) is not str:
          print(f"reqired: {function_args['location']} - get: {function_response['location']}")
        messages_for_llm.append(
          {
              "role": "tool",
              "content": f"{json.dumps(function_response)}",
          }
        )  # extend conversation with function response
        response = completion(
            model="ollama/llama3.2", 
            messages=messages_for_llm,
            api_base="http://localhost:11434"
        )
    answer = response.json()['choices'][-1]['message']['content']
    return answer


questions = [
    "give me weather of Moss",
    "How is the weather now in Lysaker",
    "How is the weather now in Dĩ An City in Vietnam",
    "How is the weather now in Tromso",
    "Thời tiết như thế nào tại quận 4 thành phố hồ chí minh",
    "How is the weather now in Mars"
]
agent = WeatherAgent()
for question in questions:
  answer = agent.invoke(question)
  print(f"Question: {question}")
  print(f"Answer: {answer}")

  print("============================================")