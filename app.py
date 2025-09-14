from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import logging

from evaluator.ppt_parser import PPTParser
from evaluator.content_detector import ContentDetector
from evaluator.similarity_evaluator import SimilarityEvaluator
from evaluator.feasibility_calculator import FeasibilityCalculator
from evaluator.link_parser import LinkParser
from evaluator.attractiveness_evaluator import AttractivenessEvaluator
from evaluator.image_analyzer import ImageAnalyzer
from evaluator.scoring_system import ScoringSystem
from database.db_manager import DatabaseManager

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'ppt', 'pptx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
ppt_parser = PPTParser()
content_detector = ContentDetector()
similarity_evaluator = SimilarityEvaluator()
feasibility_calculator = FeasibilityCalculator()
link_parser = LinkParser()
attractiveness_evaluator = AttractivenessEvaluator()
image_analyzer = ImageAnalyzer()
scoring_system = ScoringSystem()
db_manager = DatabaseManager()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    return jsonify({
        "message": "SIH PPT Evaluator API",
        "version": "1.0.0",
        "status": "running"
    })


@app.route('/api/evaluate', methods=['POST'])
def evaluate_ppt():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        problem_statement = request.form.get('problem_statement', '')
        team_name = request.form.get('team_name', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only PPT/PPTX allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")
        file.save(file_path)
        
        logger.info(f"Processing file: {filename} for team: {team_name}")
        
        # Start evaluation pipeline
        evaluation_results = evaluate_presentation(file_path, problem_statement, team_name)
        
        # Store results in database
        evaluation_id = db_manager.store_evaluation(evaluation_results)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        return jsonify({
            'evaluation_id': evaluation_id,
            'results': evaluation_results
        })
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/evaluations/<evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    try:
        evaluation = db_manager.get_evaluation(evaluation_id)
        if not evaluation:
            return jsonify({'error': 'Evaluation not found'}), 404
        return jsonify(evaluation)
    except Exception as e:
        logger.error(f"Error retrieving evaluation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/evaluations', methods=['GET'])
def get_all_evaluations():
    try:
        evaluations = db_manager.get_all_evaluations()
        return jsonify(evaluations)
    except Exception as e:
        logger.error(f"Error retrieving evaluations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/rankings/<problem_statement_id>', methods=['GET'])
def get_rankings(problem_statement_id):
    try:
        rankings = db_manager.get_rankings_by_ps(problem_statement_id)
        return jsonify(rankings)
    except Exception as e:
        logger.error(f"Error retrieving rankings: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def evaluate_presentation(file_path, problem_statement, team_name):
    """
    Complete evaluation pipeline for a PPT presentation
    """
    results = {
        'team_name': team_name,
        'problem_statement': problem_statement,
        'timestamp': datetime.now().isoformat(),
        'file_path': file_path,
        'evaluation': {}
    }
    
    try:
        # Step 1: Parse PPT
        logger.info("Step 1: Parsing PPT")
        parsed_content = ppt_parser.parse_ppt(file_path)
        results['evaluation']['parsed_content'] = parsed_content
        
        # Step 2: Check for LLM-generated content
        logger.info("Step 2: Detecting LLM-generated content")
        llm_detection = content_detector.detect_llm_content(parsed_content['text'])
        results['evaluation']['llm_detection'] = llm_detection
        
        # Step 3: Evaluate similarity to problem statement
        logger.info("Step 3: Evaluating PS similarity")
        similarity_score = similarity_evaluator.evaluate_similarity(
            parsed_content['text'], problem_statement
        )
        results['evaluation']['ps_similarity'] = similarity_score
        
        # Step 4: Calculate feasibility
        logger.info("Step 4: Calculating feasibility")
        feasibility_score = feasibility_calculator.calculate_feasibility(parsed_content)
        results['evaluation']['feasibility'] = feasibility_score
        
        # Step 5: Parse and validate links
        logger.info("Step 5: Parsing links")
        link_analysis = link_parser.analyze_links(parsed_content['links'])
        results['evaluation']['link_analysis'] = link_analysis
        
        # Step 6: Evaluate attractiveness
        logger.info("Step 6: Evaluating attractiveness")
        attractiveness_score = attractiveness_evaluator.evaluate_attractiveness(parsed_content)
        results['evaluation']['attractiveness'] = attractiveness_score
        
        # Step 7: Analyze images and diagrams
        logger.info("Step 7: Analyzing images")
        image_analysis = image_analyzer.analyze_images(parsed_content['images'])
        results['evaluation']['image_analysis'] = image_analysis
        
        # Step 8: Calculate final score
        logger.info("Step 8: Calculating final score")
        final_score = scoring_system.calculate_final_score(results['evaluation'])
        results['final_score'] = final_score
        
        logger.info(f"Evaluation completed. Final score: {final_score}")
        
    except Exception as e:
        logger.error(f"Error in evaluation pipeline: {str(e)}")
        results['error'] = str(e)
    
    return results


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)