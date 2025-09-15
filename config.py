import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LlamaParse Configuration
    LLAMA_CLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')

    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///evaluations.db')
    
    # API Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'ppt', 'pptx', 'pdf'}
    
    # LLM Evaluation Configuration
    GEMINI_MODEL = 'gemini-1.5-flash'
    LLM_EVALUATION_TIMEOUT = 60  # seconds
    MAX_RETRY_ATTEMPTS = 3
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'evaluator.log')