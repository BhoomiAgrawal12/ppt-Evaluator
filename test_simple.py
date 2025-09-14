import requests
import json
import os
from create_test_ppt import create_test_presentation

def simple_test():
    """Simple test without Unicode characters"""
    print("="*60)
    print("SIH PPT EVALUATOR - SYSTEM TEST")
    print("="*60)
    
    # Step 1: Test API health
    print("\n1. Testing API Health...")
    try:
        response = requests.get("http://localhost:5000/")
        if response.status_code == 200:
            print("   [SUCCESS] API is running")
            api_info = response.json()
            print(f"   Version: {api_info.get('version', 'Unknown')}")
        else:
            print(f"   [FAILED] API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [FAILED] Cannot connect to API: {e}")
        print("   Please make sure Flask app is running (python app.py)")
        return False
    
    # Step 2: Create test presentation
    print("\n2. Creating Test Presentation...")
    try:
        ppt_filename = create_test_presentation()
        print(f"   [SUCCESS] Created: {ppt_filename}")
    except Exception as e:
        print(f"   [FAILED] Could not create test PPT: {e}")
        return False
    
    # Step 3: Test evaluation
    print("\n3. Testing PPT Evaluation...")
    try:
        problem_statement = """
        Develop a mobile application for rural healthcare management that connects patients 
        with healthcare providers, manages medical records, and provides telemedicine 
        capabilities for remote areas with limited internet connectivity.
        """
        
        print("   Sending evaluation request...")
        with open(ppt_filename, 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': 'HealthTech Innovators',
                'problem_statement': problem_statement.strip()
            }
            
            response = requests.post(
                'http://localhost:5000/api/evaluate', 
                files=files, 
                data=data, 
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                evaluation_id = result.get('evaluation_id', '')
                print(f"   [SUCCESS] Evaluation completed!")
                print(f"   Evaluation ID: {evaluation_id}")
                
                # Display results
                show_results(result)
                
                return True
            else:
                print(f"   [FAILED] Evaluation failed: {response.status_code}")
                error_text = response.text[:500]  # Limit error text
                print(f"   Response: {error_text}")
                return False
                
    except Exception as e:
        print(f"   [FAILED] Evaluation error: {e}")
        return False
    finally:
        # Clean up
        if os.path.exists(ppt_filename):
            os.remove(ppt_filename)
            print(f"\n   Cleaned up: {ppt_filename}")

def show_results(result):
    """Display evaluation results"""
    final_score = result.get('results', {}).get('final_score', {})
    
    print(f"\n" + "="*50)
    print(f"EVALUATION RESULTS")
    print(f"="*50)
    print(f"Team: {result.get('results', {}).get('team_name', 'N/A')}")
    print(f"Final Score: {final_score.get('percentage_score', 0):.2f}%")
    print(f"Grade: {final_score.get('grade', 'N/A')}")
    
    # Component scores
    component_scores = final_score.get('component_scores', {})
    print(f"\nComponent Scores:")
    print(f"{'Component':<20} {'Score':<10}")
    print(f"{'-'*30}")
    
    for component, score in component_scores.items():
        component_name = component.replace('_', ' ').title()
        print(f"{component_name:<20} {score:.3f}")
    
    # Strengths and weaknesses
    strengths = final_score.get('strengths', [])
    weaknesses = final_score.get('weaknesses', [])
    
    if strengths:
        print(f"\nStrengths:")
        for i, strength in enumerate(strengths[:3], 1):
            print(f"  {i}. {strength}")
    
    if weaknesses:
        print(f"\nAreas for Improvement:")
        for i, weakness in enumerate(weaknesses[:3], 1):
            print(f"  {i}. {weakness}")
    
    # Top recommendations
    recommendations = final_score.get('recommendations', [])
    if recommendations:
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")

if __name__ == "__main__":
    print("Starting PPT Evaluator Test...")
    success = simple_test()
    
    print("\n" + "="*60)
    if success:
        print("SUCCESS! All tests passed. System is working correctly.")
        print("\nWhat you can do next:")
        print("- Test with your own PPT files using: python test_with_ppt.py")
        print("- Run batch evaluations using: python run_evaluation.py")
        print("- Access the API directly at: http://localhost:5000")
    else:
        print("FAILED! Some tests failed. Check error messages above.")
    print("="*60)