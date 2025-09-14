import requests
import json
import os

def interactive_ppt_test():
    """Interactive PPT testing with custom inputs"""
    print("="*60)
    print("INTERACTIVE PPT EVALUATOR TEST")
    print("="*60)
    
    # Get PPT file path
    ppt_file = input("\nEnter the path to your PPT/PPTX file: ").strip().strip('"')
    
    if not os.path.exists(ppt_file):
        print(f"Error: File not found - {ppt_file}")
        return False
    
    if not ppt_file.lower().endswith(('.ppt', '.pptx')):
        print("Warning: File doesn't appear to be a PowerPoint file")
        proceed = input("Continue anyway? (y/n): ").lower()
        if proceed != 'y':
            return False
    
    # Get team name
    default_team = os.path.splitext(os.path.basename(ppt_file))[0]
    team_name = input(f"\nEnter team name (default: {default_team}): ").strip()
    if not team_name:
        team_name = default_team
    
    # Get problem statement
    print(f"\nChoose problem statement option:")
    print("1. Enter custom problem statement")
    print("2. Use sample healthcare problem statement")
    print("3. Use sample legal services problem statement")
    print("4. Use sample agricultural problem statement")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        print("\nEnter the problem statement (press Enter twice to finish):")
        lines = []
        empty_count = 0
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2 or (empty_count >= 1 and lines):
                    break
            else:
                empty_count = 0
                lines.append(line)
        problem_statement = "\n".join(lines).strip()
    
    elif choice == "2":
        problem_statement = """
        Develop a mobile application for rural healthcare management that connects patients 
        with healthcare providers, manages medical records, and provides telemedicine 
        capabilities for remote areas with limited internet connectivity. The solution 
        should be scalable, secure, and work offline when needed.
        """
    
    elif choice == "3":
        problem_statement = """
        INCENTIVES BASED DESIGN FOR ONBOARDING LEGAL SERVICE PROVIDERS
        Create a digital platform that incentivizes legal professionals to join and actively 
        participate in providing legal services to underserved communities. The system should 
        include gamification, rewards, and performance tracking mechanisms.
        """
    
    elif choice == "4":
        problem_statement = """
        Develop an AI-powered agricultural monitoring system using drones and IoT sensors 
        to help farmers optimize crop yield, monitor plant health, predict weather-related 
        risks, and provide actionable insights for sustainable farming practices.
        """
    
    else:
        print("Invalid choice. Using generic problem statement.")
        problem_statement = "Generic problem statement for testing purposes."
    
    # Display summary
    print(f"\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"File: {os.path.basename(ppt_file)}")
    print(f"Team: {team_name}")
    print(f"Problem Statement: {problem_statement[:100]}{'...' if len(problem_statement) > 100 else ''}")
    
    confirm = input(f"\nProceed with evaluation? (y/n): ").lower()
    if confirm != 'y':
        print("Evaluation cancelled.")
        return False
    
    # Run evaluation
    return run_evaluation(ppt_file, team_name, problem_statement)

def run_evaluation(ppt_file_path, team_name, problem_statement):
    """Run the actual evaluation"""
    try:
        print(f"\nSending evaluation request...")
        print("This may take a few minutes depending on file size...")
        
        with open(ppt_file_path, 'rb') as f:
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
                display_detailed_results(result)
                return True
            else:
                print(f"Evaluation failed: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except FileNotFoundError:
        print(f"File not found: {ppt_file_path}")
        return False
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return False

def display_detailed_results(result):
    """Display comprehensive evaluation results"""
    print(f"\n" + "="*80)
    print("DETAILED EVALUATION RESULTS")
    print("="*80)
    
    # Basic info
    team_name = result.get('results', {}).get('team_name', 'N/A')
    evaluation_id = result.get('evaluation_id', '')
    final_score = result.get('results', {}).get('final_score', {})
    
    print(f"Evaluation ID: {evaluation_id}")
    print(f"Team Name: {team_name}")
    print(f"Final Score: {final_score.get('percentage_score', 0):.2f}%")
    print(f"Grade: {final_score.get('grade', 'N/A')}")
    
    # Component scores breakdown
    component_scores = final_score.get('component_scores', {})
    print(f"\n📊 COMPONENT SCORES BREAKDOWN:")
    print(f"{'Component':<25} {'Raw Score':<12} {'Weight':<10} {'Description'}")
    print(f"{'-'*70}")
    
    component_info = {
        'ps_similarity': ('Problem Statement Similarity', '25%'),
        'feasibility': ('Technical Feasibility', '20%'),
        'attractiveness': ('Visual Attractiveness', '15%'),
        'image_analysis': ('Image/Diagram Analysis', '15%'),
        'link_analysis': ('Supporting Links Quality', '10%'),
        'llm_penalty': ('LLM Detection Penalty', '-15%')
    }
    
    for component, score in component_scores.items():
        name, weight = component_info.get(component, (component, 'N/A'))
        print(f"{name:<25} {score:<12.3f} {weight:<10}")
    
    # Detailed breakdown
    score_breakdown = final_score.get('score_breakdown', {})
    if score_breakdown:
        print(f"\n📈 SCORE BREAKDOWN:")
        components = score_breakdown.get('components', {})
        for comp_name, comp_data in components.items():
            if isinstance(comp_data, dict):
                contribution = comp_data.get('contribution', 0)
                print(f"  {comp_name.replace('_', ' ').title()}: {contribution:.1f}% contribution to final score")
    
    # Strengths
    strengths = final_score.get('strengths', [])
    if strengths:
        print(f"\n💪 KEY STRENGTHS:")
        for i, strength in enumerate(strengths, 1):
            print(f"  {i}. {strength}")
    
    # Weaknesses
    weaknesses = final_score.get('weaknesses', [])
    if weaknesses:
        print(f"\n⚠️  AREAS FOR IMPROVEMENT:")
        for i, weakness in enumerate(weaknesses, 1):
            print(f"  {i}. {weakness}")
    
    # Recommendations
    recommendations = final_score.get('recommendations', [])
    if recommendations:
        print(f"\n💡 ACTIONABLE RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:8], 1):
            print(f"  {i}. {rec}")
    
    # Overall assessment
    overall_assessment = final_score.get('overall_assessment', '')
    if overall_assessment:
        print(f"\n📝 OVERALL ASSESSMENT:")
        print(f"  {overall_assessment}")
    
    # Performance ranking
    ranking_factors = final_score.get('ranking_factors', {})
    if ranking_factors:
        print(f"\n🏆 PERFORMANCE RANKING FACTORS:")
        for factor, score in ranking_factors.items():
            factor_name = factor.replace('_', ' ').title()
            print(f"  {factor_name}: {score:.3f}")
    
    print(f"\n" + "="*80)
    print(f"Evaluation completed! Results saved with ID: {result.get('evaluation_id', 'N/A')}")
    print("="*80)

if __name__ == "__main__":
    try:
        success = interactive_ppt_test()
        if success:
            print("\n🎉 Evaluation completed successfully!")
            print("\nNext steps:")
            print("- Review the detailed results above")
            print("- Use the evaluation ID to retrieve results later")
            print("- Compare with other presentations using rankings API")
        else:
            print("\n❌ Evaluation failed or was cancelled.")
    except KeyboardInterrupt:
        print("\n\nEvaluation interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")