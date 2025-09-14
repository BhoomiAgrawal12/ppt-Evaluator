#!/usr/bin/env python3
"""
Test script for the PPT Evaluator API
Tests all endpoints and functionality
"""

import requests
import json
import os
import time

API_BASE_URL = "http://localhost:5000"

def test_api_health():
    """Test if API is running"""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to API: {e}")
        return False

def test_ppt_evaluation():
    """Test PPT evaluation endpoint"""
    print("\nTesting PPT evaluation...")
    
    # Create a simple test text file as mock PPT
    test_content = """
    Smart Healthcare Mobile Application
    
    Problem Statement:
    Develop a mobile application for rural healthcare management that connects patients 
    with healthcare providers and manages medical records.
    
    Our Solution:
    We propose a mobile application with the following features:
    - Patient registration and profile management
    - Appointment booking system
    - Medical record storage
    - Telemedicine video calling
    - Medicine reminder system
    
    Technology Stack:
    - Frontend: React Native
    - Backend: Node.js with Express
    - Database: MongoDB
    - Cloud: AWS
    
    Architecture:
    Our system follows a microservices architecture with separate services for 
    user management, appointments, and medical records.
    
    Implementation Plan:
    Phase 1: Basic app development (2 months)
    Phase 2: Telemedicine integration (1 month)
    Phase 3: Testing and deployment (1 month)
    
    GitHub Repository: https://github.com/team/healthcare-app
    Demo Video: https://youtube.com/watch?v=demo123
    """
    
    # Save test content to a file
    test_file = "test_presentation.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': 'TestTeam',
                'problem_statement': 'Develop a mobile application for rural healthcare management that connects patients with healthcare providers, manages medical records, and provides telemedicine capabilities.'
            }
            
            print(f"Sending request to {API_BASE_URL}/api/evaluate")
            response = requests.post(f"{API_BASE_URL}/api/evaluate", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Evaluation completed successfully")
                
                # Extract key results
                evaluation_id = result.get('evaluation_id', '')
                final_score = result.get('results', {}).get('final_score', {})
                
                print(f"Evaluation ID: {evaluation_id}")
                print(f"Final Score: {final_score.get('percentage_score', 0):.2f}%")
                print(f"Grade: {final_score.get('grade', 'N/A')}")
                
                # Print component scores
                component_scores = final_score.get('component_scores', {})
                print("\nComponent Scores:")
                for component, score in component_scores.items():
                    print(f"  {component}: {score:.3f}")
                
                return evaluation_id
            else:
                print(f"✗ Evaluation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except Exception as e:
        print(f"✗ Error during evaluation: {e}")
        return None
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)

def test_get_evaluation(evaluation_id):
    """Test retrieving evaluation by ID"""
    if not evaluation_id:
        print("\nSkipping evaluation retrieval test (no evaluation ID)")
        return
    
    print(f"\nTesting evaluation retrieval for ID: {evaluation_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/evaluations/{evaluation_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Successfully retrieved evaluation")
            print(f"Team: {result.get('team_name', 'N/A')}")
            print(f"Score: {result.get('percentage_score', 0):.2f}%")
        elif response.status_code == 404:
            print("✗ Evaluation not found")
        else:
            print(f"✗ Error retrieving evaluation: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during retrieval: {e}")

def test_list_evaluations():
    """Test listing all evaluations"""
    print("\nTesting evaluation listing...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/evaluations")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Successfully retrieved {len(result)} evaluations")
            
            if result:
                print("Recent evaluations:")
                for eval_data in result[:3]:  # Show first 3
                    print(f"  - {eval_data.get('team_name', 'N/A')}: {eval_data.get('percentage_score', 0):.2f}%")
            else:
                print("No evaluations found")
        else:
            print(f"✗ Error listing evaluations: {response.status_code}")
            
    except Exception as e:
        print(f"✗ Error during listing: {e}")

def test_invalid_requests():
    """Test invalid requests to ensure proper error handling"""
    print("\nTesting error handling...")
    
    # Test missing file
    try:
        data = {'team_name': 'Test', 'problem_statement': 'Test PS'}
        response = requests.post(f"{API_BASE_URL}/api/evaluate", data=data)
        
        if response.status_code == 400:
            print("✓ Properly handles missing file")
        else:
            print(f"✗ Unexpected response for missing file: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing missing file: {e}")
    
    # Test invalid evaluation ID
    try:
        response = requests.get(f"{API_BASE_URL}/api/evaluations/invalid-id")
        
        if response.status_code == 404:
            print("✓ Properly handles invalid evaluation ID")
        else:
            print(f"✗ Unexpected response for invalid ID: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing invalid ID: {e}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("PPT Evaluator API Test Suite")
    print("=" * 50)
    
    # Test API health
    if not test_api_health():
        print("\n✗ API is not running. Please start the application first.")
        return
    
    # Test evaluation
    evaluation_id = test_ppt_evaluation()
    
    # Wait a moment for processing
    time.sleep(1)
    
    # Test retrieval
    test_get_evaluation(evaluation_id)
    
    # Test listing
    test_list_evaluations()
    
    # Test error handling
    test_invalid_requests()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("=" * 50)

if __name__ == "__main__":
    main()