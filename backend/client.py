import dotenv
dotenv.load_dotenv()

from openai import AsyncOpenAI 
from groq import AsyncGroq
import os

llm_client_choice = os.getenv("LLM_CLIENT")

if llm_client_choice == "groq":
    client = AsyncGroq(
        # This is the default and can be omitted
        api_key=os.getenv("GROQ_API_KEY"),
    )
else:
    client = AsyncOpenAI()