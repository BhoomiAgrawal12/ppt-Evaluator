# 🎯 SIH Presentation Evaluator

An advanced AI-powered system for evaluating presentation quality using Google Gemini LLM, built for Smart India Hackathon (SIH) events. Features intelligent evaluation across multiple criteria with support for PPT, PPTX, and PDF files.

## 🎯 Overview

The SIH PPT Evaluator AI is designed to handle the evaluation of approximately 160 presentations (4 presentations per problem statement × 40 problem statements) with consistent, objective, and comprehensive assessment criteria.

## ✨ Features

### Core Components

- **🔍 PPT Parser**: Uses LlamaParse to extract content, images, and links from PowerPoint files
- **🤖 LLM Content Detector**: Identifies AI-generated content using multiple detection methods
- **📊 Similarity Evaluator**: Measures alignment between presentation content and problem statements
- **⚖️ Feasibility Calculator**: Assesses technical, resource, timeline, and budget feasibility
- **🔗 Link Parser**: Analyzes and validates embedded links (GitHub, demo videos, documentation)
- **🎨 Attractiveness Evaluator**: Evaluates visual design, layout, and presentation quality
- **🖼️ Image Analyzer**: Analyzes diagrams, flowcharts, and technical visual content
- **🎯 Scoring System**: Comprehensive weighted scoring and ranking mechanism

### Evaluation Parameters

- ✅ **LLM Generated Content Detection** - Multi-method AI content detection
- ✅ **Technical Feasibility** - Resource, timeline, and implementation assessment
- ✅ **Problem Statement Similarity** - Semantic and keyword-based alignment analysis
- ✅ **Demo Video/GitHub Links** - Link validation and quality assessment
- ✅ **Visual Attractiveness** - Design quality and presentation aesthetics
- ✅ **Diagram Analysis** - Technical depth of flowcharts and architecture diagrams
- ✅ **Comprehensive Scoring** - Weighted scoring with detailed breakdowns
- ✅ **Ranking System** - Multi-criteria ranking for fair comparison

## 🏗️ Architecture

```
EvaluatorAI/
├── app.py                          # Flask application entry point
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── evaluator/                      # Core evaluation modules
│   ├── __init__.py
│   ├── ppt_parser.py              # LlamaParse integration
│   ├── content_detector.py        # LLM content detection
│   ├── similarity_evaluator.py    # PS alignment analysis
│   ├── feasibility_calculator.py  # Feasibility assessment
│   ├── link_parser.py             # Link validation
│   ├── attractiveness_evaluator.py # Design quality assessment
│   ├── image_analyzer.py          # Image and diagram analysis
│   └── scoring_system.py          # Final scoring and ranking
├── database/                       # Database management
│   ├── __init__.py
│   └── db_manager.py              # SQLite database operations
└── uploads/                        # Temporary file storage
```

## 🚀 Installation

### Prerequisites

- Python 3.8+
- SQLite3
- OpenAI API Key (optional, for enhanced analysis)
- LlamaParse API Key

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd EvaluatorAI
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   LLAMA_CLOUD_API_KEY=your_llama_parse_api_key
   OPENAI_API_KEY=your_openai_api_key_optional
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   ```

4. **Initialize Database**
   ```bash
   python -c "from database.db_manager import DatabaseManager; DatabaseManager().init_database()"
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## 🔧 API Documentation

### Core Endpoints

#### 1. Evaluate PPT
```http
POST /api/evaluate
Content-Type: multipart/form-data

Form Data:
- file: PPT/PPTX file
- problem_statement: Problem statement text
- team_name: Team name
```

**Response:**
```json
{
  "evaluation_id": "uuid-string",
  "results": {
    "team_name": "Team Name",
    "problem_statement": "PS text",
    "timestamp": "2024-01-01T12:00:00",
    "evaluation": {
      "parsed_content": {...},
      "llm_detection": {...},
      "ps_similarity": {...},
      "feasibility": {...},
      "link_analysis": {...},
      "attractiveness": {...},
      "image_analysis": {...}
    },
    "final_score": {
      "total_score": 0.85,
      "normalized_score": 0.85,
      "percentage_score": 85.0,
      "grade": "A",
      "strengths": [...],
      "weaknesses": [...],
      "recommendations": [...]
    }
  }
}
```

#### 2. Get Evaluation
```http
GET /api/evaluations/{evaluation_id}
```

#### 3. List All Evaluations
```http
GET /api/evaluations
```

#### 4. Get Rankings by Problem Statement
```http
GET /api/rankings/{problem_statement_id}
```

## 📊 Evaluation Criteria

### Scoring Weights
- **Problem Statement Similarity**: 25%
- **Technical Feasibility**: 20%
- **Visual Attractiveness**: 15%
- **Image Analysis**: 15%
- **Link Quality**: 10%
- **LLM Detection Penalty**: -15%

### Component Details

#### 1. Problem Statement Similarity (25%)
- Semantic similarity using sentence transformers
- Keyword-based analysis with TF-IDF
- Coverage analysis of key requirements
- Relevance scoring for solution alignment

#### 2. Technical Feasibility (20%)
- Technical complexity assessment
- Resource requirement analysis
- Timeline feasibility evaluation
- Budget considerations
- Risk assessment

#### 3. Visual Attractiveness (15%)
- Design quality evaluation
- Content structure analysis
- Color scheme assessment
- Typography evaluation
- Layout organization

#### 4. Image Analysis (15%)
- Technical diagram detection
- Flowchart analysis
- Image quality assessment
- Complexity scoring
- Relevance to technical content

#### 5. Link Quality (10%)
- GitHub repository validation
- Demo video accessibility
- Documentation link analysis
- Link diversity bonus

#### 6. LLM Detection (-15%)
- Model-based detection
- Pattern analysis
- Statistical analysis
- Confidence scoring

## 🎯 Usage Examples

### Evaluating a Single Presentation

```python
import requests

# Upload and evaluate a PPT
files = {'file': open('presentation.pptx', 'rb')}
data = {
    'problem_statement': 'Develop a mobile app for rural healthcare...',
    'team_name': 'TechInnovators'
}

response = requests.post(
    'http://localhost:5000/api/evaluate',
    files=files,
    data=data
)

result = response.json()
print(f"Score: {result['results']['final_score']['percentage_score']}%")
print(f"Grade: {result['results']['final_score']['grade']}")
```

### Bulk Evaluation Script

```python
import os
import requests
import pandas as pd

def evaluate_presentations_batch(folder_path, problem_statements):
    results = []
    
    for filename in os.listdir(folder_path):
        if filename.endswith(('.ppt', '.pptx')):
            # Extract team name from filename
            team_name = filename.split('.')[0]
            
            # Get corresponding problem statement
            ps = problem_statements.get(team_name, '')
            
            files = {'file': open(os.path.join(folder_path, filename), 'rb')}
            data = {'problem_statement': ps, 'team_name': team_name}
            
            response = requests.post(
                'http://localhost:5000/api/evaluate',
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                results.append({
                    'team_name': team_name,
                    'score': result['results']['final_score']['percentage_score'],
                    'grade': result['results']['final_score']['grade'],
                    'evaluation_id': result['evaluation_id']
                })
    
    return pd.DataFrame(results)

# Usage
problem_statements = {
    'Team1': 'Healthcare mobile app problem statement...',
    'Team2': 'Agricultural drone monitoring system...',
    # ... more mappings
}

results_df = evaluate_presentations_batch('presentations/', problem_statements)
results_df.to_csv('evaluation_results.csv', index=False)
```

## 📈 Analysis and Reporting

### Database Queries

The system stores detailed evaluation data in SQLite. You can query the database directly:

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()

# Get statistics
stats = db.get_statistics()
print(f"Total evaluations: {stats['total_evaluations']}")
print(f"Average score: {stats['average_score']}%")

# Get top teams
rankings = db.get_rankings_by_ps("healthcare", limit=10)
for i, team in enumerate(rankings):
    print(f"{i+1}. {team['team_name']}: {team['percentage_score']}%")

# Export results
db.export_evaluations_csv('all_evaluations.csv')
```

### Component Analysis

```python
# Analyze performance by component
component_analysis = db.get_component_analysis()

for component, stats in component_analysis.items():
    print(f"{component}:")
    print(f"  Average Score: {stats['average_raw_score']}")
    print(f"  Score Range: {stats['min_score']} - {stats['max_score']}")
```

## 🔍 Advanced Features

### Custom Scoring Weights

Modify scoring weights in `config.py`:

```python
SCORING_WEIGHTS = {
    'ps_similarity': 0.30,      # Increase PS weight
    'feasibility': 0.25,        # Increase feasibility weight
    'attractiveness': 0.10,     # Decrease attractiveness weight
    'image_analysis': 0.15,
    'link_analysis': 0.05,
    'llm_penalty': -0.15
}
```

### Integration with External Systems

The API can be integrated with:
- **Evaluation Dashboards**: Real-time scoring displays
- **Submission Portals**: Automated evaluation on upload
- **Ranking Systems**: Live leaderboards
- **Report Generators**: Automated feedback reports

## 🛠️ Development

### Running Tests

```bash
# Unit tests (when available)
python -m pytest tests/

# Test specific endpoint
curl -X POST -F "file=@test.pptx" -F "team_name=TestTeam" \
  -F "problem_statement=Test PS" http://localhost:5000/api/evaluate
```

### Adding New Evaluation Components

1. Create new evaluator in `evaluator/` directory
2. Implement evaluation logic
3. Update `app.py` to include new component
4. Modify scoring weights in `config.py`
5. Update database schema if needed

### Configuration Options

Key configuration parameters in `config.py`:

```python
# Model configurations
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'
LLM_DETECTION_MODEL = 'Hello-SimpleAI/chatgpt-detector-roberta'

# Thresholds
SIMILARITY_THRESHOLD = 0.7
FEASIBILITY_THRESHOLD = 0.6
LLM_DETECTION_THRESHOLD = 0.8

# API limits
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'ppt', 'pptx'}
```

## 📋 Evaluation Workflow

### For 40 Problem Statements × 4 Teams Each

1. **Setup**: Configure problem statements and team mappings
2. **Batch Processing**: Use bulk evaluation scripts
3. **Quality Check**: Review flagged presentations manually
4. **Ranking**: Generate final rankings per problem statement
5. **Reporting**: Export comprehensive evaluation reports

### Sample Processing Pipeline

```python
# 1. Define problem statements
problem_statements = load_problem_statements('ps_list.json')

# 2. Process all presentations
for ps_id, ps_text in problem_statements.items():
    presentations = get_presentations_for_ps(ps_id)
    
    for ppt_file in presentations:
        # Evaluate presentation
        result = evaluate_presentation(ppt_file, ps_text)
        
        # Store in database
        store_evaluation_result(result)

# 3. Generate rankings
for ps_id in problem_statements.keys():
    rankings = generate_rankings_for_ps(ps_id)
    export_rankings(ps_id, rankings)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your feature/fix
4. Add tests if applicable
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation above
2. Review configuration settings
3. Check API endpoint responses
4. Verify file formats and sizes
5. Ensure API keys are properly configured

## 🔮 Future Enhancements

- **AI-Powered Insights**: Enhanced natural language feedback
- **Multi-language Support**: Support for presentations in multiple languages
- **Advanced Image Analysis**: Computer vision for detailed diagram analysis
- **Real-time Processing**: WebSocket-based real-time evaluation updates
- **Machine Learning Models**: Custom ML models trained on evaluation data
- **Plagiarism Detection**: Advanced content similarity detection
- **Automated Report Generation**: PDF reports with detailed analysis

---

**Built for Smart India Hackathon 2024** - Enabling fair, comprehensive, and scalable presentation evaluation.