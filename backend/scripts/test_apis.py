import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.gemini_service import GeminiService
from app.services.web_search import WebSearchService
from app.services.knowledge_base import KnowledgeBaseService
from app.core.config import settings

async def test_gemini():
    """Test Gemini API integration."""
    print("\n🧪 Testing Gemini API...")
    try:
        service = GeminiService()
        result = await service.generate_solution("What is 2 + 2?")
        print("✅ Gemini API working")
        print(f"   Steps: {len(result.steps)}")
        print(f"   Answer: {result.final_answer[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini API failed: {str(e)}")
        return False

async def test_tavily():
    """Test Tavily API integration."""
    print("\n🧪 Testing Tavily API...")
    
    try:
        service = WebSearchService()
        result = await service.search_mathematics("derivative of x^2")
        print("✅ Tavily API working")
        print(f"   Found: {result.found}")
        print(f"   Sources: {len(result.sources)}")
        return True
    except Exception as e:
        print(f"❌ Tavily API failed: {str(e)}")
        return False

async def test_qdrant():
    """Test Qdrant integration."""
    print("\n🧪 Testing Qdrant...")
    
    try:
        service = KnowledgeBaseService()
        await service.initialize_collection()
        
        # Test search
        result = await service.search_knowledge_base("derivative")
        print("✅ Qdrant working")
        print(f"   Search result found: {result.found}")
        print(f"   Similarity score: {result.similarity_score}")
        return True
    except Exception as e:
        print(f"❌ Qdrant failed: {str(e)}")
        return False

async def main():
    """Run all API tests."""
    print("🚀 Math Routing Agent - API Integration Tests")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Checking environment variables...")
    
    required_vars = ["GEMINI_API_KEY", "TAVILY_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not getattr(settings, var.lower(), None):
            missing_vars.append(var)
            print(f"❌ {var} not set")
        else:
            print(f"✅ {var} configured")
    
    if missing_vars:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables and try again.")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Gemini", test_gemini()),
        ("Tavily", test_tavily()),
        ("Qdrant", test_qdrant())
    ]
    
    results = []
    for name, test_coro in tests:
        try:
            success = await test_coro
            results.append((name, success))
        except Exception as e:
            print(f"❌ {name} test crashed: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Math Routing Agent is ready to go!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
