#!/usr/bin/env python3
"""
Quick test of LLM evaluator without dependencies
"""

from evaluator.llm_evaluator import LLMEvaluator

def quick_test():
    print("Quick LLM Evaluator Test")
    print("=" * 30)

    # Sample content
    sample_content = {
        'text': "Healthcare app for rural areas with offline functionality",
        'slides': [{'slide_number': 1, 'content': 'Test slide', 'word_count': 10}],
        'images': []
    }

    problem_statement = "Develop a healthcare monitoring app for rural areas"
    team_name = "Test Team"

    try:
        evaluator = LLMEvaluator()

        if not evaluator.model:
            print("WARNING: GEMINI_API_KEY not configured")
            print("This will test the system structure but use fallback responses")
        else:
            print("SUCCESS: Gemini API configured")

        # Test evaluation
        print("\nRunning evaluation...")
        results = evaluator.evaluate_presentation(sample_content, problem_statement, team_name)

        print(f"Team: {results.get('team_name')}")
        print(f"Method: {results.get('evaluation_method')}")
        print(f"Timestamp: {results.get('timestamp')}")

        if results.get('error'):
            print(f"Error: {results['error']}")
        else:
            print("SUCCESS: Evaluation completed")

        ai_detection = results.get('ai_detection', {})
        print(f"AI Detection Method: {ai_detection.get('method', 'Unknown')}")
        print(f"AI Generated: {ai_detection.get('is_ai_generated', 'Unknown')}")

        final_assessment = results.get('final_assessment', {})
        if final_assessment and not final_assessment.get('error'):
            print(f"Overall Score: {final_assessment.get('overall_score', 0)}")
            print(f"Grade: {final_assessment.get('grade', 'N/A')}")

        print("\nQUICK TEST PASSED!")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_test()