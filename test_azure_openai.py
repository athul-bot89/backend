#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI configuration
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def test_azure_openai():
    """Test Azure OpenAI connection and configuration."""
    
    print("=" * 50)
    print("Azure OpenAI Configuration Test")
    print("=" * 50)
    
    try:
        from app.config import settings
        
        print("\n✅ Configuration loaded successfully!")
        print(f"   - Use Azure OpenAI: {settings.use_azure_openai}")
        
        if settings.use_azure_openai:
            print(f"   - Endpoint: {settings.azure_openai_endpoint}")
            print(f"   - Deployment: {settings.azure_openai_deployment}")
            print(f"   - API Version: {settings.azure_openai_api_version}")
            print(f"   - API Key: {'***' + settings.azure_openai_api_key[-4:] if settings.azure_openai_api_key else 'NOT SET'}")
        else:
            print(f"   - OpenAI API Key: {'***' + settings.openai_api_key[-4:] if settings.openai_api_key else 'NOT SET'}")
        
        print("\n🔧 Initializing AI Service...")
        from app.services.ai_service import AIService
        
        ai_service = AIService()
        print("✅ AI Service initialized successfully!")
        print(f"   - Model: {ai_service.model_name}")
        
        print("\n🧪 Testing simple completion...")
        
        # Test a simple completion
        response = ai_service.client.chat.completions.create(
            model=ai_service.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Azure OpenAI is configured correctly!' if you can respond."}
            ],
            max_tokens=50,
            temperature=0
        )
        
        print("✅ API call successful!")
        print(f"   Response: {response.choices[0].message.content}")
        
        print("\n" + "=" * 50)
        print("✨ All tests passed! Azure OpenAI is configured correctly.")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Make sure your .env file contains the correct Azure OpenAI credentials")
        print("   2. Verify your Azure OpenAI endpoint URL is correct")
        print("   3. Ensure your API key has access to the deployment")
        print("   4. Check that the deployment name matches what's in Azure")
        return False
    
    return True

if __name__ == "__main__":
    success = test_azure_openai()
    sys.exit(0 if success else 1)