import logging
import numpy as np
from typing import Dict, List, Any, Tuple
from config import Config

logger = logging.getLogger(__name__)


class ScoringSystem:
    def __init__(self):
        self.weights = Config.SCORING_WEIGHTS
        self.max_score = 100.0
        
        # Scoring criteria thresholds
        self.thresholds = {
            'excellent': 0.9,
            'very_good': 0.8,
            'good': 0.7,
            'satisfactory': 0.6,
            'needs_improvement': 0.4,
            'poor': 0.0
        }
    
    def calculate_final_score(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive final score based on all evaluation components
        """
        final_results = {
            'total_score': 0.0,
            'normalized_score': 0.0,
            'percentage_score': 0.0,
            'grade': '',
            'component_scores': {},
            'weighted_scores': {},
            'score_breakdown': {},
            'strengths': [],
            'weaknesses': [],
            'overall_assessment': '',
            'ranking_factors': {},
            'recommendations': []
        }
        
        try:
            # Extract component scores
            component_scores = self._extract_component_scores(evaluation_results)
            final_results['component_scores'] = component_scores
            
            # Calculate weighted scores
            weighted_scores = self._calculate_weighted_scores(component_scores)
            final_results['weighted_scores'] = weighted_scores
            
            # Calculate total score
            total_score = sum(weighted_scores.values())
            final_results['total_score'] = total_score
            
            # Normalize score to 0-1 range
            final_results['normalized_score'] = max(0.0, min(total_score, 1.0))
            
            # Convert to percentage
            final_results['percentage_score'] = final_results['normalized_score'] * 100
            
            # Assign grade
            final_results['grade'] = self._assign_grade(final_results['normalized_score'])
            
            # Detailed score breakdown
            final_results['score_breakdown'] = self._create_score_breakdown(
                component_scores, weighted_scores
            )
            
            # Identify strengths and weaknesses
            strengths, weaknesses = self._identify_strengths_weaknesses(component_scores)
            final_results['strengths'] = strengths
            final_results['weaknesses'] = weaknesses
            
            # Overall assessment
            final_results['overall_assessment'] = self._generate_overall_assessment(
                final_results['normalized_score'], strengths, weaknesses
            )
            
            # Ranking factors for comparison
            final_results['ranking_factors'] = self._calculate_ranking_factors(evaluation_results)
            
            # Generate comprehensive recommendations
            final_results['recommendations'] = self._generate_final_recommendations(
                evaluation_results, strengths, weaknesses
            )
            
        except Exception as e:
            logger.error(f"Error in final score calculation: {str(e)}")
            final_results['error'] = str(e)
        
        return final_results
    
    def _extract_component_scores(self, evaluation_results: Dict[str, Any]) -> Dict[str, float]:
        """Extract normalized scores from all evaluation components"""
        component_scores = {}
        
        try:
            # Problem Statement Similarity
            ps_similarity = evaluation_results.get('ps_similarity', {})
            if isinstance(ps_similarity, dict):
                component_scores['ps_similarity'] = ps_similarity.get('overall_similarity', 0.0)
            else:
                component_scores['ps_similarity'] = float(ps_similarity) if ps_similarity else 0.0
            
            # Feasibility
            feasibility = evaluation_results.get('feasibility', {})
            if isinstance(feasibility, dict):
                component_scores['feasibility'] = feasibility.get('overall_feasibility', 0.0)
            else:
                component_scores['feasibility'] = float(feasibility) if feasibility else 0.0
            
            # Attractiveness
            attractiveness = evaluation_results.get('attractiveness', {})
            if isinstance(attractiveness, dict):
                component_scores['attractiveness'] = attractiveness.get('overall_attractiveness', 0.0)
            else:
                component_scores['attractiveness'] = float(attractiveness) if attractiveness else 0.0
            
            # Image Analysis
            image_analysis = evaluation_results.get('image_analysis', {})
            if isinstance(image_analysis, dict):
                component_scores['image_analysis'] = image_analysis.get('overall_image_score', 0.0)
            else:
                component_scores['image_analysis'] = float(image_analysis) if image_analysis else 0.0
            
            # Link Analysis
            link_analysis = evaluation_results.get('link_analysis', {})
            if isinstance(link_analysis, dict):
                component_scores['link_analysis'] = link_analysis.get('link_quality_score', 0.0)
            else:
                component_scores['link_analysis'] = float(link_analysis) if link_analysis else 0.0
            
            # LLM Detection (penalty)
            llm_detection = evaluation_results.get('llm_detection', {})
            if isinstance(llm_detection, dict):
                llm_probability = llm_detection.get('overall_llm_probability', 0.0)
                # Convert to penalty (higher LLM probability = lower score)
                component_scores['llm_penalty'] = llm_probability
            else:
                component_scores['llm_penalty'] = 0.0
            
            # Ensure all scores are between 0 and 1
            for key in component_scores:
                component_scores[key] = max(0.0, min(component_scores[key], 1.0))
            
        except Exception as e:
            logger.error(f"Error extracting component scores: {str(e)}")
            # Provide default scores if extraction fails
            component_scores = {
                'ps_similarity': 0.0,
                'feasibility': 0.0,
                'attractiveness': 0.0,
                'image_analysis': 0.0,
                'link_analysis': 0.0,
                'llm_penalty': 0.0
            }
        
        return component_scores
    
    def _calculate_weighted_scores(self, component_scores: Dict[str, float]) -> Dict[str, float]:
        """Calculate weighted scores based on configured weights"""
        weighted_scores = {}
        
        for component, score in component_scores.items():
            weight = self.weights.get(component, 0.0)
            
            if component == 'llm_penalty':
                # LLM penalty reduces the score
                weighted_scores[component] = score * weight  # This will be negative
            else:
                weighted_scores[component] = score * weight
        
        return weighted_scores
    
    def _assign_grade(self, normalized_score: float) -> str:
        """Assign letter grade based on normalized score"""
        if normalized_score >= self.thresholds['excellent']:
            return 'A+'
        elif normalized_score >= self.thresholds['very_good']:
            return 'A'
        elif normalized_score >= self.thresholds['good']:
            return 'B+'
        elif normalized_score >= self.thresholds['satisfactory']:
            return 'B'
        elif normalized_score >= self.thresholds['needs_improvement']:
            return 'C'
        else:
            return 'D'
    
    def _create_score_breakdown(self, component_scores: Dict[str, float], 
                              weighted_scores: Dict[str, float]) -> Dict[str, Any]:
        """Create detailed score breakdown"""
        breakdown = {
            'components': {},
            'total_possible': 1.0,
            'total_achieved': sum(score for score in weighted_scores.values() if score > 0),
            'penalty_applied': abs(weighted_scores.get('llm_penalty', 0.0))
        }
        
        for component, raw_score in component_scores.items():
            weight = self.weights.get(component, 0.0)
            weighted_score = weighted_scores.get(component, 0.0)
            
            breakdown['components'][component] = {
                'raw_score': raw_score,
                'weight': weight,
                'weighted_score': weighted_score,
                'percentage': raw_score * 100,
                'contribution': abs(weighted_score) / sum(abs(s) for s in weighted_scores.values()) * 100 
                               if sum(abs(s) for s in weighted_scores.values()) > 0 else 0
            }
        
        return breakdown
    
    def _identify_strengths_weaknesses(self, component_scores: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """Identify strengths and weaknesses based on component scores"""
        strengths = []
        weaknesses = []
        
        # Component name mapping
        component_names = {
            'ps_similarity': 'Problem Statement Alignment',
            'feasibility': 'Project Feasibility',
            'attractiveness': 'Presentation Design',
            'image_analysis': 'Visual Content Quality',
            'link_analysis': 'Supporting Links',
            'llm_penalty': 'Content Originality'
        }
        
        for component, score in component_scores.items():
            component_name = component_names.get(component, component)
            
            if component == 'llm_penalty':
                # For LLM penalty, lower is better
                if score < 0.3:
                    strengths.append(f"High content originality ({component_name})")
                elif score > 0.7:
                    weaknesses.append(f"Potential AI-generated content ({component_name})")
            else:
                if score >= 0.8:
                    strengths.append(f"Excellent {component_name.lower()}")
                elif score >= 0.6:
                    strengths.append(f"Good {component_name.lower()}")
                elif score < 0.4:
                    weaknesses.append(f"Poor {component_name.lower()}")
        
        return strengths, weaknesses
    
    def _generate_overall_assessment(self, normalized_score: float, 
                                   strengths: List[str], weaknesses: List[str]) -> str:
        """Generate overall assessment text"""
        if normalized_score >= self.thresholds['excellent']:
            assessment = "Outstanding presentation with excellent execution across all criteria."
        elif normalized_score >= self.thresholds['very_good']:
            assessment = "Very strong presentation with high-quality content and implementation."
        elif normalized_score >= self.thresholds['good']:
            assessment = "Good presentation with solid foundation and clear potential."
        elif normalized_score >= self.thresholds['satisfactory']:
            assessment = "Satisfactory presentation meeting basic requirements with room for improvement."
        elif normalized_score >= self.thresholds['needs_improvement']:
            assessment = "Presentation needs significant improvement in multiple areas."
        else:
            assessment = "Presentation requires major revision across most evaluation criteria."
        
        # Add specific context
        if len(strengths) > 2:
            assessment += " The presentation demonstrates multiple strong points."
        if len(weaknesses) > 2:
            assessment += " Several areas need attention for improvement."
        
        return assessment
    
    def _calculate_ranking_factors(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate factors used for ranking presentations"""
        ranking_factors = {
            'innovation_score': 0.0,
            'technical_depth': 0.0,
            'implementation_readiness': 0.0,
            'presentation_quality': 0.0,
            'solution_completeness': 0.0
        }
        
        try:
            # Innovation score (based on feasibility and PS similarity)
            feasibility = evaluation_results.get('feasibility', {})
            ps_similarity = evaluation_results.get('ps_similarity', {})
            
            if isinstance(feasibility, dict):
                tech_feasibility = feasibility.get('technical_feasibility', 0.0)
                scalability = feasibility.get('scalability_score', 0.0)
                ranking_factors['innovation_score'] = (tech_feasibility + scalability) / 2
            
            # Technical depth (from image analysis and feasibility)
            image_analysis = evaluation_results.get('image_analysis', {})
            if isinstance(image_analysis, dict):
                tech_depth = image_analysis.get('technical_depth_score', 0.0)
                ranking_factors['technical_depth'] = tech_depth
            
            # Implementation readiness (feasibility + links)
            if isinstance(feasibility, dict):
                resource_feas = feasibility.get('resource_feasibility', 0.0)
                timeline_feas = feasibility.get('timeline_feasibility', 0.0)
                ranking_factors['implementation_readiness'] = (resource_feas + timeline_feas) / 2
            
            # Presentation quality (attractiveness + image quality)
            attractiveness = evaluation_results.get('attractiveness', {})
            if isinstance(attractiveness, dict):
                ranking_factors['presentation_quality'] = attractiveness.get('overall_attractiveness', 0.0)
            
            # Solution completeness (PS similarity + link analysis)
            if isinstance(ps_similarity, dict):
                coverage = ps_similarity.get('coverage_score', 0.0)
                relevance = ps_similarity.get('relevance_score', 0.0)
                ranking_factors['solution_completeness'] = (coverage + relevance) / 2
            
        except Exception as e:
            logger.error(f"Error calculating ranking factors: {str(e)}")
        
        return ranking_factors
    
    def _generate_final_recommendations(self, evaluation_results: Dict[str, Any], 
                                      strengths: List[str], weaknesses: List[str]) -> List[str]:
        """Generate comprehensive final recommendations"""
        recommendations = []
        
        try:
            # Priority recommendations based on weaknesses
            if len(weaknesses) > 0:
                recommendations.append("Priority Improvements:")
                for weakness in weaknesses[:3]:  # Top 3 weaknesses
                    recommendations.append(f"• Address {weakness}")
            
            # Component-specific recommendations
            components = ['ps_similarity', 'feasibility', 'attractiveness', 'image_analysis', 'link_analysis']
            
            for component in components:
                component_data = evaluation_results.get(component, {})
                if isinstance(component_data, dict) and 'recommendations' in component_data:
                    comp_recommendations = component_data['recommendations']
                    if comp_recommendations and len(comp_recommendations) > 0:
                        # Add top recommendation from each component
                        recommendations.append(f"• {comp_recommendations[0]}")
            
            # Overall strategic recommendations
            if len(strengths) > 2:
                recommendations.append("Leverage your strong points to further enhance the presentation")
            
            # LLM content check
            llm_detection = evaluation_results.get('llm_detection', {})
            if isinstance(llm_detection, dict):
                if llm_detection.get('is_likely_llm_generated', False):
                    recommendations.append("• Review content for originality and add personal insights")
            
            # If no specific recommendations, provide general ones
            if len(recommendations) == 0:
                recommendations.extend([
                    "Continue refining technical details",
                    "Enhance visual presentation quality",
                    "Strengthen problem-solution alignment"
                ])
        
        except Exception as e:
            logger.error(f"Error generating final recommendations: {str(e)}")
            recommendations = ["Review all evaluation components for improvement opportunities"]
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def rank_presentations(self, presentations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rank multiple presentations based on their scores and ranking factors
        """
        try:
            # Calculate ranking score for each presentation
            for presentation in presentations:
                ranking_score = self._calculate_ranking_score(presentation)
                presentation['ranking_score'] = ranking_score
            
            # Sort by ranking score (descending)
            ranked_presentations = sorted(
                presentations, 
                key=lambda x: x.get('ranking_score', 0.0), 
                reverse=True
            )
            
            # Add rank position
            for i, presentation in enumerate(ranked_presentations):
                presentation['rank'] = i + 1
            
            return ranked_presentations
            
        except Exception as e:
            logger.error(f"Error ranking presentations: {str(e)}")
            return presentations
    
    def _calculate_ranking_score(self, presentation: Dict[str, Any]) -> float:
        """Calculate ranking score for a presentation"""
        try:
            final_score = presentation.get('final_score', {})
            if not isinstance(final_score, dict):
                return 0.0
            
            # Base score
            base_score = final_score.get('normalized_score', 0.0)
            
            # Ranking factors
            ranking_factors = final_score.get('ranking_factors', {})
            
            # Weighted ranking calculation
            ranking_weights = {
                'innovation_score': 0.25,
                'technical_depth': 0.25,
                'implementation_readiness': 0.2,
                'presentation_quality': 0.15,
                'solution_completeness': 0.15
            }
            
            ranking_bonus = 0.0
            for factor, weight in ranking_weights.items():
                factor_score = ranking_factors.get(factor, 0.0)
                ranking_bonus += factor_score * weight
            
            # Combine base score with ranking factors
            total_ranking_score = (base_score * 0.7) + (ranking_bonus * 0.3)
            
            return min(total_ranking_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating ranking score: {str(e)}")
            return 0.0