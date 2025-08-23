import os
from dotenv import load_dotenv

print("Testing .env file loading...")

# Load environment variables
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"✅ API Key loaded successfully!")
    print(f"   First 10 characters: {api_key[:10]}...")
    print(f"   Length: {len(api_key)} characters")
else:
    print("❌ API Key not loaded!")
    print("   Available environment variables:")
    for key, value in os.environ.items():
        if "GEMINI" in key or "API" in key:
            print(f"   {key}: {value[:10] if value else 'None'}...")

print("\nCurrent working directory:", os.getcwd())
print(".env file exists:", os.path.exists(".env"))
