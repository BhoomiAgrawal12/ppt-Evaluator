#!/usr/bin/env python3
"""
Batch evaluation script for processing multiple PPT files
Usage: python run_evaluation.py --folder presentations/ --ps-file problem_statements.json
"""

import os
import sys
import json
import argparse
import requests
import pandas as pd
from pathlib import Path
import time
from datetime import datetime

def load_problem_statements(ps_file_path):
    """Load problem statements from JSON file"""
    try:
        with open(ps_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading problem statements: {e}")
        return {}

def evaluate_single_presentation(api_url, file_path, problem_statement, team_name):
    """Evaluate a single presentation"""
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'problem_statement': problem_statement,
                'team_name': team_name
            }
            
            response = requests.post(f"{api_url}/api/evaluate", files=files, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error evaluating {file_path}: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"Exception evaluating {file_path}: {e}")
        return None

def batch_evaluate(folder_path, problem_statements, api_url="http://localhost:5000"):
    """Batch evaluate all presentations in a folder"""
    results = []
    total_files = 0
    processed_files = 0
    
    # Count total files
    for file_path in Path(folder_path).glob("*.ppt*"):
        total_files += 1
    
    print(f"Found {total_files} presentation files")
    
    for file_path in Path(folder_path).glob("*.ppt*"):
        filename = file_path.name
        team_name = file_path.stem  # Filename without extension
        
        # Get problem statement for this team
        problem_statement = problem_statements.get(team_name, "")
        
        if not problem_statement:
            print(f"Warning: No problem statement found for team '{team_name}'")
            continue
        
        print(f"Processing {filename} ({processed_files + 1}/{total_files})...")
        
        # Evaluate presentation
        result = evaluate_single_presentation(api_url, file_path, problem_statement, team_name)
        
        if result:
            final_score = result.get('results', {}).get('final_score', {})
            results.append({
                'team_name': team_name,
                'filename': filename,
                'evaluation_id': result.get('evaluation_id', ''),
                'percentage_score': final_score.get('percentage_score', 0),
                'normalized_score': final_score.get('normalized_score', 0),
                'grade': final_score.get('grade', ''),
                'ps_similarity': final_score.get('component_scores', {}).get('ps_similarity', 0),
                'feasibility': final_score.get('component_scores', {}).get('feasibility', 0),
                'attractiveness': final_score.get('component_scores', {}).get('attractiveness', 0),
                'image_analysis': final_score.get('component_scores', {}).get('image_analysis', 0),
                'link_analysis': final_score.get('component_scores', {}).get('link_analysis', 0),
                'llm_penalty': final_score.get('component_scores', {}).get('llm_penalty', 0),
                'timestamp': datetime.now().isoformat()
            })
        
        processed_files += 1
        
        # Small delay to avoid overwhelming the API
        time.sleep(1)
    
    return results

def export_results(results, output_file="evaluation_results.csv"):
    """Export results to CSV"""
    if results:
        df = pd.DataFrame(results)
        df = df.sort_values('percentage_score', ascending=False)
        df.to_csv(output_file, index=False)
        print(f"Results exported to {output_file}")
        
        # Print summary
        print("\n=== EVALUATION SUMMARY ===")
        print(f"Total presentations evaluated: {len(results)}")
        print(f"Average score: {df['percentage_score'].mean():.2f}%")
        print(f"Highest score: {df['percentage_score'].max():.2f}% ({df.loc[df['percentage_score'].idxmax(), 'team_name']})")
        print(f"Lowest score: {df['percentage_score'].min():.2f}% ({df.loc[df['percentage_score'].idxmin(), 'team_name']})")
        
        print("\n=== TOP 10 TEAMS ===")
        top_10 = df.head(10)
        for i, row in top_10.iterrows():
            print(f"{row.name + 1:2d}. {row['team_name']:20s} - {row['percentage_score']:6.2f}% ({row['grade']})")
        
        print("\n=== GRADE DISTRIBUTION ===")
        grade_counts = df['grade'].value_counts()
        for grade, count in grade_counts.items():
            print(f"{grade}: {count} teams ({count/len(results)*100:.1f}%)")
    
    else:
        print("No results to export")

def main():
    parser = argparse.ArgumentParser(description="Batch evaluate PPT presentations")
    parser.add_argument("--folder", required=True, help="Folder containing PPT files")
    parser.add_argument("--ps-file", required=True, help="JSON file containing problem statements")
    parser.add_argument("--api-url", default="http://localhost:5000", help="API base URL")
    parser.add_argument("--output", default="evaluation_results.csv", help="Output CSV file")
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.folder):
        print(f"Error: Folder '{args.folder}' does not exist")
        sys.exit(1)
    
    if not os.path.exists(args.ps_file):
        print(f"Error: Problem statements file '{args.ps_file}' does not exist")
        sys.exit(1)
    
    # Load problem statements
    problem_statements = load_problem_statements(args.ps_file)
    if not problem_statements:
        print("Error: No problem statements loaded")
        sys.exit(1)
    
    print(f"Loaded {len(problem_statements)} problem statements")
    
    # Check if API is running
    try:
        response = requests.get(f"{args.api_url}/")
        if response.status_code != 200:
            print(f"Error: API not responding at {args.api_url}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: Cannot connect to API at {args.api_url}: {e}")
        sys.exit(1)
    
    print("Starting batch evaluation...")
    
    # Run batch evaluation
    results = batch_evaluate(args.folder, problem_statements, args.api_url)
    
    # Export results
    export_results(results, args.output)
    
    print("Batch evaluation completed!")

if __name__ == "__main__":
    main()