import logging
import re
import numpy as np
from typing import Dict, List, Any, Tuple
import openai
from config import Config

logger = logging.getLogger(__name__)


class FeasibilityCalculator:
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized for feasibility analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
    
    def calculate_feasibility(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate feasibility of the proposed solution
        """
        results = {
            'overall_feasibility': 0.0,
            'technical_feasibility': 0.0,
            'resource_feasibility': 0.0,
            'timeline_feasibility': 0.0,
            'budget_feasibility': 0.0,
            'scalability_score': 0.0,
            'risk_assessment': {},
            'detailed_analysis': {},
            'recommendations': []
        }
        
        try:
            text_content = parsed_content.get('text', '')
            
            if not text_content:
                results['error'] = "No text content to analyze"
                return results
            
            # Technical feasibility analysis
            results['technical_feasibility'] = self._analyze_technical_feasibility(text_content)
            
            # Resource feasibility analysis  
            results['resource_feasibility'] = self._analyze_resource_feasibility(text_content)
            
            # Timeline feasibility analysis
            results['timeline_feasibility'] = self._analyze_timeline_feasibility(text_content)
            
            # Budget feasibility analysis
            results['budget_feasibility'] = self._analyze_budget_feasibility(text_content)
            
            # Scalability analysis
            results['scalability_score'] = self._analyze_scalability(text_content)
            
            # Risk assessment
            results['risk_assessment'] = self._assess_risks(text_content)
            
            # Detailed analysis using LLM if available
            if self.client:
                results['detailed_analysis'] = self._llm_feasibility_analysis(text_content)
            
            # Calculate overall feasibility
            results['overall_feasibility'] = self._calculate_overall_feasibility(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            logger.error(f"Error in feasibility calculation: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_technical_feasibility(self, content: str) -> float:
        """Analyze technical feasibility of the proposed solution"""
        try:
            content_lower = content.lower()
            
            # Technical complexity indicators
            complexity_indicators = {
                'high_complexity': [
                    'machine learning', 'artificial intelligence', 'blockchain', 'quantum',
                    'distributed system', 'microservices', 'real-time processing',
                    'big data', 'data science', 'neural network', 'deep learning'
                ],
                'medium_complexity': [
                    'web application', 'mobile app', 'database', 'api', 'cloud',
                    'authentication', 'payment gateway', 'notification system'
                ],
                'low_complexity': [
                    'static website', 'simple form', 'basic crud', 'file upload',
                    'email system', 'basic dashboard'
                ]
            }
            
            # Established technology indicators
            established_tech = [
                'react', 'angular', 'vue', 'node.js', 'python', 'java', 'c++',
                'mysql', 'postgresql', 'mongodb', 'aws', 'azure', 'google cloud',
                'docker', 'kubernetes', 'jenkins', 'git'
            ]
            
            # Calculate complexity score
            complexity_score = 0.0
            for category, terms in complexity_indicators.items():
                term_count = sum(1 for term in terms if term in content_lower)
                if category == 'low_complexity':
                    complexity_score += term_count * 0.8  # Higher score for lower complexity
                elif category == 'medium_complexity':
                    complexity_score += term_count * 0.6
                else:  # high_complexity
                    complexity_score += term_count * 0.3
            
            # Established technology bonus
            tech_count = sum(1 for tech in established_tech if tech in content_lower)
            tech_bonus = min(tech_count * 0.1, 0.3)
            
            # Implementation details indicator
            implementation_keywords = [
                'architecture', 'design pattern', 'algorithm', 'framework',
                'library', 'module', 'component', 'interface', 'protocol'
            ]
            impl_detail_score = sum(1 for keyword in implementation_keywords if keyword in content_lower)
            impl_score = min(impl_detail_score * 0.05, 0.2)
            
            # Combine scores
            total_score = complexity_score + tech_bonus + impl_score
            
            # Normalize to 0-1 range
            return min(total_score / 2.0, 1.0)
            
        except Exception as e:
            logger.error(f"Technical feasibility analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_resource_feasibility(self, content: str) -> float:
        """Analyze resource requirements feasibility"""
        try:
            content_lower = content.lower()
            
            # Team size indicators
            team_indicators = [
                'team', 'developer', 'designer', 'project manager', 'tester',
                'backend', 'frontend', 'full-stack', 'devops', 'data scientist'
            ]
            
            # Infrastructure indicators
            infrastructure_indicators = [
                'server', 'cloud', 'hosting', 'database server', 'load balancer',
                'cdn', 'storage', 'backup', 'monitoring', 'security'
            ]
            
            # Calculate resource score
            team_mentions = sum(1 for indicator in team_indicators if indicator in content_lower)
            infra_mentions = sum(1 for indicator in infrastructure_indicators if indicator in content_lower)
            
            # Realistic team size (2-8 people for SIH)
            if 2 <= team_mentions <= 8:
                team_score = 1.0
            elif team_mentions > 8:
                team_score = 0.6  # Overly ambitious
            elif team_mentions == 1:
                team_score = 0.7
            else:
                team_score = 0.8  # No specific mention, assume reasonable
            
            # Infrastructure reasonableness
            if infra_mentions <= 5:
                infra_score = 1.0
            elif infra_mentions <= 10:
                infra_score = 0.8
            else:
                infra_score = 0.5  # Too complex infrastructure
            
            # Check for unrealistic resource claims
            unrealistic_indicators = [
                'unlimited', 'massive scale', 'enterprise level', 'global deployment',
                'millions of users', 'petabyte', 'supercomputer'
            ]
            
            unrealistic_count = sum(1 for indicator in unrealistic_indicators if indicator in content_lower)
            penalty = min(unrealistic_count * 0.2, 0.4)
            
            resource_score = (team_score + infra_score) / 2 - penalty
            
            return max(0.0, min(resource_score, 1.0))
            
        except Exception as e:
            logger.error(f"Resource feasibility analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_timeline_feasibility(self, content: str) -> float:
        """Analyze timeline feasibility"""
        try:
            content_lower = content.lower()
            
            # Timeline indicators
            timeline_patterns = [
                r'(\d+)\s*month[s]?', r'(\d+)\s*week[s]?', r'(\d+)\s*day[s]?',
                r'(\d+)\s*year[s]?', r'timeline', r'schedule', r'deadline',
                r'phase', r'milestone', r'sprint'
            ]
            
            # Development phases
            phase_indicators = [
                'planning', 'design', 'development', 'testing', 'deployment',
                'prototype', 'mvp', 'beta', 'production', 'maintenance'
            ]
            
            # Extract timeline mentions
            timeline_mentions = 0
            for pattern in timeline_patterns:
                matches = re.findall(pattern, content_lower)
                timeline_mentions += len(matches)
            
            # Count development phases
            phase_count = sum(1 for phase in phase_indicators if phase in content_lower)
            
            # Realistic timeline score
            if timeline_mentions > 0:
                timeline_score = 0.8  # Good that timeline is mentioned
            else:
                timeline_score = 0.6  # No specific timeline
            
            # Phase planning bonus
            if phase_count >= 3:
                timeline_score += 0.2
            elif phase_count >= 1:
                timeline_score += 0.1
            
            # Check for unrealistic timelines
            unrealistic_timeline = [
                'overnight', 'immediately', 'instant', 'real-time development',
                '1 day', '1 week for entire project'
            ]
            
            unrealistic_count = sum(1 for indicator in unrealistic_timeline if indicator in content_lower)
            penalty = min(unrealistic_count * 0.3, 0.5)
            
            final_score = timeline_score - penalty
            
            return max(0.0, min(final_score, 1.0))
            
        except Exception as e:
            logger.error(f"Timeline feasibility analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_budget_feasibility(self, content: str) -> float:
        """Analyze budget feasibility"""
        try:
            content_lower = content.lower()
            
            # Budget indicators
            budget_keywords = [
                'budget', 'cost', 'price', 'funding', 'investment', 'expense',
                'affordable', 'cheap', 'expensive', 'free', 'open source'
            ]
            
            # Cost-conscious indicators
            cost_conscious = [
                'open source', 'free tier', 'low cost', 'budget-friendly',
                'cost-effective', 'minimal cost', 'bootstrap'
            ]
            
            # Expensive indicators
            expensive_indicators = [
                'enterprise license', 'premium', 'high-end', 'expensive',
                'costly', 'large investment', 'significant funding'
            ]
            
            budget_mentions = sum(1 for keyword in budget_keywords if keyword in content_lower)
            cost_conscious_count = sum(1 for indicator in cost_conscious if indicator in content_lower)
            expensive_count = sum(1 for indicator in expensive_indicators if indicator in content_lower)
            
            # Calculate budget feasibility
            base_score = 0.7  # Default assumption
            
            if budget_mentions > 0:
                base_score = 0.8  # Good that budget is considered
            
            if cost_conscious_count > 0:
                base_score += 0.2  # Bonus for cost-conscious approach
            
            if expensive_count > 0:
                base_score -= 0.3  # Penalty for expensive requirements
            
            return max(0.0, min(base_score, 1.0))
            
        except Exception as e:
            logger.error(f"Budget feasibility analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_scalability(self, content: str) -> float:
        """Analyze scalability of the solution"""
        try:
            content_lower = content.lower()
            
            # Scalability indicators
            scalability_keywords = [
                'scalable', 'scalability', 'horizontal scaling', 'vertical scaling',
                'load balancing', 'distributed', 'microservices', 'cloud',
                'auto-scaling', 'elastic', 'performance', 'optimization'
            ]
            
            # Architecture patterns that support scalability
            scalable_patterns = [
                'microservices', 'api gateway', 'load balancer', 'caching',
                'database sharding', 'cdn', 'message queue', 'event-driven'
            ]
            
            scalability_count = sum(1 for keyword in scalability_keywords if keyword in content_lower)
            pattern_count = sum(1 for pattern in scalable_patterns if pattern in content_lower)
            
            # Calculate scalability score
            scalability_score = min((scalability_count + pattern_count) * 0.1, 0.8)
            
            # Base score for any solution
            base_score = 0.4
            
            total_score = base_score + scalability_score
            
            return min(total_score, 1.0)
            
        except Exception as e:
            logger.error(f"Scalability analysis failed: {str(e)}")
            return 0.0
    
    def _assess_risks(self, content: str) -> Dict[str, Any]:
        """Assess risks in the proposed solution"""
        try:
            content_lower = content.lower()
            
            risks = {
                'technical_risks': [],
                'resource_risks': [],
                'timeline_risks': [],
                'overall_risk_level': 'medium'
            }
            
            # Technical risks
            high_risk_tech = [
                'new technology', 'experimental', 'cutting edge', 'untested',
                'complex algorithm', 'machine learning', 'ai', 'blockchain'
            ]
            
            tech_risk_count = sum(1 for risk in high_risk_tech if risk in content_lower)
            if tech_risk_count > 2:
                risks['technical_risks'].append("High use of experimental/complex technologies")
            
            # Resource risks
            if 'team' not in content_lower and 'developer' not in content_lower:
                risks['resource_risks'].append("No clear team structure mentioned")
            
            # Timeline risks
            if 'timeline' not in content_lower and 'schedule' not in content_lower:
                risks['timeline_risks'].append("No timeline or schedule mentioned")
            
            # Dependency risks
            if 'third party' in content_lower or 'external api' in content_lower:
                risks['technical_risks'].append("Dependencies on third-party services")
            
            # Calculate overall risk level
            total_risks = len(risks['technical_risks']) + len(risks['resource_risks']) + len(risks['timeline_risks'])
            
            if total_risks >= 4:
                risks['overall_risk_level'] = 'high'
            elif total_risks >= 2:
                risks['overall_risk_level'] = 'medium'
            else:
                risks['overall_risk_level'] = 'low'
            
            return risks
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {str(e)}")
            return {'technical_risks': [], 'resource_risks': [], 'timeline_risks': [], 'overall_risk_level': 'medium'}
    
    def _llm_feasibility_analysis(self, content: str) -> Dict[str, Any]:
        """Use LLM for detailed feasibility analysis"""
        try:
            prompt = f"""
            Analyze the feasibility of the following project proposal. Consider technical complexity, 
            resource requirements, timeline, and overall viability for a hackathon/SIH project.
            
            Proposal: {content[:2000]}...
            
            Provide analysis on:
            1. Technical feasibility (0-10)
            2. Resource requirements (realistic/unrealistic)
            3. Timeline feasibility (0-10)
            4. Key challenges
            5. Success probability (0-10)
            
            Respond in JSON format.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse LLM response
            llm_analysis = response.choices[0].message.content
            
            return {
                'llm_analysis': llm_analysis,
                'analysis_method': 'gpt-3.5-turbo'
            }
            
        except Exception as e:
            logger.error(f"LLM feasibility analysis failed: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_overall_feasibility(self, results: Dict[str, Any]) -> float:
        """Calculate weighted overall feasibility score"""
        weights = {
            'technical_feasibility': 0.3,
            'resource_feasibility': 0.25,
            'timeline_feasibility': 0.2,
            'budget_feasibility': 0.15,
            'scalability_score': 0.1
        }
        
        overall_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in results and results[metric] > 0:
                overall_score += results[metric] * weight
                total_weight += weight
        
        # Risk penalty
        risk_level = results.get('risk_assessment', {}).get('overall_risk_level', 'medium')
        risk_penalty = {'low': 0.0, 'medium': 0.1, 'high': 0.2}.get(risk_level, 0.1)
        
        if total_weight > 0:
            final_score = (overall_score / total_weight) - risk_penalty
            return max(0.0, min(final_score, 1.0))
        else:
            return 0.0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on feasibility analysis"""
        recommendations = []
        
        overall_feasibility = results.get('overall_feasibility', 0.0)
        
        # Overall recommendations
        if overall_feasibility >= 0.8:
            recommendations.append("High feasibility project. Well-planned and realistic.")
        elif overall_feasibility >= 0.6:
            recommendations.append("Good feasibility with minor concerns to address.")
        elif overall_feasibility >= 0.4:
            recommendations.append("Moderate feasibility. Consider simplifying some aspects.")
        else:
            recommendations.append("Low feasibility. Major revision needed to make project viable.")
        
        # Specific recommendations
        if results.get('technical_feasibility', 0) < 0.5:
            recommendations.append("Technical complexity seems too high. Consider simpler solutions.")
        
        if results.get('resource_feasibility', 0) < 0.5:
            recommendations.append("Resource requirements may be unrealistic for the project scope.")
        
        if results.get('timeline_feasibility', 0) < 0.5:
            recommendations.append("Timeline appears unrealistic. Consider extending deadlines or reducing scope.")
        
        # Risk-based recommendations
        risk_level = results.get('risk_assessment', {}).get('overall_risk_level', 'medium')
        if risk_level == 'high':
            recommendations.append("High risk project. Have contingency plans ready.")
        
        return recommendations