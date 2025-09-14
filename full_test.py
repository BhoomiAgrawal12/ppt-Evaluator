import requests
import json
import os
from create_test_ppt import create_test_presentation

def full_system_test():
    """Complete end-to-end test of the PPT evaluation system"""
    print("="*60)
    print("SIH PPT EVALUATOR - FULL SYSTEM TEST")
    print("="*60)
    
    # Step 1: Test API health
    print("\n1. Testing API Health...")
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("   ✓ API is running successfully")
            api_info = response.json()
            print(f"   ✓ Version: {api_info.get('version', 'Unknown')}")
        else:
            print(f"   ✗ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Cannot connect to API: {e}")
        print("   Please make sure the Flask app is running (python app.py)")
        return False
    
    # Step 2: Create test presentation
    print("\n2. Creating Test Presentation...")
    try:
        ppt_filename = create_test_presentation()
        print(f"   ✓ Created: {ppt_filename}")
    except Exception as e:
        print(f"   ✗ Failed to create test PPT: {e}")
        return False
    
    # Step 3: Test evaluation
    print("\n3. Testing PPT Evaluation...")
    try:
        problem_statement = """
        Develop a mobile application for rural healthcare management that connects patients 
        with healthcare providers, manages medical records, and provides telemedicine 
        capabilities for remote areas with limited internet connectivity. The solution 
        should be scalable, secure, and work offline when needed.
        """
        
        with open(ppt_filename, 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': 'HealthTech Innovators',
                'problem_statement': problem_statement.strip()
            }
            
            print("   Sending evaluation request...")
            response = requests.post(
                'http://localhost:5000/api/evaluate', 
                files=files, 
                data=data, 
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                evaluation_id = result.get('evaluation_id', '')
                print(f"   ✓ Evaluation completed successfully!")
                print(f"   ✓ Evaluation ID: {evaluation_id}")
                
                # Display results
                display_evaluation_results(result)
                
                # Step 4: Test retrieval
                print("\n4. Testing Result Retrieval...")
                test_retrieval(evaluation_id)
                
                # Step 5: Test listing
                print("\n5. Testing Evaluation Listing...")
                test_listing()
                
                return True
            else:
                print(f"   ✗ Evaluation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ✗ Evaluation error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(ppt_filename):
            os.remove(ppt_filename)
            print(f"\n   Cleaned up test file: {ppt_filename}")

def display_evaluation_results(result):
    """Display detailed evaluation results"""
    final_score = result.get('results', {}).get('final_score', {})
    
    print(f"\n📋 EVALUATION RESULTS:")
    print(f"   Team: {result.get('results', {}).get('team_name', 'N/A')}")
    print(f"   Final Score: {final_score.get('percentage_score', 0):.2f}%")
    print(f"   Grade: {final_score.get('grade', 'N/A')}")
    
    # Component scores
    component_scores = final_score.get('component_scores', {})
    print(f"\n📊 Component Breakdown:")
    for component, score in component_scores.items():
        print(f"   {component.replace('_', ' ').title()}: {score:.3f}")
    
    # Quick summary
    strengths = final_score.get('strengths', [])
    weaknesses = final_score.get('weaknesses', [])
    
    if strengths:
        print(f"\n💪 Key Strengths ({len(strengths)}):")
        for strength in strengths[:2]:
            print(f"   • {strength}")
    
    if weaknesses:
        print(f"\n⚠️  Areas to Improve ({len(weaknesses)}):")
        for weakness in weaknesses[:2]:
            print(f"   • {weakness}")

def test_retrieval(evaluation_id):
    """Test retrieving evaluation by ID"""
    try:
        response = requests.get(f"http://localhost:5000/api/evaluations/{evaluation_id}")
        if response.status_code == 200:
            print("   ✓ Successfully retrieved evaluation by ID")
        else:
            print(f"   ✗ Failed to retrieve evaluation: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Retrieval error: {e}")

def test_listing():
    """Test listing all evaluations"""
    try:
        response = requests.get("http://localhost:5000/api/evaluations")
        if response.status_code == 200:
            evaluations = response.json()
            print(f"   ✓ Successfully listed evaluations (found {len(evaluations)})")
        else:
            print(f"   ✗ Failed to list evaluations: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Listing error: {e}")

if __name__ == "__main__":
    success = full_system_test()
    
    print("\n" + "="*60)
    if success:
        print("🎉 ALL TESTS PASSED! System is ready for production use.")
        print("\nNext steps:")
        print("• Use 'python test_with_ppt.py' to test with your own PPT files")
        print("• Use 'python run_evaluation.py' for batch processing")
        print("• Access the API at http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print("="*60)