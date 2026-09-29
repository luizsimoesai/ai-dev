import asyncio

from dotenv import load_dotenv
from typesafe_sdk import AsyncTypeSafeClient, Noul

load_dotenv()


async def main() -> None:
    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state="Please refund the duplicate charge.",
            questions={
                "refund_requested": Noul(
                    instructions="Does the customer request a refund?"
                ),
            },
        )

    refund_requested = response.nouls["refund_requested"]
    print(f"Refund requested: {refund_requested.noul:.2f}")


if __name__ == "__main__":
    asyncio.run(main())
