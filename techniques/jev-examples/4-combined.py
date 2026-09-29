from dotenv import load_dotenv
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

load_dotenv()

with TypeSafeClient() as client:
    response = client.system_one(
        state=(
            "Stripe has failed to connect for three days. "
            "Please help immediately."
        ),
        questions={
            "department": Choice(
                instructions="Which team should handle this request?",
                criteria={
                    "billing": "Payment or subscription issues.",
                    "technical": "Product bugs or integration failures.",
                },
            ),
            "urgent": Noul(
                instructions="Does this message require an urgent response?"
            ),
            "frustration": Score(
                instructions="How frustrated does the customer appear?",
                criteria=["Calm.", "Concerned but civil.", "Very angry."],
            ),
        },
    )

department = response.choices["department"]
urgency = response.nouls["urgent"]
frustration = response.scores["frustration"]

print(f"Department: {department.choice} (confidence={department.confidence:.2f})")
print(f"Urgent: {urgency.noul:.2f}")
print(f"Frustration: {frustration.score:.2f}")
