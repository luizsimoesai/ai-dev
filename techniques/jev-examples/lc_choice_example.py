from dotenv import load_dotenv
from langchain_typesafe import Choice, TypeSafeClassifier

load_dotenv()

classifier = TypeSafeClassifier()

response = classifier.invoke({
    "state": "Stripe fails whenever I try to connect my account.",
    "questions": {
        "department": Choice(
            instructions="Which team should handle this request?",
            criteria={
                "billing": "Payment, invoice, or subscription issues.",
                "technical": "Product bugs or integration failures.",
                "sales": "Pricing or purchasing questions.",
            },
        ),
    },
})

department = response.choices["department"]

if department.confidence >= 0.7:
    print(f"Routing to {department.choice} (confidence={department.confidence:.2f})")
else:
    print("Confidence too low, routing to human triage.")
