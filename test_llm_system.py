#!/usr/bin/env python3
"""
Test script for the LLM-based evaluation system
Tests the complete pipeline without requiring actual files
"""

import os
import sys
from datetime import datetime
from evaluator.llm_evaluator import LLMEvaluator

def test_llm_evaluator():
    """Test the LLM evaluator with sample data"""
    print("Testing LLM Evaluation System")
    print("=" * 50)

    # Create sample presentation content
    sample_content = {
        'text': """
        Healthcare Monitoring System for Rural Areas

        Problem Statement: Develop a mobile application for healthcare monitoring in rural areas where internet connectivity is limited.

        Our Solution: We propose "RuralHealth Monitor" - a mobile application that works offline and syncs data when connectivity is available.

        Key Features:
        - Offline data collection and storage
        - Basic health parameter monitoring (BP, temperature, pulse)
        - SMS-based alerts for emergencies
        - Cloud synchronization when internet is available
        - Simple interface for low-literacy users

        Technical Architecture:
        - React Native for cross-platform mobile app
        - SQLite for local data storage
        - Node.js backend with MongoDB
        - SMS gateway integration
        - Progressive Web App capabilities

        Implementation Plan:
        Phase 1: Basic health parameter recording (2 weeks)
        Phase 2: Offline functionality and local storage (2 weeks)
        Phase 3: SMS integration and cloud sync (1 week)
        Phase 4: Testing and deployment (1 week)

        Team: 4 members - 2 developers, 1 designer, 1 tester
        Budget: Low-cost solution using open-source technologies
        """,
        'slides': [
            {
                'slide_number': 1,
                'content': 'Healthcare Monitoring System for Rural Areas - Title Slide',
                'word_count': 8,
                'has_bullet_points': False,
                'title': 'Healthcare Monitoring System for Rural Areas'
            },
            {
                'slide_number': 2,
                'content': 'Problem Statement: Develop a mobile application for healthcare monitoring in rural areas',
                'word_count': 14,
                'has_bullet_points': False,
                'title': 'Problem Statement'
            },
            {
                'slide_number': 3,
                'content': 'Our Solution: RuralHealth Monitor - Key Features: Offline data collection, Health monitoring, SMS alerts',
                'word_count': 16,
                'has_bullet_points': True,
                'title': 'Our Solution'
            },
            {
                'slide_number': 4,
                'content': 'Technical Architecture: React Native, SQLite, Node.js, MongoDB',
                'word_count': 9,
                'has_bullet_points': False,
                'title': 'Technical Architecture'
            },
            {
                'slide_number': 5,
                'content': 'Implementation Plan: 4 phases over 6 weeks with 4 team members',
                'word_count': 12,
                'has_bullet_points': True,
                'title': 'Implementation Plan'
            }
        ],
        'images': [
            {
                'type': 'image',
                'description': 'System architecture diagram',
                'slide_number': 4
            },
            {
                'type': 'chart',
                'description': 'Implementation timeline chart',
                'slide_number': 5
            }
        ],
        'links': []
    }

    problem_statement = """
    Develop a comprehensive mobile application for healthcare monitoring in rural and remote areas
    where internet connectivity is intermittent or unavailable. The solution should enable healthcare
    workers to collect, store, and transmit patient data efficiently, with particular focus on
    maternal health, child health, and chronic disease management. The application should work
    offline and synchronize data when connectivity becomes available.
    """

    team_name = "HealthTech Innovators"

    # Initialize LLM evaluator
    try:
        evaluator = LLMEvaluator()

        if not evaluator.model:
            print("WARNING: GEMINI_API_KEY not configured. Using fallback mode.")
            print("   To test with actual LLM evaluation:")
            print("   1. Add GEMINI_API_KEY to your .env file")
            print("   2. Run this test again")
            print()

        # Run evaluation
        print("Starting LLM evaluation...")
        print(f"Team: {team_name}")
        print(f"Content length: {len(sample_content['text'])} characters")
        print(f"Slides: {len(sample_content['slides'])}")
        print(f"Images: {len(sample_content['images'])}")
        print()

        results = evaluator.evaluate_presentation(
            sample_content,
            problem_statement,
            team_name
        )

        # Display results
        print("Evaluation Results:")
        print(f"   Evaluation Method: {results.get('evaluation_method', 'Unknown')}")
        print(f"   Timestamp: {results.get('timestamp', 'Unknown')}")

        if results.get('error'):
            print(f"   ERROR: {results['error']}")
        else:
            print("   SUCCESS: Evaluation completed!")

        # Show AI detection results
        ai_detection = results.get('ai_detection', {})
        print(f"\nAI Content Detection:")
        print(f"   Is AI Generated: {ai_detection.get('is_ai_generated', 'Unknown')}")
        print(f"   Confidence: {ai_detection.get('confidence', 0):.2f}")
        print(f"   Method: {ai_detection.get('method', 'Unknown')}")

        # Show final assessment
        final_assessment = results.get('final_assessment', {})
        if final_assessment:
            print(f"\nFinal Assessment:")
            print(f"   Overall Score: {final_assessment.get('overall_score', 0):.3f}")
            print(f"   Percentage: {final_assessment.get('percentage_score', 0):.1f}%")
            print(f"   Grade: {final_assessment.get('grade', 'N/A')}")
            print(f"   Summary: {final_assessment.get('summary', 'No summary available')}")

            # Show strengths and weaknesses
            strengths = final_assessment.get('top_strengths', [])
            if strengths:
                print(f"\nTop Strengths:")
                for i, strength in enumerate(strengths[:3], 1):
                    print(f"   {i}. {strength}")

            weaknesses = final_assessment.get('key_weaknesses', [])
            if weaknesses:
                print(f"\nKey Weaknesses:")
                for i, weakness in enumerate(weaknesses[:3], 1):
                    print(f"   {i}. {weakness}")

        # Show evaluation details
        evaluations = results.get('evaluations', {})
        if evaluations:
            print(f"\nDetailed Evaluation Scores:")
            criteria_names = {
                'technical_feasibility': 'Technical Feasibility',
                'problem_alignment': 'Problem Alignment',
                'solution_quality': 'Solution Quality',
                'presentation_quality': 'Presentation Quality',
                'innovation': 'Innovation & Creativity'
            }

            for criteria, evaluation in evaluations.items():
                if evaluation and not evaluation.get('error'):
                    name = criteria_names.get(criteria, criteria.title())
                    score = evaluation.get('score', 0)
                    print(f"   {name}: {score:.3f} ({score*100:.1f}%)")

        print(f"\nTest completed successfully!")
        return True

    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_detector_service():
    """Test if the detector service is running"""
    print("\nTesting AI Content Detector Service")
    print("=" * 50)

    try:
        import requests

        test_text = "This is a sample text to test the AI detection service."
        response = requests.post(
            'http://localhost:5001/detect',
            json={'text': test_text},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print("SUCCESS: Detector service is running!")
            print(f"   Test result: {result['label']} (confidence: {result['score']:.3f})")
            return True
        else:
            print(f"WARNING: Detector service returned status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("WARNING: Detector service is not running on port 5001")
        print("   Start it with: python detector.py")
        return False
    except Exception as e:
        print(f"ERROR: Error testing detector service: {str(e)}")
        return False

def main():
    """Main test function"""
    print("SIH LLM Evaluator - System Test")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Test 1: LLM Evaluator
    test1_success = test_llm_evaluator()

    # Test 2: Detector Service
    test2_success = test_detector_service()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"   LLM Evaluator: {'PASS' if test1_success else 'FAIL'}")
    print(f"   AI Detector: {'PASS' if test2_success else 'NOT RUNNING'}")

    if test1_success:
        print("\nSUCCESS: Core LLM evaluation system is working!")
        if not test2_success:
            print("NOTE: AI detector service is not running, but LLM evaluation will use fallback mode.")
    else:
        print("\nERROR: LLM evaluation system has issues. Please check configuration.")

    print("\nTo start the full system: python start_services.py")
    print("Then open: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()