#!/usr/bin/env python3
"""
Test script to verify Azure OpenAI connection and configuration.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_openai_connection():
    """Test the Azure OpenAI connection with your provided configuration."""
    
    print("=" * 60)
    print("Azure OpenAI Connection Test")
    print("=" * 60)
    
    # Display configuration
    print("\nConfiguration Details:")
    print(f"Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    print(f"Deployment: {os.getenv('AZURE_OPENAI_DEPLOYMENT')}")
    print(f"API Version: {os.getenv('AZURE_OPENAI_API_VERSION')}")
    print(f"API Key: {'✓ Configured' if os.getenv('AZURE_OPENAI_API_KEY') else '✗ Not found'}")
    
    try:
        from openai import AzureOpenAI
        
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        )
        
        print("\n✓ Azure OpenAI client initialized successfully")
        
        # Test with a simple chat completion
        print("\nTesting chat completion...")
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT'),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello! Azure OpenAI is working correctly.' in exactly those words."}
            ],
            temperature=0,
            max_tokens=50
        )
        
        print(f"\nResponse from Azure OpenAI:")
        print(f"  {response.choices[0].message.content}")
        
        # Display model info
        print(f"\nModel Information:")
        print(f"  Model: {response.model}")
        print(f"  Usage: {response.usage.total_tokens} tokens")
        
        print("\n" + "=" * 60)
        print("✓ Azure OpenAI connection test PASSED!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error connecting to Azure OpenAI: {e}")
        print("\nPlease verify:")
        print("  1. Your API key is correct")
        print("  2. The endpoint URL is accessible")
        print("  3. The deployment name 'gpt-4o' exists in your Azure resource")
        print("  4. Your network allows connection to Azure")
        print("\n" + "=" * 60)
        print("✗ Azure OpenAI connection test FAILED")
        print("=" * 60)
        return False

def test_ai_service():
    """Test the AI service with the new configuration."""
    print("\n" + "=" * 60)
    print("Testing AI Service Integration")
    print("=" * 60)
    
    try:
        from app.services.ai_service import AIService
        
        # Initialize the AI service
        ai_service = AIService()
        print("\n✓ AI Service initialized successfully")
        print(f"  Using model: {ai_service.model_name}")
        
        # Test chapter detection with sample TOC
        sample_toc = """
        Table of Contents
        
        Chapter 1: Introduction to Python ............... 1
        Chapter 2: Data Types and Variables ............. 15
        Chapter 3: Control Flow ......................... 30
        """
        
        print("\nTesting chapter detection...")
        chapters = ai_service.detect_chapters_from_toc(sample_toc)
        
        if chapters:
            print(f"\n✓ Chapter detection successful!")
            print(f"  Found {len(chapters)} chapters:")
            for chapter in chapters:
                print(f"    - Chapter {chapter.get('chapter_number')}: {chapter.get('title')}")
        else:
            print("\n⚠ No chapters detected")
            
        return True
        
    except Exception as e:
        print(f"\n✗ Error testing AI Service: {e}")
        return False

if __name__ == "__main__":
    # Test Azure OpenAI connection
    connection_success = test_azure_openai_connection()
    
    if connection_success:
        # Test AI Service integration
        test_ai_service()
    else:
        print("\nSkipping AI Service test due to connection failure.")
        sys.exit(1)