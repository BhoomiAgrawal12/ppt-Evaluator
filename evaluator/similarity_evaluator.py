import logging
import re
import numpy as np
from typing import Dict, List, Any, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from config import Config

logger = logging.getLogger(__name__)

try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    logger.warning("Failed to download NLTK data")


class SimilarityEvaluator:
    def __init__(self):
        self.sentence_transformer = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            # Load sentence transformer model
            self.sentence_transformer = SentenceTransformer(Config.SENTENCE_TRANSFORMER_MODEL)
            logger.info(f"Loaded sentence transformer: {Config.SENTENCE_TRANSFORMER_MODEL}")
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer: {str(e)}")
        
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            self.stop_words = set()
    
    def evaluate_similarity(self, ppt_content: str, problem_statement: str) -> Dict[str, Any]:
        """
        Evaluate how well the PPT content addresses the problem statement
        """
        results = {
            'overall_similarity': 0.0,
            'semantic_similarity': 0.0,
            'keyword_similarity': 0.0,
            'coverage_score': 0.0,
            'relevance_score': 0.0,
            'detailed_analysis': {},
            'recommendations': []
        }
        
        try:
            # Preprocess texts
            ppt_clean = self._preprocess_text(ppt_content)
            ps_clean = self._preprocess_text(problem_statement)
            
            if not ppt_clean or not ps_clean:
                results['error'] = "Empty content after preprocessing"
                return results
            
            # Method 1: Semantic similarity using sentence transformers
            if self.sentence_transformer:
                semantic_sim = self._calculate_semantic_similarity(ppt_clean, ps_clean)
                results['semantic_similarity'] = semantic_sim
            
            # Method 2: Keyword-based similarity
            keyword_sim = self._calculate_keyword_similarity(ppt_clean, ps_clean)
            results['keyword_similarity'] = keyword_sim
            
            # Method 3: Coverage analysis
            coverage_score = self._analyze_coverage(ppt_clean, ps_clean)
            results['coverage_score'] = coverage_score
            
            # Method 4: Relevance scoring
            relevance_score = self._calculate_relevance_score(ppt_content, problem_statement)
            results['relevance_score'] = relevance_score
            
            # Detailed analysis
            results['detailed_analysis'] = self._detailed_analysis(ppt_content, problem_statement)
            
            # Calculate overall similarity
            results['overall_similarity'] = self._calculate_overall_similarity(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            logger.error(f"Error in similarity evaluation: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and periods
        text = re.sub(r'[^\w\s\.]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stop words
        if self.stop_words:
            words = word_tokenize(text)
            words = [word for word in words if word not in self.stop_words and len(word) > 2]
            text = ' '.join(words)
        
        return text
    
    def _calculate_semantic_similarity(self, ppt_content: str, ps_content: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        try:
            # Encode texts
            ppt_embedding = self.sentence_transformer.encode([ppt_content])
            ps_embedding = self.sentence_transformer.encode([ps_content])
            
            # Calculate cosine similarity
            similarity = cosine_similarity(ppt_embedding, ps_embedding)[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Semantic similarity calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_keyword_similarity(self, ppt_content: str, ps_content: str) -> float:
        """Calculate keyword-based similarity using TF-IDF"""
        try:
            # Fit TF-IDF on both documents
            corpus = [ppt_content, ps_content]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Keyword similarity calculation failed: {str(e)}")
            return 0.0
    
    def _analyze_coverage(self, ppt_content: str, ps_content: str) -> float:
        """Analyze how well PPT covers the problem statement requirements"""
        try:
            # Extract key phrases from problem statement
            ps_phrases = self._extract_key_phrases(ps_content)
            
            if not ps_phrases:
                return 0.0
            
            # Check coverage in PPT content
            covered_phrases = 0
            ppt_lower = ppt_content.lower()
            
            for phrase in ps_phrases:
                phrase_lower = phrase.lower()
                # Check for exact match or partial match
                if phrase_lower in ppt_lower or self._check_partial_match(phrase_lower, ppt_lower):
                    covered_phrases += 1
            
            coverage_score = covered_phrases / len(ps_phrases)
            return float(coverage_score)
            
        except Exception as e:
            logger.error(f"Coverage analysis failed: {str(e)}")
            return 0.0
    
    def _extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text"""
        # Simple approach: extract noun phrases and important keywords
        key_phrases = []
        
        # Extract multi-word terms (2-3 words)
        words = text.split()
        for i in range(len(words) - 1):
            phrase = ' '.join(words[i:i+2])
            if len(phrase) > 5 and phrase not in key_phrases:
                key_phrases.append(phrase)
        
        # Extract single important words (longer words)
        important_words = [word for word in words if len(word) > 5]
        key_phrases.extend(important_words)
        
        # Remove duplicates and return top phrases
        key_phrases = list(set(key_phrases))
        return key_phrases[:max_phrases]
    
    def _check_partial_match(self, phrase: str, text: str, threshold: float = 0.7) -> bool:
        """Check if phrase has partial match in text"""
        phrase_words = set(phrase.split())
        text_words = set(text.split())
        
        if not phrase_words:
            return False
        
        # Calculate Jaccard similarity
        intersection = len(phrase_words.intersection(text_words))
        union = len(phrase_words.union(text_words))
        
        if union == 0:
            return False
        
        jaccard_sim = intersection / union
        return jaccard_sim >= threshold
    
    def _calculate_relevance_score(self, ppt_content: str, problem_statement: str) -> float:
        """Calculate how relevant the PPT content is to solving the problem"""
        try:
            # Look for solution-oriented keywords in PPT
            solution_keywords = [
                'solution', 'approach', 'method', 'algorithm', 'implementation',
                'design', 'architecture', 'framework', 'system', 'platform',
                'technology', 'features', 'functionality', 'benefits', 'advantages'
            ]
            
            problem_keywords = [
                'problem', 'challenge', 'issue', 'difficulty', 'pain point',
                'requirement', 'need', 'objective', 'goal', 'target'
            ]
            
            ppt_lower = ppt_content.lower()
            ps_lower = problem_statement.lower()
            
            # Count solution keywords in PPT
            solution_count = sum(1 for keyword in solution_keywords if keyword in ppt_lower)
            
            # Count problem keywords in both texts
            problem_count_ppt = sum(1 for keyword in problem_keywords if keyword in ppt_lower)
            problem_count_ps = sum(1 for keyword in problem_keywords if keyword in ps_lower)
            
            # Calculate relevance score
            total_keywords = len(solution_keywords) + len(problem_keywords)
            found_keywords = solution_count + problem_count_ppt
            
            relevance_score = found_keywords / total_keywords
            
            # Bonus if PPT addresses problems mentioned in PS
            if problem_count_ps > 0 and problem_count_ppt > 0:
                relevance_score += 0.1
            
            return min(float(relevance_score), 1.0)
            
        except Exception as e:
            logger.error(f"Relevance score calculation failed: {str(e)}")
            return 0.0
    
    def _detailed_analysis(self, ppt_content: str, problem_statement: str) -> Dict[str, Any]:
        """Perform detailed analysis of content alignment"""
        analysis = {
            'content_length_ratio': 0.0,
            'common_terms': [],
            'missing_key_terms': [],
            'content_structure_score': 0.0,
            'technical_depth_score': 0.0
        }
        
        try:
            # Content length analysis
            ppt_words = len(ppt_content.split())
            ps_words = len(problem_statement.split())
            
            if ps_words > 0:
                analysis['content_length_ratio'] = ppt_words / ps_words
            
            # Find common terms
            ppt_terms = set(self._preprocess_text(ppt_content).split())
            ps_terms = set(self._preprocess_text(problem_statement).split())
            
            common_terms = ppt_terms.intersection(ps_terms)
            analysis['common_terms'] = list(common_terms)[:10]  # Top 10
            
            # Find missing key terms from PS
            important_ps_terms = [term for term in ps_terms if len(term) > 4]
            missing_terms = [term for term in important_ps_terms if term not in ppt_terms]
            analysis['missing_key_terms'] = missing_terms[:10]  # Top 10
            
            # Content structure score
            analysis['content_structure_score'] = self._analyze_content_structure(ppt_content)
            
            # Technical depth score
            analysis['technical_depth_score'] = self._analyze_technical_depth(ppt_content)
            
        except Exception as e:
            logger.error(f"Detailed analysis failed: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_content_structure(self, content: str) -> float:
        """Analyze the structure and organization of content"""
        try:
            sentences = sent_tokenize(content)
            
            if len(sentences) < 3:
                return 0.2
            
            score = 0.0
            
            # Check for good sentence variety
            sentence_lengths = [len(s.split()) for s in sentences]
            if len(set(sentence_lengths)) / len(sentence_lengths) > 0.3:
                score += 0.3
            
            # Check for transition words
            transition_words = ['however', 'therefore', 'furthermore', 'moreover', 'additionally']
            transition_count = sum(1 for word in transition_words if word in content.lower())
            score += min(transition_count / len(sentences), 0.3)
            
            # Check for structured content (headings, lists)
            if any(pattern in content for pattern in ['\n-', '\n*', '\n1.', '\n2.']):
                score += 0.4
            
            return min(score, 1.0)
            
        except Exception:
            return 0.0
    
    def _analyze_technical_depth(self, content: str) -> float:
        """Analyze technical depth and sophistication"""
        try:
            technical_terms = [
                'algorithm', 'implementation', 'architecture', 'framework', 'api',
                'database', 'server', 'client', 'protocol', 'interface', 'module',
                'component', 'library', 'function', 'method', 'class', 'object'
            ]
            
            content_lower = content.lower()
            technical_count = sum(1 for term in technical_terms if term in content_lower)
            
            # Normalize by content length
            words_count = len(content.split())
            if words_count == 0:
                return 0.0
            
            technical_density = technical_count / words_count
            
            # Score based on technical density
            if technical_density > 0.05:
                return 1.0
            elif technical_density > 0.02:
                return 0.7
            elif technical_density > 0.01:
                return 0.4
            else:
                return 0.2
                
        except Exception:
            return 0.0
    
    def _calculate_overall_similarity(self, results: Dict[str, Any]) -> float:
        """Calculate weighted overall similarity score"""
        weights = {
            'semantic_similarity': 0.4,
            'keyword_similarity': 0.25,
            'coverage_score': 0.2,
            'relevance_score': 0.15
        }
        
        overall_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in results and results[metric] > 0:
                overall_score += results[metric] * weight
                total_weight += weight
        
        if total_weight > 0:
            return overall_score / total_weight
        else:
            return 0.0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on similarity analysis"""
        recommendations = []
        
        overall_sim = results.get('overall_similarity', 0.0)
        
        if overall_sim >= 0.8:
            recommendations.append("Excellent alignment with problem statement.")
        elif overall_sim >= 0.6:
            recommendations.append("Good alignment with problem statement.")
        elif overall_sim >= 0.4:
            recommendations.append("Moderate alignment. Consider improving content relevance.")
        else:
            recommendations.append("Poor alignment with problem statement. Major revision needed.")
        
        # Specific recommendations
        if results.get('coverage_score', 0) < 0.5:
            recommendations.append("PPT doesn't cover key aspects of the problem statement.")
        
        if results.get('semantic_similarity', 0) < 0.4:
            recommendations.append("Content lacks semantic similarity to problem requirements.")
        
        if results.get('detailed_analysis', {}).get('missing_key_terms'):
            missing_terms = results['detailed_analysis']['missing_key_terms'][:3]
            recommendations.append(f"Consider including these key terms: {', '.join(missing_terms)}")
        
        return recommendations