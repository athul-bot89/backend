import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Get API key from .env file
api_key = os.getenv('OPENAI_API_KEY')

# Configure OpenAI client
client = openai.OpenAI(api_key=api_key)

def test_gpt_response():
    try:
        # Make a test request to GPT
        response = client.chat.completions.create(
            model="gpt-5.2-mini",  # Using a valid model (or "gpt-4" or "gpt-3.5-turbo")
            messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short bedtime story about a unicorn."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        # Print the response
        print("Response:", response.choices[0].message.content)
        print("Status: Success")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gpt_response()