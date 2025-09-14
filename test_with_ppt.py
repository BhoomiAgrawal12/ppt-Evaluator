import requests
import json

def test_with_ppt_file(ppt_file_path, custom_problem_statement=None, custom_team_name=None):
    """Test evaluation with a real PPT file"""
    print(f"Testing with PPT file: {ppt_file_path}")
    
    try:
        # Use custom problem statement or ask user for input
        if custom_problem_statement:
            problem_statement = custom_problem_statement
        else:
            print("\nPlease enter the problem statement for this presentation:")
            print("(Press Enter twice to finish)")
            lines = []
            while True:
                line = input()
                if line == "" and lines:  # Empty line and we have some content
                    break
                lines.append(line)
            problem_statement = "\n".join(lines).strip()
            
            if not problem_statement:
                print("No problem statement provided. Using default...")
                problem_statement = "Generic problem statement for testing purposes."
        
        # Use custom team name or extract from filename
        if custom_team_name:
            team_name = custom_team_name
        else:
            team_name = input("Enter team name (or press Enter to use filename): ").strip()
            if not team_name:
                import os
                team_name = os.path.splitext(os.path.basename(ppt_file_path))[0]
        
        print(f"\nEvaluating with:")
        print(f"Team Name: {team_name}")
        print(f"Problem Statement: {problem_statement[:100]}{'...' if len(problem_statement) > 100 else ''}")
        
        with open(ppt_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': team_name,
                'problem_statement': problem_statement.strip()
            }
            
            print("Sending evaluation request...")
            response = requests.post('http://localhost:5000/api/evaluate', files=files, data=data, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Evaluation completed successfully!")
                
                # Extract and display results
                evaluation_id = result.get('evaluation_id', '')
                final_score = result.get('results', {}).get('final_score', {})
                
                print(f"\n{'='*50}")
                print(f"EVALUATION RESULTS")
                print(f"{'='*50}")
                print(f"Evaluation ID: {evaluation_id}")
                print(f"Team Name: {result.get('results', {}).get('team_name', 'N/A')}")
                print(f"Final Score: {final_score.get('percentage_score', 0):.2f}%")
                print(f"Grade: {final_score.get('grade', 'N/A')}")
                
                # Component scores
                component_scores = final_score.get('component_scores', {})
                print(f"\n📊 COMPONENT SCORES:")
                print(f"{'Component':<25} {'Score':<10} {'Description'}")
                print(f"{'-'*50}")
                
                component_names = {
                    'ps_similarity': 'PS Similarity',
                    'feasibility': 'Feasibility', 
                    'attractiveness': 'Attractiveness',
                    'image_analysis': 'Image Analysis',
                    'link_analysis': 'Link Analysis',
                    'llm_penalty': 'LLM Penalty'
                }
                
                for component, score in component_scores.items():
                    name = component_names.get(component, component)
                    print(f"{name:<25} {score:.3f}")
                
                # Strengths and Weaknesses
                strengths = final_score.get('strengths', [])
                weaknesses = final_score.get('weaknesses', [])
                
                if strengths:
                    print(f"\n💪 STRENGTHS:")
                    for strength in strengths:
                        print(f"  • {strength}")
                
                if weaknesses:
                    print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
                    for weakness in weaknesses:
                        print(f"  • {weakness}")
                
                # Recommendations
                recommendations = final_score.get('recommendations', [])
                if recommendations:
                    print(f"\n💡 RECOMMENDATIONS:")
                    for i, rec in enumerate(recommendations[:5], 1):
                        print(f"  {i}. {rec}")
                
                return True
            else:
                print(f"✗ Evaluation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except FileNotFoundError:
        print(f"✗ File not found: {ppt_file_path}")
        print("Please provide a valid PPT/PPTX file path")
        return False
    except Exception as e:
        print(f"✗ Error during evaluation: {e}")
        return False

if __name__ == "__main__":
    # Replace with your actual PPT file path
    ppt_file = input("Enter the path to your PPT/PPTX file: ").strip().strip('"')
    test_with_ppt_file(ppt_file)