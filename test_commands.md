# Testing Commands for SIH PPT Evaluator

## Prerequisites
Make sure the Flask app is running:
```bash
python app.py
```

## Test Method 1: Complete Automated Test
```bash
python full_test.py
```
This will:
- Check API health
- Create a test PowerPoint presentation
- Run full evaluation
- Test all endpoints
- Display detailed results

## Test Method 2: Test with Your Own PPT File
```bash
python test_with_ppt.py
```
Then enter the path to your PPT/PPTX file when prompted.

## Test Method 3: Manual API Testing with curl

### 1. Check API Health
```bash
curl http://localhost:5000/
```

### 2. Evaluate a PPT file
```bash
curl -X POST \
  -F "file=@your_presentation.pptx" \
  -F "team_name=TestTeam" \
  -F "problem_statement=Your problem statement here" \
  http://localhost:5000/api/evaluate
```

### 3. Get evaluation by ID
```bash
curl http://localhost:5000/api/evaluations/YOUR_EVALUATION_ID
```

### 4. List all evaluations
```bash
curl http://localhost:5000/api/evaluations
```

## Test Method 4: Create Test PPT Only
```bash
python create_test_ppt.py
```
This creates `test_healthcare_presentation.pptx` that you can use for testing.

## Test Method 5: Simple Health Check
```bash
python simple_test.py
```

## Expected Output Example
When successful, you should see:
```
Final Score: 75.30%
Grade: B+
Component Scores:
  PS Similarity: 0.823
  Feasibility: 0.756
  Attractiveness: 0.689
  Image Analysis: 0.234
  Link Analysis: 0.567
  LLM Penalty: 0.123
```

## Troubleshooting
If tests fail:
1. Ensure Flask app is running (`python app.py`)
2. Check that all dependencies are installed
3. Verify API keys are set in .env file
4. Make sure you're using PPT/PPTX files (not TXT)