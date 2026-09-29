from dotenv import load_dotenv
from typesafe_sdk import Score, TypeSafeClient

load_dotenv()

with TypeSafeClient() as client:
    response = client.system_one(
        state="This has failed three times. Fix it now.",
        questions={
            "frustration": Score(
                instructions="How frustrated does the customer appear?",
                criteria=[
                    "Calm and neutral.",
                    "Concerned but civil.",
                    "Very angry or using strong language.",
                ],
            ),
        },
    )

frustration = response.scores["frustration"]

print(f"Score: {frustration.score:.2f}")
print(f"Legend: {frustration.legend}")
print(f"Probabilities: {frustration.probabilities}")
