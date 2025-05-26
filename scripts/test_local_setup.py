#!/usr/bin/env python3
"""Test EAIA setup locally before deployment."""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set environment
os.environ['USE_AWS_SECRETS'] = 'true'
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'


def test_imports():
    """Test that all required modules can be imported."""
    print("📦 Testing imports...")
    try:
        import langchain
        import langgraph
        import anthropic
        import openai
        from eaia.main import graph
        from eaia import gmail
        from eaia.aws_secrets import get_gmail_credentials_from_aws
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print("\n📋 Testing configuration...")
    try:
        from eaia.main.config import get_config
        import yaml
        from pathlib import Path
        
        # Load config directly from yaml
        config_path = Path(__file__).parent.parent / "eaia" / "main" / "config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        print(f"✅ Config loaded for: {config['email']}")
        print(f"   Name: {config['full_name']}")
        print(f"   Timezone: {config['timezone']}")
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False


def test_gmail_connection():
    """Test Gmail API connection."""
    print("\n📧 Testing Gmail connection...")
    try:
        from eaia.gmail import get_credentials
        from googleapiclient.discovery import build
        
        creds = get_credentials()
        service = build("gmail", "v1", credentials=creds)
        
        # Get profile
        profile = service.users().getProfile(userId="me").execute()
        print(f"✅ Connected to Gmail: {profile.get('emailAddress')}")
        print(f"   Total messages: {profile.get('messagesTotal')}")
        
        # Get one recent message
        results = service.users().messages().list(
            userId="me",
            maxResults=1,
            q="newer_than:1d"
        ).execute()
        
        if results.get('messages'):
            print("✅ Can read emails successfully")
        else:
            print("⚠️  No emails in last 24 hours")
        
        return True
    except Exception as e:
        print(f"❌ Gmail error: {e}")
        return False


def test_llm_apis():
    """Test LLM API connections."""
    print("\n🤖 Testing LLM APIs...")
    
    # Test OpenAI
    try:
        import openai
        client = openai.Client()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        print("✅ OpenAI API working")
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False
    
    # Test Anthropic
    try:
        import anthropic
        client = anthropic.Client()
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": "Say 'test successful'"}],
            max_tokens=10
        )
        print("✅ Anthropic API working")
    except Exception as e:
        print(f"❌ Anthropic error: {e}")
        return False
    
    return True


def test_graph_structure():
    """Test the LangGraph structure."""
    print("\n🔧 Testing graph structure...")
    try:
        from eaia.main.graph import graph
        
        # Check graph is compiled
        if hasattr(graph, 'nodes'):
            print(f"✅ Graph compiled with {len(graph.nodes)} nodes")
        else:
            print("✅ Graph structure loaded")
        
        # List available entry points
        print("   Entry points available for testing")
        
        return True
    except Exception as e:
        print(f"❌ Graph error: {e}")
        return False


def main():
    """Run all tests."""
    print("EAIA Local Setup Test")
    print("=" * 50)
    
    # Check environment variables
    print("🔍 Environment Check:")
    env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "LANGSMITH_API_KEY",
        "USE_AWS_SECRETS",
        "AWS_REGION"
    ]
    
    missing = []
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            if "KEY" in var:
                print(f"✅ {var}: {'*' * 8}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            if var != "LANGSMITH_API_KEY":  # Optional for local testing
                missing.append(var)
    
    if missing:
        print(f"\n❌ Missing required variables: {', '.join(missing)}")
        print("Set these before running EAIA")
        return 1
    
    # Run tests
    tests = [
        test_imports,
        test_config,
        test_gmail_connection,
        test_llm_apis,
        test_graph_structure
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} tests passed!")
        print("\n🚀 Ready for deployment!")
        print("\nNext steps:")
        print("1. Set LANGSMITH_API_KEY environment variable")
        print("2. Run: langgraph dev")
        print("3. Test email ingestion with run_ingest.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\nFix the failing tests before deployment")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())