import os
import asyncio
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv

# Add references
from agent_framework import tool, Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from pydantic import Field

load_dotenv()


async def main():
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load the expenses data file
    script_dir = Path(__file__).parent
    file_path = script_dir / 'data.txt'
    with file_path.open('r') as file:
        data = file.read() + "\n"

    # Ask for a prompt
    user_prompt = input(f"Here is the expenses data in your file:\n\n{data}\n\nWhat would you like me to do with it?\n\n")

    # Run the async agent code
    await process_expenses_data(user_prompt, data)


# Create a tool function for the email functionality
@tool(approval_mode="never_require")
def submit_claim(
    to: Annotated[str, Field(description="Who to send the email to")],
    subject: Annotated[str, Field(description="The subject of the email.")],
    body: Annotated[str, Field(description="The text body of the email.")],
):
    print("\nTo:", to)
    print("Subject:", subject)
    print(body, "\n")


async def process_expenses_data(prompt, expenses_data):
    # Create a foundry chat client
    client = FoundryChatClient(
        project_endpoint=os.getenv("PROJECT_ENDPOINT"),
        model=os.getenv("MODEL_DEPLOYMENT_NAME"),
        credential=AzureCliCredential(),
    )

    # Initialize an agent with the tool and instructions
    agent = Agent(
        client=client,
        name="ExpenseClaimAgent",
        instructions="""You are an AI assistant for expense claim submission.
                    At the user's request, create an expense claim and use the submit_claim tool to send an email to expenses@contoso.com with the subject 'Expense Claim' and a body that contains itemized expenses with a total.
                    Then confirm to the user that you've done so. Don't ask for any more information from the user, just use the data provided to create the email.""",
        tools=[submit_claim],
    )

    # Use the agent to process the expenses data
    try:
        # Invoke the agent with the prompt and the expenses data
        response = await agent.run(f"{prompt}: {expenses_data}")
        # Display the response
        print(f"\n# Agent:\n{response.text}")
    except Exception as e:
        # Something went wrong
        print(e)


if __name__ == "__main__":
    asyncio.run(main())
