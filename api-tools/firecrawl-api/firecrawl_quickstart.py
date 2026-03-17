# https://www.firecrawl.dev/

import os
from pydantic import BaseModel
from dotenv import load_dotenv
from firecrawl import Firecrawl

load_dotenv()  # loads .env
api_key = os.getenv("FIRECRAWL_API_KEY")

firecrawl = Firecrawl(api_key=api_key)

# Scrape a website:
doc = firecrawl.scrape("https://firecrawl.dev", formats=["markdown", "html"])
print(doc)

# Crawling
docs = firecrawl.crawl(url="https://docs.firecrawl.dev", limit=10)
print(docs)


# JSON Mode
class JsonSchema(BaseModel):
    graph_database_info: str
    is_neo4j: bool

result = firecrawl.scrape(
    'https://luizweb-e3e887ee.mintlify.app/neo4j',
    formats=[{
      "type": "json",
      "schema": JsonSchema
    }],
    only_main_content=False,
    timeout=120000
)

print(result)
