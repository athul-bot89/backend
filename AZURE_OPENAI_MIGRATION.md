# Azure OpenAI Migration Guide

This guide explains how to configure your AI Teaching Assistant backend to use Azure OpenAI instead of the standard OpenAI API.

## Why Azure OpenAI?

Azure OpenAI provides:
- 🔐 **Enterprise Security**: Built-in Azure security and compliance
- 🌍 **Regional Deployment**: Deploy models closer to your users
- 📊 **Better Monitoring**: Azure Monitor integration for usage tracking
- 💼 **Enterprise Support**: Azure support channels
- 🚀 **Latest Models**: Access to advanced models like GPT-5.2

## Your Azure OpenAI Configuration

Based on your provided model configuration:

```json
{
  "name": "gpt-5.2-chat",
  "endpoint": "https://ai-kokuljosetesthub385023345165.openai.azure.com/openai/deployments/gpt-5.2-chat/chat/completions?api-version=2025-01-01-preview"
}
```

### Extracted Configuration Details:
- **Resource Name**: `ai-kokuljosetesthub385023345165`
- **Deployment Name**: `gpt-5.2-chat`
- **API Version**: `2025-01-01-preview`
- **Model Version**: GPT-5.2 (Latest generation!)

## Setup Instructions

### 1. Update Your .env File

Replace the contents of your `.env` file with:

```env
# Azure OpenAI Configuration
USE_AZURE_OPENAI=true
AZURE_OPENAI_API_KEY=<YOUR_AZURE_API_KEY>
AZURE_OPENAI_ENDPOINT=https://ai-kokuljosetesthub385023345165.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-5.2-chat
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Database and other settings remain the same
DATABASE_URL=sqlite:///./teaching_assistant.db
MAX_UPLOAD_SIZE=52428800
UPLOAD_DIR=uploads
CHAPTERS_DIR=chapters
API_HOST=0.0.0.0
API_PORT=8000
```

### 2. Get Your Azure OpenAI API Key

1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure OpenAI resource: `ai-kokuljosetesthub385023345165`
3. Under "Resource Management" → "Keys and Endpoint"
4. Copy either `KEY1` or `KEY2`
5. Replace `<YOUR_AZURE_API_KEY>` in the `.env` file

### 3. Test Your Configuration

Run the test script to verify everything is working:

```bash
python test_azure_openai.py
```

You should see:
```
✅ Configuration loaded successfully!
✅ AI Service initialized successfully!
✅ API call successful!
✨ All tests passed! Azure OpenAI is configured correctly.
```

### 4. Start Your Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Key Improvements with GPT-5.2

Your application now benefits from GPT-5.2's advanced capabilities:

1. **Better Chapter Detection**: More accurate identification of chapter structure
2. **Improved Summaries**: Higher quality educational content generation
3. **Enhanced Key Concepts**: Better extraction of important learning points
4. **Faster Response Times**: Optimized model performance
5. **Higher Token Limits**: Process longer documents more effectively

## Rate Limits

Your deployment has the following limits:
- **Requests**: 1,500 per minute
- **Tokens**: 150,000 per minute
- **Max Capacity**: 150 units

This is more than sufficient for educational content processing!

## Switching Back to OpenAI (If Needed)

To switch back to standard OpenAI:

1. Update `.env`:
```env
USE_AZURE_OPENAI=false
OPENAI_API_KEY=your_openai_api_key_here
```

2. Restart your application

## Troubleshooting

### Common Issues and Solutions:

1. **Authentication Error (401)**
   - Verify your API key is correct
   - Check the key hasn't expired
   - Ensure the key is for the correct resource

2. **Resource Not Found (404)**
   - Verify the endpoint URL is correct
   - Check the deployment name matches exactly
   - Ensure the deployment is active

3. **Rate Limit Exceeded (429)**
   - Implement retry logic with exponential backoff
   - Consider caching responses for repeated requests
   - Monitor usage in Azure Portal

4. **Model Not Available**
   - Verify the deployment status in Azure Portal
   - Check if the model needs to be deployed first
   - Ensure your subscription has access to GPT-5.2

## Monitoring Usage

Track your Azure OpenAI usage:

1. Go to Azure Portal
2. Navigate to your OpenAI resource
3. Check "Metrics" for:
   - Token usage
   - Request counts
   - Latency metrics
   - Error rates

## Support

For issues specific to:
- **Azure OpenAI**: Use Azure Support channels
- **Application Code**: Check the repository issues
- **API Integration**: Review the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)

## Next Steps

Now that Azure OpenAI is configured, you can:
1. Upload textbooks for processing
2. Use AI to detect and extract chapters
3. Generate summaries and educational content
4. Monitor performance and usage in Azure Portal

Enjoy the enhanced capabilities of GPT-5.2! 🚀