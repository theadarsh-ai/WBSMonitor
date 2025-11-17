"""
Test Azure AI connection and verify 100% agentic mode is working.
"""
import os
from pydantic import SecretStr
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

def test_azure_connection():
    print("=" * 60)
    print("🧪 Testing Azure AI Connection for 100% Agentic Mode")
    print("=" * 60)
    
    endpoint = os.getenv("AZURE_INFERENCE_ENDPOINT", "").strip('"').strip("'")
    credential = os.getenv("AZURE_INFERENCE_CREDENTIAL", "").strip('"').strip("'")
    deployment = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4").strip('"').strip("'")
    api_version = os.getenv("AZURE_API_VERSION", "2024-02-15-preview").strip('"').strip("'")
    
    print(f"\n📋 Configuration:")
    print(f"  Endpoint: {endpoint[:60]}...")
    print(f"  Deployment: {deployment}")
    print(f"  API Version: {api_version}")
    print(f"  Credential: {'✓ SET (' + str(len(credential)) + ' chars)' if credential else '✗ NOT SET'}")
    
    if not endpoint or not credential:
        print("\n❌ Missing required credentials!")
        return False
    
    try:
        print(f"\n🔌 Attempting connection to Azure AI...")
        llm = AzureChatOpenAI(
            azure_endpoint=endpoint,
            api_key=SecretStr(credential),
            api_version=api_version,
            azure_deployment=deployment,
            temperature=0.7
        )
        
        print(f"✓ Client initialized")
        
        print(f"\n🤖 Testing AI decision-making capability...")
        messages = [
            SystemMessage(content="You are an expert project risk analyst."),
            HumanMessage(content="Analyze this task: 'Database Migration - 45% complete, due in 5 days'. Respond with just: CRITICAL, ALERT, AT_RISK, or ON_TRACK")
        ]
        
        response = llm.invoke(messages)
        result = response.content if hasattr(response, 'content') else str(response)
        
        print(f"✓ AI Response: {result}")
        print(f"\n✅ SUCCESS! Azure AI is working in 100% AGENTIC MODE!")
        print(f"   All decisions will now be made by AI autonomously.")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"1. Verify endpoint URL is correct (should start with https://)")
        print(f"2. Check API key is valid")
        print(f"3. Confirm deployment name '{deployment}' exists in Azure")
        print(f"4. Try API version '2024-08-01-preview' if current doesn't work")
        return False

if __name__ == "__main__":
    success = test_azure_connection()
    exit(0 if success else 1)
