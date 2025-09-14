import requests
import json
import os
import csv
from datetime import datetime

def batch_test_presentations():
    """Test multiple presentations with different problem statements"""
    print("="*60)
    print("BATCH PPT EVALUATION TEST")
    print("="*60)
    
    # Define test configurations
    test_configs = [
        {
            "name": "Healthcare Mobile App",
            "problem_statement": """
            Develop a mobile application for rural healthcare management that connects patients 
            with healthcare providers, manages medical records, and provides telemedicine 
            capabilities for remote areas with limited internet connectivity.
            """
        },
        {
            "name": "Legal Services Platform", 
            "problem_statement": """
            INCENTIVES BASED DESIGN FOR ONBOARDING LEGAL SERVICE PROVIDERS
            Create a digital platform that incentivizes legal professionals to join and actively 
            participate in providing legal services to underserved communities.
            """
        },
        {
            "name": "Agricultural Monitoring",
            "problem_statement": """
            Develop an AI-powered agricultural monitoring system using drones and IoT sensors 
            to help farmers optimize crop yield, monitor plant health, and predict weather-related risks.
            """
        },
        {
            "name": "Smart Traffic Management",
            "problem_statement": """
            Build a traffic management system that uses computer vision and AI to optimize 
            traffic flow, reduce congestion in urban areas, and improve overall transportation efficiency.
            """
        },
        {
            "name": "Waste Management IoT",
            "problem_statement": """
            Build a smart waste management solution for urban areas that uses IoT sensors 
            to optimize waste collection routes, reduce environmental impact, and improve efficiency.
            """
        }
    ]
    
    # Get folder containing PPT files
    folder_path = input("Enter folder path containing PPT files: ").strip().strip('"')
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found - {folder_path}")
        return False
    
    # Find PPT files
    ppt_files = []
    for file in os.listdir(folder_path):
        if file.lower().endswith(('.ppt', '.pptx')):
            ppt_files.append(os.path.join(folder_path, file))
    
    if not ppt_files:
        print("No PPT files found in the specified folder.")
        return False
    
    print(f"\nFound {len(ppt_files)} PPT files:")
    for i, file in enumerate(ppt_files, 1):
        print(f"  {i}. {os.path.basename(file)}")
    
    # Choose test mode
    print(f"\nChoose evaluation mode:")
    print("1. Use same problem statement for all presentations")
    print("2. Assign different problem statements to each presentation")
    print("3. Manually assign problem statements")
    
    mode = input("Enter choice (1-3): ").strip()
    
    results = []
    
    if mode == "1":
        # Single PS for all
        print(f"\nAvailable problem statements:")
        for i, config in enumerate(test_configs, 1):
            print(f"  {i}. {config['name']}")
        
        ps_choice = input("Choose problem statement (1-5): ").strip()
        try:
            ps_index = int(ps_choice) - 1
            selected_ps = test_configs[ps_index]["problem_statement"]
        except:
            selected_ps = test_configs[0]["problem_statement"]
        
        for ppt_file in ppt_files:
            team_name = os.path.splitext(os.path.basename(ppt_file))[0]
            result = evaluate_presentation(ppt_file, team_name, selected_ps)
            if result:
                results.append(result)
    
    elif mode == "2":
        # Cycle through different PS
        for i, ppt_file in enumerate(ppt_files):
            team_name = os.path.splitext(os.path.basename(ppt_file))[0]
            config = test_configs[i % len(test_configs)]
            print(f"\nEvaluating {team_name} with {config['name']} problem statement")
            
            result = evaluate_presentation(ppt_file, team_name, config["problem_statement"])
            if result:
                result['problem_category'] = config['name']
                results.append(result)
    
    elif mode == "3":
        # Manual assignment
        for ppt_file in ppt_files:
            team_name = os.path.splitext(os.path.basename(ppt_file))[0]
            print(f"\nAssigning problem statement for: {team_name}")
            print("Available problem statements:")
            for i, config in enumerate(test_configs, 1):
                print(f"  {i}. {config['name']}")
            
            ps_choice = input("Choose problem statement (1-5): ").strip()
            try:
                ps_index = int(ps_choice) - 1
                selected_config = test_configs[ps_index]
            except:
                selected_config = test_configs[0]
            
            result = evaluate_presentation(ppt_file, team_name, selected_config["problem_statement"])
            if result:
                result['problem_category'] = selected_config['name']
                results.append(result)
    
    # Generate report
    if results:
        generate_batch_report(results)
        return True
    else:
        print("No successful evaluations completed.")
        return False

def evaluate_presentation(ppt_file, team_name, problem_statement):
    """Evaluate a single presentation"""
    try:
        print(f"  Evaluating: {os.path.basename(ppt_file)}")
        
        with open(ppt_file, 'rb') as f:
            files = {'file': f}
            data = {
                'team_name': team_name,
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
                
                # Extract key metrics
                final_score = result.get('results', {}).get('final_score', {})
                component_scores = final_score.get('component_scores', {})
                
                evaluation_result = {
                    'team_name': team_name,
                    'file_name': os.path.basename(ppt_file),
                    'evaluation_id': result.get('evaluation_id', ''),
                    'final_score': final_score.get('percentage_score', 0),
                    'grade': final_score.get('grade', ''),
                    'ps_similarity': component_scores.get('ps_similarity', 0),
                    'feasibility': component_scores.get('feasibility', 0),
                    'attractiveness': component_scores.get('attractiveness', 0),
                    'image_analysis': component_scores.get('image_analysis', 0),
                    'link_analysis': component_scores.get('link_analysis', 0),
                    'llm_penalty': component_scores.get('llm_penalty', 0),
                    'strengths': len(final_score.get('strengths', [])),
                    'weaknesses': len(final_score.get('weaknesses', [])),
                    'timestamp': datetime.now().isoformat()
                }
                
                print(f"    ✓ Score: {evaluation_result['final_score']:.2f}% (Grade: {evaluation_result['grade']})")
                return evaluation_result
            else:
                print(f"    ✗ Failed: {response.status_code}")
                return None
                
    except Exception as e:
        print(f"    ✗ Error: {str(e)}")
        return None

def generate_batch_report(results):
    """Generate comprehensive batch evaluation report"""
    
    # Sort by score
    results.sort(key=lambda x: x['final_score'], reverse=True)
    
    # Generate CSV report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"batch_evaluation_report_{timestamp}.csv"
    
    csv_fields = [
        'rank', 'team_name', 'file_name', 'final_score', 'grade',
        'ps_similarity', 'feasibility', 'attractiveness', 'image_analysis',
        'link_analysis', 'llm_penalty', 'strengths', 'weaknesses',
        'problem_category', 'evaluation_id', 'timestamp'
    ]
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fields)
        writer.writeheader()
        
        for i, result in enumerate(results, 1):
            result['rank'] = i
            writer.writerow(result)
    
    # Display summary
    print(f"\n" + "="*80)
    print("BATCH EVALUATION SUMMARY")
    print("="*80)
    print(f"Total Presentations Evaluated: {len(results)}")
    print(f"Average Score: {sum(r['final_score'] for r in results) / len(results):.2f}%")
    print(f"Highest Score: {results[0]['final_score']:.2f}% ({results[0]['team_name']})")
    print(f"Lowest Score: {results[-1]['final_score']:.2f}% ({results[-1]['team_name']})")
    
    # Grade distribution
    grades = {}
    for result in results:
        grade = result['grade']
        grades[grade] = grades.get(grade, 0) + 1
    
    print(f"\nGrade Distribution:")
    for grade in ['A+', 'A', 'B+', 'B', 'C', 'D']:
        count = grades.get(grade, 0)
        if count > 0:
            print(f"  {grade}: {count} teams ({count/len(results)*100:.1f}%)")
    
    # Top 10 rankings
    print(f"\nTOP 10 RANKINGS:")
    print(f"{'Rank':<6} {'Team':<25} {'Score':<8} {'Grade':<6} {'File'}")
    print(f"{'-'*70}")
    
    for i, result in enumerate(results[:10], 1):
        print(f"{i:<6} {result['team_name'][:24]:<25} {result['final_score']:<8.2f} {result['grade']:<6} {result['file_name']}")
    
    # Component analysis
    print(f"\nCOMPONENT AVERAGES:")
    components = ['ps_similarity', 'feasibility', 'attractiveness', 'image_analysis', 'link_analysis']
    for comp in components:
        avg = sum(r[comp] for r in results) / len(results)
        print(f"  {comp.replace('_', ' ').title()}: {avg:.3f}")
    
    print(f"\nDetailed results saved to: {csv_filename}")
    print("="*80)

if __name__ == "__main__":
    try:
        success = batch_test_presentations()
        if success:
            print("\n🎉 Batch evaluation completed successfully!")
        else:
            print("\n❌ Batch evaluation failed.")
    except KeyboardInterrupt:
        print("\n\nBatch evaluation interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")