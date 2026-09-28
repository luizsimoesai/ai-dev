# https://platform.openai.com/docs/guides/tools

from dotenv import load_dotenv
from openai import OpenAI
_ = load_dotenv()

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1",
    tools=[{"type": "web_search_preview"}],
    input="What is the exchange rate for the dollar today?"
)

print(response.output_text)

