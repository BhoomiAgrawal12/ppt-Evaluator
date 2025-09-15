#!/usr/bin/env python3
"""
Verify the complete setup of the LLM-based evaluation system
"""

import os
from config import Config

def verify_setup():
    print("SIH LLM Evaluator - Setup Verification")
    print("=" * 50)

    # Check environment variables
    gemini_key = Config.GEMINI_API_KEY
    llama_key = Config.LLAMA_CLOUD_API_KEY

    print("1. API Keys Configuration:")
    print(f"   GEMINI_API_KEY: {'SET' if gemini_key else 'MISSING'}")
    print(f"   LLAMA_CLOUD_API_KEY: {'SET' if llama_key else 'MISSING'}")

    # Check dependencies
    print("\n2. Dependencies Check:")
    try:
        from google import genai
        print("   google.genai: AVAILABLE")
    except ImportError as e:
        print(f"   google.genai: IMPORT ERROR - {e}")

    try:
        from evaluator.llm_evaluator import LLMEvaluator
        print("   LLMEvaluator: AVAILABLE")
    except ImportError as e:
        print(f"   LLMEvaluator: IMPORT ERROR - {e}")

    try:
        from evaluator.ppt_parser import DocumentParser
        print("   DocumentParser: AVAILABLE")
    except ImportError as e:
        print(f"   DocumentParser: IMPORT ERROR - {e}")

    # Check file structure
    print("\n3. File Structure:")
    essential_files = [
        'app.py',
        'detector.py',
        'evaluator/llm_evaluator.py',
        'evaluator/ppt_parser.py',
        'templates/index.html',
        'start_services.py'
    ]

    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"   {file_path}: PRESENT")
        else:
            print(f"   {file_path}: MISSING")

    # Quick functionality test
    print("\n4. System Test:")
    try:
        evaluator = LLMEvaluator()
        if evaluator.client:
            print("   LLM Client: INITIALIZED SUCCESSFULLY")
        else:
            print("   LLM Client: FALLBACK MODE (API key needed)")

        # Test basic evaluation structure
        sample_content = {
            'text': 'Test content',
            'slides': [{'slide_number': 1, 'content': 'Test', 'word_count': 2}],
            'images': []
        }

        result = evaluator.evaluate_presentation(sample_content, 'Test problem', 'Test team')

        if result and 'evaluation_method' in result:
            print("   Evaluation Pipeline: WORKING")
        else:
            print("   Evaluation Pipeline: ERROR")

    except Exception as e:
        print(f"   System Test: ERROR - {e}")

    # Final recommendations
    print("\n5. Recommendations:")
    if not gemini_key:
        print("   - Add GEMINI_API_KEY to your .env file for full LLM evaluation")
    if not llama_key:
        print("   - Add LLAMA_CLOUD_API_KEY to your .env file for document parsing")

    if gemini_key and llama_key:
        print("   - All set! Run: python start_services.py")
    else:
        print("   - System will work in limited mode without API keys")

    print("\n" + "=" * 50)
    print("Setup verification complete!")

if __name__ == "__main__":
    verify_setup()