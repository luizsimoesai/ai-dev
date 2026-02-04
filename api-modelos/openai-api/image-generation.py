from openai import OpenAI
import base64

from dotenv import load_dotenv
_ = load_dotenv()

client = OpenAI() 

response = client.responses.create(
    model="gpt-4.1-mini",
    input="pixel art style drawing of a man sitting at his desk developing a system in python",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

# -------------------------------------------------------


client = OpenAI()

img = client.images.generate(
    model="gpt-image-1",
    prompt="pixel art style drawing of a man sitting at his desk developing a system in python",
    n=1,
    size="1024x1024"
)

image_bytes = base64.b64decode(img.data[0].b64_json)
with open("output.png", "wb") as f:
    f.write(image_bytes)
