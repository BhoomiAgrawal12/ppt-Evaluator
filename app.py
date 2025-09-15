from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
import logging

from evaluator.ppt_parser import DocumentParser
from evaluator.llm_evaluator import LLMEvaluator
import requests
import json
from database.db_manager import DatabaseManager

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'ppt', 'pptx', 'pdf'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
document_parser = DocumentParser()
llm_evaluator = LLMEvaluator()
db_manager = DatabaseManager()

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('evaluator.log')  # File output
    ]
)
logger = logging.getLogger(__name__)

# Enable debug logging for Flask
app.config['DEBUG'] = True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']




@app.route('/')
def index():
    logger.info("Serving main index page")
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return '', 204  # No content


@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error for path: {request.path}")
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/api/status')
def api_status():
    return jsonify({
        "message": "SIH Presentation Evaluator - LLM Edition",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "Multi-format document parsing (PPT/PPTX/PDF)",
            "AI content detection using transformer models",
            "Complete LLM-based evaluation using Google Gemini",
            "Intelligent assessment across multiple criteria",
            "No statistical word-based scoring"
        ],
        "evaluation_criteria": [
            "Technical Feasibility",
            "Problem Statement Alignment",
            "Solution Quality",
            "Presentation Quality",
            "Innovation & Creativity"
        ]
    })


@app.route('/api/evaluate', methods=['POST'])
def evaluate_ppt():
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] === NEW EVALUATION REQUEST ===")

    try:
        # Log request details
        logger.info(f"[{request_id}] Request method: {request.method}")
        logger.info(f"[{request_id}] Request URL: {request.url}")
        logger.info(f"[{request_id}] Request headers: {dict(request.headers)}")
        logger.info(f"[{request_id}] Form data keys: {list(request.form.keys())}")
        logger.info(f"[{request_id}] Files in request: {list(request.files.keys())}")

        # Check if file is present
        if 'file' not in request.files:
            logger.error(f"[{request_id}] ERROR: No file provided in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        problem_statement = request.form.get('problem_statement', '')
        team_name = request.form.get('team_name', '')

        logger.info(f"[{request_id}] File name: {file.filename}")
        logger.info(f"[{request_id}] Team name: {team_name}")
        logger.info(f"[{request_id}] Problem statement length: {len(problem_statement)} chars")

        if file.filename == '':
            logger.error(f"[{request_id}] ERROR: No file selected")
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            logger.error(f"[{request_id}] ERROR: Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Only PPT/PPTX/PDF allowed'}), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_id}_{filename}")

        logger.info(f"[{request_id}] Saving file to: {file_path}")
        file.save(file_path)

        # Check file was saved successfully
        file_size = os.path.getsize(file_path)
        logger.info(f"[{request_id}] File saved successfully. Size: {file_size} bytes")

        logger.info(f"[{request_id}] Processing file: {filename} for team: {team_name}")

        # Start LLM-based evaluation pipeline
        logger.info(f"[{request_id}] Starting LLM evaluation pipeline...")
        evaluation_results = evaluate_presentation_llm(file_path, problem_statement, team_name)
        logger.info(f"[{request_id}] LLM evaluation completed successfully")

        # Store results in database
        logger.info(f"[{request_id}] Storing results in database...")
        evaluation_id = db_manager.store_evaluation(evaluation_results)
        logger.info(f"[{request_id}] Results stored with ID: {evaluation_id}")

        # Clean up uploaded file
        logger.info(f"[{request_id}] Cleaning up uploaded file...")
        os.remove(file_path)
        logger.info(f"[{request_id}] File cleanup completed")

        logger.info(f"[{request_id}] === EVALUATION REQUEST COMPLETED SUCCESSFULLY ===")

        return jsonify({
            'evaluation_id': evaluation_id,
            **evaluation_results  # Return results directly
        })

    except Exception as e:
        logger.error(f"[{request_id}] ERROR: Exception during evaluation: {str(e)}")
        logger.error(f"[{request_id}] Exception type: {type(e).__name__}")

        # Log stack trace
        import traceback
        logger.error(f"[{request_id}] Stack trace:\n{traceback.format_exc()}")

        return jsonify({'error': f'Internal server error: {str(e)}'}), 500


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




def evaluate_presentation_llm(file_path, problem_statement, team_name):
    """
    LLM-based evaluation pipeline for presentations
    """
    try:
        logger.info(f"Starting LLM-based evaluation for {team_name}")

        # Step 1: Parse Document (PPT, PPTX or PDF)
        logger.info("Step 1: Parsing Document")
        parsed_content = document_parser.parse_document(file_path)

        # Step 2: Run complete LLM evaluation
        logger.info("Step 2: Running LLM evaluation")
        evaluation_results = llm_evaluator.evaluate_presentation(
            parsed_content, problem_statement, team_name
        )

        # Add parsing metadata
        evaluation_results['parsing_info'] = {
            'total_slides': len(parsed_content.get('slides', [])),
            'total_images': len(parsed_content.get('images', [])),
            'total_links': len(parsed_content.get('links', [])),
            'text_length': len(parsed_content.get('text', ''))
        }

        logger.info(f"LLM evaluation completed for {team_name}")
        return evaluation_results

    except Exception as e:
        logger.error(f"Error in LLM evaluation pipeline: {str(e)}")
        return {
            'team_name': team_name,
            'problem_statement': problem_statement,
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'final_assessment': {
                'overall_score': 0.0,
                'grade': 'F',
                'summary': f'Evaluation failed: {str(e)}'
            }
        }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)