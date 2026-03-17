# https://ollama.com/blog/web-search

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env", override=True)

import ollama  # noqa: E402

response = ollama.web_search("What is Ollama?")

print(response)

for result in response["results"]:    
    print(result["title"])
    print(result["url"])
    #print(result["content"][0:50] + " ...")
    print("------\n")
