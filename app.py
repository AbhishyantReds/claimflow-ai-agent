"""
ClaimFlow AI - Hugging Face Spaces Entry Point
"""
import sys
import os
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize database and vector store on first run
if not os.path.exists("data/claimflow.db"):
    print("🔧 Initializing database...")
    subprocess.run([sys.executable, "scripts/init_database.py"])
    print("✅ Database initialized")
    
if not os.path.exists("data/chroma_db"):
    print("🔧 Initializing vector store...")
    subprocess.run([sys.executable, "scripts/ingest_policies.py"])
    print("✅ Vector store initialized")

# Test OpenAI connection
print("\n🔍 Testing OpenAI connection...")
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage
    import config
    
    test_llm = ChatOpenAI(api_key=config.OPENAI_API_KEY, model="gpt-4o", timeout=10)
    response = test_llm.invoke([SystemMessage(content="Say OK")])
    print(f"✅ OpenAI connected successfully: {response.content}")
except Exception as e:
    print(f"❌ OpenAI connection FAILED: {e}")
    print("⚠️  App will start but conversation will not work!")

# Import and run the simple app
from ui.simple_app import demo

if __name__ == "__main__":
    demo.launch()
