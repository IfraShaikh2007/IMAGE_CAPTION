import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load your .env file
genai.configure(api_key=os.getenv("API_KEY"))

for m in genai.list_models():
    print(m.name)
