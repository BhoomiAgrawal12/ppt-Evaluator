import logging
import json
import time
from typing import Dict, List, Any, Optional
from google import genai
from config import Config
import requests
import os

logger = logging.getLogger(__name__)


class LLMEvaluator:
    """
    LLM-based evaluation system using Google Gemini for intelligent presentation assessment
    """

    def __init__(self):
        self.gemini_api_key = Config.GEMINI_API_KEY
        self.model_name = Config.GEMINI_MODEL
        self.timeout = Config.LLM_EVALUATION_TIMEOUT
        self.max_retries = Config.MAX_RETRY_ATTEMPTS

        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set. LLM evaluation will be limited.")
            self.client = None
        else:
            try:
                # Use the new client approach with API key
                self.client = genai.Client(api_key=self.gemini_api_key)
                logger.info(f"Initialized Gemini client with model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {str(e)}")
                self.client = None

    @property
    def model(self):
        """For backward compatibility"""
        return self.client

    def evaluate_presentation(self, content: Dict[str, Any], problem_statement: str, team_name: str) -> Dict[str, Any]:
        """
        Complete LLM-based evaluation of a presentation
        """
        results = {
            'team_name': team_name,
            'problem_statement': problem_statement,
            'evaluation_method': 'llm_based',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'evaluations': {},
            'final_assessment': {},
            'ai_detection': {},
            'error': None
        }

        try:
            # Extract presentation content
            presentation_text = content.get('text', '')
            slides_info = content.get('slides', [])
            images_info = content.get('images', [])

            # 1. AI Content Detection using detector.py
            logger.info("Step 1: Detecting AI-generated content")
            results['ai_detection'] = self._detect_ai_content(presentation_text)

            # 2. Technical Feasibility Evaluation
            logger.info("Step 2: Evaluating technical feasibility")
            results['evaluations']['technical_feasibility'] = self._evaluate_technical_feasibility(
                presentation_text, problem_statement
            )

            # 3. Problem Statement Alignment
            logger.info("Step 3: Evaluating problem statement alignment")
            results['evaluations']['problem_alignment'] = self._evaluate_problem_alignment(
                presentation_text, problem_statement
            )

            # 4. Solution Quality Assessment
            logger.info("Step 4: Evaluating solution quality")
            results['evaluations']['solution_quality'] = self._evaluate_solution_quality(
                presentation_text, slides_info, images_info
            )

            # 5. Presentation Quality
            logger.info("Step 5: Evaluating presentation quality")
            results['evaluations']['presentation_quality'] = self._evaluate_presentation_quality(
                presentation_text, slides_info, images_info
            )

            # 6. Innovation and Creativity
            logger.info("Step 6: Evaluating innovation and creativity")
            results['evaluations']['innovation'] = self._evaluate_innovation(
                presentation_text, problem_statement
            )

            # 7. Final Assessment and Scoring
            logger.info("Step 7: Generating final assessment")
            results['final_assessment'] = self._generate_final_assessment(
                results['evaluations'], results['ai_detection'], problem_statement
            )

            logger.info(f"LLM evaluation completed for {team_name}")

        except Exception as e:
            logger.error(f"Error in LLM evaluation: {str(e)}")
            results['error'] = str(e)
            results['final_assessment'] = {
                'overall_score': 0.0,
                'grade': 'F',
                'summary': 'Evaluation failed due to technical error'
            }

        return results

    def _detect_ai_content(self, text: str) -> Dict[str, Any]:
        """Use detector.py service for AI content detection"""
        try:
            response = requests.post(
                'http://localhost:5001/detect',
                json={'text': text},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'is_ai_generated': result['label'] == 'AI-Generated',
                    'confidence': result['score'],
                    'label': result['label'],
                    'method': 'transformer_model'
                }
            else:
                logger.warning("AI detector service unavailable")
                return {
                    'is_ai_generated': False,
                    'confidence': 0.0,
                    'label': 'Human-Written',
                    'method': 'fallback',
                    'note': 'Detector service unavailable'
                }

        except Exception as e:
            logger.warning(f"AI detection failed: {str(e)}")
            return {
                'is_ai_generated': False,
                'confidence': 0.0,
                'label': 'Human-Written',
                'method': 'fallback',
                'error': str(e)
            }

    def _evaluate_technical_feasibility(self, presentation_text: str, problem_statement: str) -> Dict[str, Any]:
        """Evaluate technical feasibility using LLM"""
        prompt = f"""
        You are an expert technical evaluator for hackathon presentations. Analyze the following presentation content and problem statement to evaluate the technical feasibility of the proposed solution.

        Problem Statement: {problem_statement}

        Presentation Content: {presentation_text}

        Evaluate the technical feasibility on these aspects:
        1. Technical Complexity - Is the proposed solution technically sound and achievable?
        2. Technology Stack - Are the chosen technologies appropriate and realistic?
        3. Implementation Timeline - Can this be realistically implemented in a hackathon timeframe?
        4. Resource Requirements - Are the resource needs reasonable and specified?
        5. Scalability - Does the solution consider future growth and scaling?

        Provide your evaluation in JSON format:
        {{
            "score": <0.0 to 1.0>,
            "technical_complexity": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "technology_stack": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "implementation_timeline": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "resource_requirements": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "scalability": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "strengths": ["<strength 1>", "<strength 2>"],
            "concerns": ["<concern 1>", "<concern 2>"],
            "recommendations": ["<recommendation 1>", "<recommendation 2>"]
        }}
        """

        return self._make_llm_call(prompt, "technical_feasibility")

    def _evaluate_problem_alignment(self, presentation_text: str, problem_statement: str) -> Dict[str, Any]:
        """Evaluate how well the presentation aligns with the problem statement"""
        prompt = f"""
        You are an expert evaluator for hackathon presentations. Analyze how well the presentation content addresses the given problem statement.

        Problem Statement: {problem_statement}

        Presentation Content: {presentation_text}

        Evaluate the alignment on these aspects:
        1. Problem Understanding - Does the team clearly understand the problem?
        2. Solution Relevance - How directly does the solution address the problem?
        3. Target Audience - Is the intended user/beneficiary clearly identified?
        4. Problem Scope - Does the solution address the right scope of the problem?
        5. Requirements Coverage - Are the key requirements from the PS addressed?

        Provide your evaluation in JSON format:
        {{
            "score": <0.0 to 1.0>,
            "problem_understanding": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "solution_relevance": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "target_audience": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "problem_scope": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "requirements_coverage": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "key_alignments": ["<alignment 1>", "<alignment 2>"],
            "gaps": ["<gap 1>", "<gap 2>"],
            "suggestions": ["<suggestion 1>", "<suggestion 2>"]
        }}
        """

        return self._make_llm_call(prompt, "problem_alignment")

    def _evaluate_solution_quality(self, presentation_text: str, slides_info: List[Dict], images_info: List[Dict]) -> Dict[str, Any]:
        """Evaluate the quality of the proposed solution"""
        slides_summary = f"Total slides: {len(slides_info)}"
        if slides_info:
            slides_summary += f", Average words per slide: {sum(s.get('word_count', 0) for s in slides_info) / len(slides_info):.1f}"

        images_summary = f"Total images: {len(images_info)}"

        prompt = f"""
        You are an expert solution architect evaluating hackathon presentations. Analyze the quality and completeness of the proposed solution.

        Presentation Content: {presentation_text}

        Presentation Structure: {slides_summary}
        Visual Elements: {images_summary}

        Evaluate the solution quality on these aspects:
        1. Solution Completeness - Is the solution well-defined and complete?
        2. Innovation Level - How innovative and creative is the approach?
        3. User Experience - Is user experience well considered?
        4. Architecture Design - Is the system architecture clearly defined?
        5. Implementation Details - Are implementation details provided?

        Provide your evaluation in JSON format:
        {{
            "score": <0.0 to 1.0>,
            "completeness": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "innovation": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "user_experience": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "architecture": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "implementation": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "highlights": ["<highlight 1>", "<highlight 2>"],
            "weaknesses": ["<weakness 1>", "<weakness 2>"],
            "improvements": ["<improvement 1>", "<improvement 2>"]
        }}
        """

        return self._make_llm_call(prompt, "solution_quality")

    def _evaluate_presentation_quality(self, presentation_text: str, slides_info: List[Dict], images_info: List[Dict]) -> Dict[str, Any]:
        """Evaluate presentation quality and communication effectiveness"""
        content_structure = self._analyze_content_structure(slides_info)

        prompt = f"""
        You are an expert presentation coach evaluating hackathon presentations for clarity, structure, and communication effectiveness.

        Presentation Content: {presentation_text}

        Content Structure Analysis: {content_structure}
        Number of Visual Elements: {len(images_info)}

        Evaluate the presentation quality on these aspects:
        1. Content Organization - Is the content well-structured and logical?
        2. Clarity and Communication - Is the message clear and well-communicated?
        3. Visual Design - Are visual elements effective and professional?
        4. Flow and Narrative - Does the presentation tell a coherent story?
        5. Audience Engagement - Is the presentation engaging and compelling?

        Provide your evaluation in JSON format:
        {{
            "score": <0.0 to 1.0>,
            "organization": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "clarity": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "visual_design": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "flow": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "engagement": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "strong_points": ["<strong point 1>", "<strong point 2>"],
            "areas_for_improvement": ["<improvement 1>", "<improvement 2>"],
            "presentation_tips": ["<tip 1>", "<tip 2>"]
        }}
        """

        return self._make_llm_call(prompt, "presentation_quality")

    def _evaluate_innovation(self, presentation_text: str, problem_statement: str) -> Dict[str, Any]:
        """Evaluate innovation and creativity of the solution"""
        prompt = f"""
        You are an innovation expert evaluating hackathon presentations for creativity, originality, and innovative thinking.

        Problem Statement: {problem_statement}

        Presentation Content: {presentation_text}

        Evaluate the innovation on these aspects:
        1. Originality - How original and unique is the approach?
        2. Creative Thinking - Does the solution show creative problem-solving?
        3. Technology Innovation - Are innovative technologies or methods used?
        4. Business Innovation - Is there innovative thinking in business model/approach?
        5. Social Impact - Does the solution have potential for positive social impact?

        Provide your evaluation in JSON format:
        {{
            "score": <0.0 to 1.0>,
            "originality": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "creative_thinking": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "technology_innovation": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "business_innovation": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "social_impact": {{
                "assessment": "<detailed analysis>",
                "score": <0.0 to 1.0>
            }},
            "innovative_aspects": ["<aspect 1>", "<aspect 2>"],
            "conventional_aspects": ["<aspect 1>", "<aspect 2>"],
            "innovation_suggestions": ["<suggestion 1>", "<suggestion 2>"]
        }}
        """

        return self._make_llm_call(prompt, "innovation")

    def _generate_final_assessment(self, evaluations: Dict[str, Any], ai_detection: Dict[str, Any], problem_statement: str) -> Dict[str, Any]:
        """Generate final assessment and overall scoring"""
        evaluation_summary = json.dumps(evaluations, indent=2)
        ai_summary = json.dumps(ai_detection, indent=2)

        prompt = f"""
        You are the chief judge for a hackathon evaluation. Based on all the detailed evaluations, provide a comprehensive final assessment.

        Evaluation Results: {evaluation_summary}

        AI Detection Results: {ai_summary}

        Problem Statement: {problem_statement}

        Consider these weights:
        - Technical Feasibility: 30%
        - Problem Alignment: 25%
        - Solution Quality: 20%
        - Presentation Quality: 15%
        - Innovation: 10%
        - AI Content Penalty: -20% if highly AI-generated

        Provide your final assessment in JSON format:
        {{
            "overall_score": <0.0 to 1.0>,
            "percentage_score": <0 to 100>,
            "grade": "<A+/A/B+/B/C+/C/D/F>",
            "weighted_scores": {{
                "technical_feasibility": <weighted score>,
                "problem_alignment": <weighted score>,
                "solution_quality": <weighted score>,
                "presentation_quality": <weighted score>,
                "innovation": <weighted score>,
                "ai_penalty": <penalty if applicable>
            }},
            "summary": "<comprehensive 2-3 sentence summary>",
            "top_strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
            "key_weaknesses": ["<weakness 1>", "<weakness 2>"],
            "critical_recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"],
            "judge_comments": "<detailed judge feedback as if speaking to the team>",
            "ranking_justification": "<explanation of why this score is appropriate>",
            "improvement_roadmap": ["<step 1>", "<step 2>", "<step 3>"]
        }}
        """

        return self._make_llm_call(prompt, "final_assessment")

    def _analyze_content_structure(self, slides_info: List[Dict]) -> str:
        """Analyze presentation content structure"""
        if not slides_info:
            return "No slide structure information available"

        total_slides = len(slides_info)
        total_words = sum(slide.get('word_count', 0) for slide in slides_info)
        avg_words = total_words / total_slides if total_slides > 0 else 0

        titled_slides = sum(1 for slide in slides_info if slide.get('title'))
        bullet_slides = sum(1 for slide in slides_info if slide.get('has_bullet_points'))

        return f"Total slides: {total_slides}, Average words/slide: {avg_words:.1f}, " \
               f"Titled slides: {titled_slides}, Bullet point slides: {bullet_slides}"

    def _make_llm_call(self, prompt: str, evaluation_type: str) -> Dict[str, Any]:
        """Make LLM API call with retry logic and error handling"""
        if not self.client:
            logger.warning(f"Gemini client not available for {evaluation_type}")
            return {
                'score': 0.5,
                'error': 'LLM client not available',
                'assessment': 'Unable to perform LLM evaluation - client not configured'
            }

        for attempt in range(self.max_retries):
            try:
                # Use the new client API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                if response.text:
                    # Try to parse JSON response
                    try:
                        result = json.loads(response.text)
                        return result
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try to extract JSON from the response
                        import re
                        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
                        if json_match:
                            try:
                                result = json.loads(json_match.group())
                                return result
                            except json.JSONDecodeError:
                                pass

                        # If all JSON extraction fails, return structured fallback
                        return {
                            'score': 0.5,
                            'assessment': response.text,
                            'error': 'Could not parse structured response'
                        }
                else:
                    logger.warning(f"Empty response from LLM for {evaluation_type}")

            except Exception as e:
                logger.error(f"LLM call failed for {evaluation_type}, attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries - 1:
                    return {
                        'score': 0.0,
                        'error': f'LLM evaluation failed after {self.max_retries} attempts: {str(e)}',
                        'assessment': f'Failed to evaluate {evaluation_type} using LLM'
                    }
                time.sleep(2 ** attempt)  # Exponential backoff

        return {
            'score': 0.0,
            'error': f'Max retries exceeded for {evaluation_type}',
            'assessment': 'Failed to complete LLM evaluation'
        }