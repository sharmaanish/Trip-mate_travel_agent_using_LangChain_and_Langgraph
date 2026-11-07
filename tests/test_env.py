import os
from dotenv import load_dotenv

load_dotenv()

variables = [
    "GROQ_API_KEY",
    "AVIATIONSTACK_API_KEY",
    "TAVILY_API_KEY",
    "DATABASE_URL",
    "LANGSMITH_API_KEY",
    "LANGSMITH_PROJECT"
]

for var in variables:
    value = os.getenv(var)
    print(f"{var}: {'LOADED' if value else 'MISSING'}")