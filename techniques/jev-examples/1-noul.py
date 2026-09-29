from dotenv import load_dotenv
from typesafe_sdk import Noul, TypeSafeClient

load_dotenv()

with TypeSafeClient() as client:
    response = client.system_one(
        state=(
            "The deploy failed twice and customers are seeing 500s. "
            "Can someone look now?"
        ),
        questions={
            "urgent": Noul(
                instructions="Does this need attention right now?"
            ),
        },
    )

urgency = response.nouls["urgent"].noul
print(urgency)
