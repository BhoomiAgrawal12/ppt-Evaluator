import logging
import re
import numpy as np
from typing import Dict, List, Any, Tuple
import base64
from PIL import Image
import io

logger = logging.getLogger(__name__)


class AttractivenessEvaluator:
    def __init__(self):
        self.design_keywords = {
            'positive': [
                'clean', 'modern', 'elegant', 'professional', 'sleek', 'minimalist',
                'vibrant', 'colorful', 'attractive', 'beautiful', 'stunning',
                'user-friendly', 'intuitive', 'responsive', 'interactive'
            ],
            'negative': [
                'cluttered', 'messy', 'outdated', 'boring', 'plain', 'ugly',
                'confusing', 'overwhelming', 'difficult', 'hard to read'
            ]
        }
    
    def evaluate_attractiveness(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the visual attractiveness and design quality of the PPT
        """
        results = {
            'overall_attractiveness': 0.0,
            'visual_design_score': 0.0,
            'content_structure_score': 0.0,
            'color_scheme_score': 0.0,
            'typography_score': 0.0,
            'image_quality_score': 0.0,
            'layout_score': 0.0,
            'detailed_analysis': {},
            'recommendations': []
        }
        
        try:
            text_content = parsed_content.get('text', '')
            images = parsed_content.get('images', [])
            slides = parsed_content.get('slides', [])
            
            # Visual design analysis
            results['visual_design_score'] = self._analyze_visual_design(text_content)
            
            # Content structure analysis
            results['content_structure_score'] = self._analyze_content_structure(slides, text_content)
            
            # Color scheme analysis (if available)
            results['color_scheme_score'] = self._analyze_color_scheme(images, text_content)
            
            # Typography analysis
            results['typography_score'] = self._analyze_typography(text_content, slides)
            
            # Image quality analysis
            results['image_quality_score'] = self._analyze_image_quality(images)
            
            # Layout analysis
            results['layout_score'] = self._analyze_layout(slides, text_content)
            
            # Detailed analysis
            results['detailed_analysis'] = self._detailed_attractiveness_analysis(parsed_content)
            
            # Calculate overall attractiveness
            results['overall_attractiveness'] = self._calculate_overall_attractiveness(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            logger.error(f"Error in attractiveness evaluation: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_visual_design(self, text_content: str) -> float:
        """Analyze visual design elements mentioned in content"""
        try:
            content_lower = text_content.lower()
            
            # Design-related keywords
            design_terms = [
                'design', 'ui', 'ux', 'interface', 'user experience', 'visual',
                'graphic', 'layout', 'template', 'theme', 'style', 'aesthetic'
            ]
            
            # Modern design concepts
            modern_concepts = [
                'responsive', 'mobile-first', 'accessibility', 'usability',
                'wireframe', 'mockup', 'prototype', 'material design',
                'flat design', 'card layout', 'grid system'
            ]
            
            # Count design-related mentions
            design_count = sum(1 for term in design_terms if term in content_lower)
            modern_count = sum(1 for concept in modern_concepts if concept in content_lower)
            
            # Positive design keywords
            positive_count = sum(1 for word in self.design_keywords['positive'] if word in content_lower)
            negative_count = sum(1 for word in self.design_keywords['negative'] if word in content_lower)
            
            # Calculate score
            base_score = min((design_count + modern_count) * 0.1, 0.6)
            keyword_score = min(positive_count * 0.05, 0.3)
            penalty = min(negative_count * 0.05, 0.2)
            
            final_score = base_score + keyword_score - penalty + 0.1  # Base score
            
            return max(0.0, min(final_score, 1.0))
            
        except Exception as e:
            logger.error(f"Visual design analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_content_structure(self, slides: List[Dict], text_content: str) -> float:
        """Analyze content structure and organization"""
        try:
            if not slides:
                # Fallback to text analysis
                return self._analyze_text_structure(text_content)
            
            structure_score = 0.0
            
            # Slide count analysis
            slide_count = len(slides)
            if 5 <= slide_count <= 15:  # Optimal range for presentations
                structure_score += 0.3
            elif 3 <= slide_count <= 20:
                structure_score += 0.2
            else:
                structure_score += 0.1
            
            # Check for consistent slide structure
            has_titles = sum(1 for slide in slides if slide.get('title', '').strip())
            title_consistency = has_titles / max(slide_count, 1)
            structure_score += title_consistency * 0.2
            
            # Check for balanced content
            word_counts = [slide.get('word_count', 0) for slide in slides]
            if word_counts:
                avg_words = np.mean(word_counts)
                std_words = np.std(word_counts)
                
                # Good balance if std is not too high
                if std_words < avg_words * 0.5:  # Low variability
                    structure_score += 0.2
                else:
                    structure_score += 0.1
            
            # Check for bullet points usage
            bullet_slides = sum(1 for slide in slides if slide.get('has_bullet_points', False))
            if bullet_slides > 0:
                structure_score += 0.15
            
            # Progressive disclosure check
            if slide_count > 3:
                first_slide_words = slides[0].get('word_count', 0)
                last_slide_words = slides[-1].get('word_count', 0)
                
                # Good if conclusion is shorter than introduction
                if last_slide_words < first_slide_words:
                    structure_score += 0.15
            
            return min(structure_score, 1.0)
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_text_structure(self, text_content: str) -> float:
        """Analyze text structure when slide data is not available"""
        try:
            # Check for headings and structure
            structure_indicators = [
                r'\n#{1,6}\s+',  # Markdown headings
                r'\n\d+\.',     # Numbered lists
                r'\n[-*•]\s+',  # Bullet points
                r'\n[A-Z][^.]*:',  # Section headers
            ]
            
            structure_count = 0
            for pattern in structure_indicators:
                matches = len(re.findall(pattern, text_content))
                structure_count += matches
            
            # Paragraph analysis
            paragraphs = text_content.split('\n\n')
            paragraph_count = len([p for p in paragraphs if len(p.strip()) > 50])
            
            # Calculate structure score
            structure_score = min(structure_count * 0.05, 0.4)
            paragraph_score = min(paragraph_count * 0.02, 0.3)
            base_score = 0.3
            
            return min(structure_score + paragraph_score + base_score, 1.0)
            
        except Exception:
            return 0.5
    
    def _analyze_color_scheme(self, images: List[Dict], text_content: str) -> float:
        """Analyze color scheme and visual consistency"""
        try:
            score = 0.5  # Base score
            
            # Check for color mentions in text
            color_keywords = [
                'color', 'theme', 'brand', 'palette', 'scheme', 'consistent',
                'visual identity', 'brand colors', 'color theory'
            ]
            
            color_mentions = sum(1 for keyword in color_keywords 
                               if keyword in text_content.lower())
            
            if color_mentions > 0:
                score += min(color_mentions * 0.1, 0.3)
            
            # Basic image color analysis (if images have base64 data)
            if images:
                try:
                    color_analysis = self._analyze_image_colors(images)
                    if color_analysis.get('has_consistent_palette'):
                        score += 0.2
                except Exception as e:
                    logger.warning(f"Image color analysis failed: {str(e)}")
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Color scheme analysis failed: {str(e)}")
            return 0.5
    
    def _analyze_image_colors(self, images: List[Dict]) -> Dict[str, Any]:
        """Analyze colors in images"""
        try:
            # This is a simplified analysis
            # In a full implementation, you'd use PIL/OpenCV for detailed color analysis
            
            results = {
                'dominant_colors': [],
                'has_consistent_palette': False,
                'color_diversity': 0.0
            }
            
            processed_images = 0
            
            for img_data in images[:3]:  # Analyze first 3 images only
                base64_data = img_data.get('base64', '')
                if base64_data and base64_data.startswith('data:image'):
                    try:
                        # Extract base64 data
                        image_data = base64_data.split(',')[1]
                        image_bytes = base64.b64decode(image_data)
                        
                        # Open image with PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Simple color analysis (would be more sophisticated in practice)
                        # For now, just check if image was processed successfully
                        processed_images += 1
                        
                    except Exception as e:
                        logger.warning(f"Failed to process image: {str(e)}")
                        continue
            
            if processed_images > 0:
                results['has_consistent_palette'] = True  # Simplified assumption
                results['color_diversity'] = min(processed_images / 3.0, 1.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Image color analysis failed: {str(e)}")
            return {'dominant_colors': [], 'has_consistent_palette': False, 'color_diversity': 0.0}
    
    def _analyze_typography(self, text_content: str, slides: List[Dict]) -> float:
        """Analyze typography and text formatting"""
        try:
            score = 0.5  # Base score
            
            # Check for typography mentions
            typography_terms = [
                'font', 'typography', 'text', 'heading', 'title', 'readable',
                'legible', 'font size', 'font family', 'bold', 'italic'
            ]
            
            typo_mentions = sum(1 for term in typography_terms 
                              if term in text_content.lower())
            
            if typo_mentions > 0:
                score += min(typo_mentions * 0.05, 0.2)
            
            # Analyze text variety (if slides available)
            if slides:
                # Check for varied content lengths (good typography practice)
                word_counts = [slide.get('word_count', 0) for slide in slides]
                if word_counts and len(set(word_counts)) > 2:  # Variety in lengths
                    score += 0.15
                
                # Check for titles
                titled_slides = sum(1 for slide in slides if slide.get('title'))
                if titled_slides > len(slides) * 0.7:  # Most slides have titles
                    score += 0.15
            
            # Check for proper formatting indicators
            formatting_indicators = [
                r'\*\*[^*]+\*\*',  # Bold text
                r'\*[^*]+\*',      # Italic text
                r'#{1,6}\s+',      # Headers
                r'\n\s*[-*•]\s+',  # Lists
            ]
            
            formatting_count = 0
            for pattern in formatting_indicators:
                formatting_count += len(re.findall(pattern, text_content))
            
            formatting_score = min(formatting_count * 0.02, 0.2)
            score += formatting_score
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Typography analysis failed: {str(e)}")
            return 0.5
    
    def _analyze_image_quality(self, images: List[Dict]) -> float:
        """Analyze quality of images in the presentation"""
        try:
            if not images:
                return 0.3  # No images present
            
            score = 0.0
            total_images = len(images)
            
            # Basic quality indicators
            quality_factors = {
                'has_description': 0.2,
                'proper_format': 0.15,
                'reasonable_size': 0.15,
                'has_base64_data': 0.2,
                'appropriate_type': 0.3
            }
            
            for img in images:
                img_score = 0.0
                
                # Check for alt text/description
                if img.get('description') or img.get('alt_text'):
                    img_score += quality_factors['has_description']
                
                # Check format
                img_format = img.get('format', '').lower()
                if img_format in ['png', 'jpg', 'jpeg', 'svg', 'webp']:
                    img_score += quality_factors['proper_format']
                
                # Check if has base64 data (means image was properly extracted)
                if img.get('base64'):
                    img_score += quality_factors['has_base64_data']
                
                # Check image type
                img_type = img.get('type', '').lower()
                if img_type in ['image', 'chart', 'diagram', 'flowchart']:
                    img_score += quality_factors['appropriate_type']
                
                # Size check (basic)
                size_info = img.get('size', {})
                if size_info and isinstance(size_info, dict):
                    img_score += quality_factors['reasonable_size']
                
                score += img_score
            
            # Average score across all images
            average_score = score / total_images if total_images > 0 else 0
            
            # Bonus for having multiple images
            diversity_bonus = min(total_images * 0.05, 0.2)
            
            final_score = average_score + diversity_bonus
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Image quality analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_layout(self, slides: List[Dict], text_content: str) -> float:
        """Analyze layout and spatial organization"""
        try:
            score = 0.5  # Base score
            
            # Layout-related keywords
            layout_terms = [
                'layout', 'grid', 'alignment', 'spacing', 'margin', 'padding',
                'organized', 'structured', 'balanced', 'symmetry', 'hierarchy'
            ]
            
            layout_mentions = sum(1 for term in layout_terms 
                                if term in text_content.lower())
            
            if layout_mentions > 0:
                score += min(layout_mentions * 0.05, 0.2)
            
            # Analyze slide organization (if available)
            if slides:
                # Check for consistent slide lengths
                word_counts = [slide.get('word_count', 0) for slide in slides]
                if word_counts:
                    # Good layout has reasonable consistency
                    avg_words = np.mean(word_counts)
                    std_words = np.std(word_counts)
                    
                    if avg_words > 0 and std_words / avg_words < 0.6:  # Not too variable
                        score += 0.15
                
                # Check for proper slide progression
                if len(slides) >= 3:
                    # Good presentations often start broad, go detailed, then conclude
                    first_third = slides[:len(slides)//3]
                    last_third = slides[-len(slides)//3:]
                    
                    first_avg = np.mean([s.get('word_count', 0) for s in first_third])
                    last_avg = np.mean([s.get('word_count', 0) for s in last_third])
                    
                    if first_avg > 0 and last_avg <= first_avg * 1.2:  # Reasonable conclusion
                        score += 0.15
            
            # Check for structural elements
            structural_elements = [
                r'\n\s*[-*•]\s+',  # Bullet points
                r'\n\d+\.',        # Numbered lists
                r'\n#{1,6}\s+',    # Headers
                r'\n\s*\|\s*',     # Tables
            ]
            
            structure_count = 0
            for pattern in structural_elements:
                structure_count += len(re.findall(pattern, text_content))
            
            structure_score = min(structure_count * 0.02, 0.2)
            score += structure_score
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Layout analysis failed: {str(e)}")
            return 0.5
    
    def _detailed_attractiveness_analysis(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed analysis of attractiveness factors"""
        analysis = {
            'slide_count': len(parsed_content.get('slides', [])),
            'image_count': len(parsed_content.get('images', [])),
            'avg_words_per_slide': 0.0,
            'has_visual_elements': False,
            'content_balance_score': 0.0,
            'engagement_factors': []
        }
        
        try:
            slides = parsed_content.get('slides', [])
            images = parsed_content.get('images', [])
            text_content = parsed_content.get('text', '')
            
            # Calculate average words per slide
            if slides:
                total_words = sum(slide.get('word_count', 0) for slide in slides)
                analysis['avg_words_per_slide'] = total_words / len(slides)
            
            # Check for visual elements
            analysis['has_visual_elements'] = len(images) > 0
            
            # Content balance analysis
            if slides:
                word_counts = [slide.get('word_count', 0) for slide in slides]
                if word_counts:
                    # Good balance means not too much variance
                    cv = np.std(word_counts) / np.mean(word_counts) if np.mean(word_counts) > 0 else 1
                    analysis['content_balance_score'] = max(0, 1 - cv)
            
            # Engagement factors
            engagement_keywords = [
                'interactive', 'demo', 'example', 'case study', 'story',
                'question', 'quiz', 'poll', 'animation', 'transition'
            ]
            
            found_engagement = [keyword for keyword in engagement_keywords 
                              if keyword in text_content.lower()]
            analysis['engagement_factors'] = found_engagement
            
        except Exception as e:
            logger.error(f"Detailed attractiveness analysis failed: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _calculate_overall_attractiveness(self, results: Dict[str, Any]) -> float:
        """Calculate weighted overall attractiveness score"""
        weights = {
            'visual_design_score': 0.2,
            'content_structure_score': 0.2,
            'color_scheme_score': 0.15,
            'typography_score': 0.15,
            'image_quality_score': 0.15,
            'layout_score': 0.15
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
        """Generate recommendations based on attractiveness analysis"""
        recommendations = []
        
        overall_score = results.get('overall_attractiveness', 0.0)
        
        # Overall recommendations
        if overall_score >= 0.8:
            recommendations.append("Excellent presentation design and attractiveness")
        elif overall_score >= 0.6:
            recommendations.append("Good design with room for minor improvements")
        elif overall_score >= 0.4:
            recommendations.append("Average design. Consider improving visual appeal")
        else:
            recommendations.append("Poor design quality. Major improvements needed")
        
        # Specific recommendations
        if results.get('visual_design_score', 0) < 0.5:
            recommendations.append("Improve visual design elements and aesthetics")
        
        if results.get('content_structure_score', 0) < 0.5:
            recommendations.append("Better organize content structure and flow")
        
        if results.get('color_scheme_score', 0) < 0.5:
            recommendations.append("Consider improving color scheme and visual consistency")
        
        if results.get('typography_score', 0) < 0.5:
            recommendations.append("Improve typography and text formatting")
        
        if results.get('image_quality_score', 0) < 0.4:
            recommendations.append("Add more high-quality images or improve existing ones")
        
        if results.get('layout_score', 0) < 0.5:
            recommendations.append("Improve layout organization and spatial design")
        
        # Additional specific recommendations
        detailed_analysis = results.get('detailed_analysis', {})
        
        if detailed_analysis.get('image_count', 0) == 0:
            recommendations.append("Add relevant images to make presentation more engaging")
        
        if detailed_analysis.get('avg_words_per_slide', 0) > 100:
            recommendations.append("Consider reducing text per slide for better readability")
        
        if not detailed_analysis.get('engagement_factors'):
            recommendations.append("Add interactive or engaging elements to improve audience interest")
        
        return recommendations