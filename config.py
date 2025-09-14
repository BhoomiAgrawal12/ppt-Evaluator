import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LlamaParse Configuration
    LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///evaluations.db')
    
    # API Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'ppt', 'pptx'}
    
    # Evaluation Thresholds
    SIMILARITY_THRESHOLD = 0.7
    FEASIBILITY_THRESHOLD = 0.6
    ATTRACTIVENESS_THRESHOLD = 0.5
    LLM_DETECTION_THRESHOLD = 0.8
    
    # Scoring Weights
    SCORING_WEIGHTS = {
        'ps_similarity': 0.25,
        'feasibility': 0.20,
        'attractiveness': 0.15,
        'image_analysis': 0.15,
        'link_analysis': 0.10,
        'llm_penalty': -0.15  # Penalty for LLM-generated content
    }
    
    # Model Configuration
    SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'
    LLM_DETECTION_MODEL = 'Hello-SimpleAI/chatgpt-detector-roberta'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'evaluator.log')