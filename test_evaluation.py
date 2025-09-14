import requests
import json

def test_evaluation():
    """Test the PPT evaluation endpoint"""
    print("Testing PPT evaluation...")
    
    try:
        # Test data
        problem_statement = """
        Develop a mobile application for rural healthcare management that connects patients 
        with healthcare providers, manages medical records, and provides telemedicine 
        capabilities for remote areas with limited internet connectivity.
        """
        
        # Read test file
        with open('test_presentation.txt', 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': 'TestTeam',
                'problem_statement': problem_statement.strip()
            }
            
            print("Sending evaluation request...")
            response = requests.post('http://localhost:5000/api/evaluate', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("Evaluation completed successfully!")
                
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
                
                # Print some recommendations
                recommendations = final_score.get('recommendations', [])
                if recommendations:
                    print(f"\nTop Recommendations:")
                    for i, rec in enumerate(recommendations[:3]):
                        print(f"  {i+1}. {rec}")
                
                return True
            else:
                print(f"Evaluation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return False

if __name__ == "__main__":
    test_evaluation()