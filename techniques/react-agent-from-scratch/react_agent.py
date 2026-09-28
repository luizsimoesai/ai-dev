import argparse
import re
import requests
from openai import OpenAI
from sympy import sympify
from typing import Dict, List, Optional

from dotenv import load_dotenv
load_dotenv()


# --------------------------------------------------
# OPENAI - CLIENT
# --------------------------------------------------
client = OpenAI()
model = "gpt-4o-mini"


# --------------------------------------------------
# PROMPT
# --------------------------------------------------

prompt = '''
You operate in a loop of THOUGHT, ACTION, PAUSE, OBSERVATION.
At the end of the loop, you produce an ANSWER.

Use THOUGHT to describe your reasoning about the question you've been asked.
Use ACTION to run one of the actions available to you - then return PAUSE.
OBSERVATION will be the result of running that action.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python, so make sure to use floating point syntax if needed.

get_cost:
e.g. get_cost: keyboard
Returns the cost of a keyboard.

get_current_weather:
e.g. get_current_weather: Brasília
Returns the current temperature of a city.

wikipedia:
e.g. wikipedia: LangChain
Returns a summary from a Wikipedia search.

Always look things up on Wikipedia if you have the opportunity to do so.

Example session #1:

Question: How much does a monitor cost?
THOUGHT: I should check the cost of a monitor using get_cost.
ACTION: get_cost: monitor
PAUSE

You will be called again with this:

OBSERVATION: A monitor costs $799.00.

You then produce the answer:

ANSWER: A monitor costs $799.00.


Example session #2:

Question: What is the capital of France?
THOUGHT: I should look up France on Wikipedia.
ACTION: wikipedia: France
PAUSE

You will be called again with this:

OBSERVATION: France is a country. The capital is Paris.

You then produce the answer:

ANSWER: The capital of France is Paris.


Example session #3:

Question: What's the weather like in São Paulo?
THOUGHT: I should get the current temperature for São Paulo using get_current_weather.
ACTION: get_current_weather: São Paulo
PAUSE

You will be called again with this:

OBSERVATION: 21°C

You then produce the answer:

ANSWER: The current temperature in São Paulo is 21°C.

'''.strip()


# --------------------------------------------------
# AGENT
# --------------------------------------------------
class Agent:
    def __init__(self, system: str = "") -> None:
        self.system: str = system
        self.messages: List[Dict[str, str]] = []

        if self.system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, prompt: str) -> str:
        self.messages.append({"role": "user", "content": prompt})
        result: str = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self, model: str = model, temperature: float = 0) -> str:
        completion = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=self.messages
        )
        return completion.choices[0].message.content

# --------------------------------------------------
# TOOLS
# --------------------------------------------------
def calculate(expression: str) -> float:
    """
    Evaluates a mathematical expression given as a string and returns the result
    rounded to at most two decimal places. Uses the SymPy library.

    Args:
        expression (str): The mathematical expression to evaluate, e.g. "(2 * 10) + (3 * 15)".

    Returns:
        float: The evaluated result, rounded to at most two decimal places.
    """
    try:
        result = sympify(expression).evalf()
        return round(float(result), 2)
    except Exception as e:
        return f"Error: {e}"


def get_cost(item: str) -> str:
    """
    Simulates a call to a fictitious store API.
    Returns the cost of a tech item.

    Args:
        item (str): The name of the tech item.

    Returns:
        str: A message with the item's price, or a generic message for other items.
    """
    if item == 'mouse':
        return 'A mouse costs $19.90'
    elif item == 'keyboard':
        return 'A keyboard costs $29.90'
    elif item == 'monitor':
        return 'A monitor costs $159.00'
    else:
        return 'Other items cost $39.00.'


def get_current_weather(city: str) -> Optional[str]:
    """
    Gets the current temperature for a city using the wttr.in API.

    Args:
        city (str): The name of the city to get the weather for.

    Returns:
        Optional[str]: A formatted string with the current temperature in Celsius.
        Returns `None` if there's an error in the request or the data.
    """
    base_url = f"http://wttr.in/{city}?format=j1"
    response = requests.get(base_url)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        temperature = data['current_condition'][0]['temp_C']
    except (KeyError, IndexError):
        return None

    return f"{temperature}°C"


def wikipedia(search_term: str) -> Optional[str]:
    """
    Queries the Wikipedia API and returns the snippet from the first result found.

    Args:
        search_term (str): The search term to query on Wikipedia.

    Returns:
        Optional[str]: The snippet from the first result found. Returns `None` if there are no results.
    """
    response = requests.get('https://en.wikipedia.org/w/api.php', params={
        'action': 'query',
        'list': 'search',
        'srsearch': search_term,
        'format': 'json'
    })
    results = response.json().get('query').get('search', [])

    if not results:
        return None
    return results[0]['snippet']


tools = {
    'calculate': calculate,
    'get_cost': get_cost,
    'get_current_weather': get_current_weather,
    'wikipedia': wikipedia,
}


# --------------------------------------------------
# RUNNING THE AGENT LOOP
# --------------------------------------------------

# regex to find the 'ACTION' string
action_re = re.compile(r'^ACTION: (\w+): (.*)$')

def call_agent(question: str, max_turns: int = 5) -> str:
    i: int = 0
    bot: Agent = Agent(prompt)
    next_prompt: str = question

    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)

        # using the regex to parse the Agent's response
        actions = [
            action_re.match(a) for a in result.split('\n') if action_re.match(a)
        ]

        if actions:
            action, action_input = actions[0].groups()

            if action not in tools:
                raise Exception(f"Unknown action: {action}: {action_input}")

            print(f"\033[92m -- running --> {action} {action_input}\033[0m")
            observation = tools[action](action_input)

            print(f"\033[96mOBSERVATION:\033[0m {observation}")
            next_prompt = f'OBSERVATION: {observation}'
        else:
            return


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Call the agent with a prompt")
    parser.add_argument("prompt", type=str, help="Prompt text for the agent")
    args = parser.parse_args()

    call_agent(args.prompt)
