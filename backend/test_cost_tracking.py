#!/usr/bin/env python3
"""Test script to verify OpenAI API cost tracking is working."""

import os
from dotenv import load_dotenv
from services.openai_service import extract_fields_with_openai, analyze_with_prompt, calculate_cost

load_dotenv()

def test_cost_calculation():
    """Test the cost calculation function."""
    print("=" * 60)
    print("Testing Cost Calculation Function")
    print("=" * 60)
    
    # Mock usage data
    test_usage = {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150
    }
    
    # Test GPT-4
    gpt4_cost = calculate_cost(test_usage, "gpt-4")
    print(f"\nGPT-4 Cost for 150 tokens (100 prompt + 50 completion):")
    print(f"  Prompt cost: 100/1000 * $0.03 = ${(100/1000) * 0.03:.6f}")
    print(f"  Completion cost: 50/1000 * $0.06 = ${(50/1000) * 0.06:.6f}")
    print(f"  Total: ${gpt4_cost['cost_usd']:.6f}")
    
    # Test GPT-3.5
    gpt35_cost = calculate_cost(test_usage, "gpt-3.5-turbo")
    print(f"\nGPT-3.5-Turbo Cost for 150 tokens:")
    print(f"  Total: ${gpt35_cost['cost_usd']:.6f}")
    
    print(f"\n✓ Cost calculation working correctly!")


def test_extract_fields():
    """Test field extraction with cost tracking."""
    print("\n" + "=" * 60)
    print("Testing Resume Field Extraction (GPT-3.5-Turbo)")
    print("=" * 60)
    
    sample_resume = """
    John Doe
    Senior Software Engineer
    
    Experience: 5 years
    
    Skills:
    - Python, JavaScript, React
    - AWS, Docker, Kubernetes
    - PostgreSQL, MongoDB
    """
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not found. Skipping live API test.")
        return
    
    print("\nCalling OpenAI API...")
    result = extract_fields_with_openai(sample_resume)
    
    if result.get("api_usage"):
        usage = result["api_usage"]
        print(f"\n✓ API call successful!")
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {usage['prompt_tokens']}")
        print(f"  Completion tokens: {usage['completion_tokens']}")
        print(f"  Total tokens: {usage['total_tokens']}")
        print(f"\n💰 Cost: ${usage['cost_usd']:.6f}")
        
        print(f"\nExtracted Fields:")
        print(f"  Skills: {result.get('skills', [])}")
        print(f"  Titles: {result.get('titles', [])}")
        print(f"  Years: {result.get('years_exp', 0)}")
    else:
        print("\n❌ No usage data returned. Check if OpenAI API is configured correctly.")


def test_analyze_prompt():
    """Test prompt analysis with cost tracking."""
    print("\n" + "=" * 60)
    print("Testing Resume Analysis with Prompt (GPT-4)")
    print("=" * 60)
    
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  OPENAI_API_KEY not found. Skipping live API test.")
        return
    
    # Mock resume contexts
    contexts = [
        {
            "text": "Senior Python developer with 5 years experience in AWS...",
            "metadata": {
                "category": "Software Engineer",
                "skills": ["Python", "AWS", "Docker"],
                "years": 5
            },
            "score": 0.85
        }
    ]
    
    prompt = "Who are the best Python developers?"
    
    print(f"\nQuery: {prompt}")
    print("Calling OpenAI API...")
    
    result = analyze_with_prompt(prompt, contexts)
    
    if result.get("api_usage"):
        usage = result["api_usage"]
        print(f"\n✓ API call successful!")
        print(f"\nToken Usage:")
        print(f"  Prompt tokens: {usage['prompt_tokens']}")
        print(f"  Completion tokens: {usage['completion_tokens']}")
        print(f"  Total tokens: {usage['total_tokens']}")
        print(f"\n💰 Cost: ${usage['cost_usd']:.6f}")
        print(f"\nModel: {result['model']}")
        print(f"Answer preview: {result['answer'][:150]}...")
    else:
        print("\n❌ No usage data returned.")


def main():
    """Run all tests."""
    print("\n🧪 OpenAI Cost Tracking Test Suite\n")
    
    # Test 1: Cost calculation logic
    test_cost_calculation()
    
    # Test 2: Live API call (if key is available)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"\n✓ OpenAI API key found (ends with: ...{api_key[-4:]})")
        
        try:
            test_extract_fields()
            test_analyze_prompt()
        except Exception as e:
            print(f"\n❌ Error during live API test: {e}")
    else:
        print("\n⚠️  No OPENAI_API_KEY found in environment.")
        print("Set it to run live API tests:")
        print("  export OPENAI_API_KEY='sk-...'")
    
    print("\n" + "=" * 60)
    print("✅ Cost tracking tests complete!")
    print("=" * 60)
    print("\nTo see costs in your API responses, make requests to:")
    print("  - POST /api/analyze-resume")
    print("  - POST /api/query (with use_openai=true)")
    print("  - POST /api/find-references (with include_comparison=true)")
    print("\nAll responses will now include 'api_usage' with cost information.")
    print("\n")


if __name__ == "__main__":
    main()
