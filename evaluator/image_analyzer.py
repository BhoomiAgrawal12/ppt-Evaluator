import logging
import base64
import io
import numpy as np
from typing import Dict, List, Any
from PIL import Image, ImageStat
import openai
from config import Config

logger = logging.getLogger(__name__)


class ImageAnalyzer:
    def __init__(self):
        self.client = None
        if Config.OPENAI_API_KEY:
            try:
                self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                logger.info("OpenAI client initialized for image analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {str(e)}")
        
        self.diagram_keywords = [
            'flowchart', 'diagram', 'architecture', 'workflow', 'process',
            'system design', 'data flow', 'er diagram', 'uml', 'wireframe',
            'mockup', 'prototype', 'schema', 'model', 'framework'
        ]
    
    def analyze_images(self, images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze images for flowcharts, diagrams, and technical content
        """
        results = {
            'total_images': len(images),
            'technical_diagrams': 0,
            'flowcharts': 0,
            'wireframes': 0,
            'screenshots': 0,
            'other_images': 0,
            'image_analysis': [],
            'overall_image_score': 0.0,
            'technical_depth_score': 0.0,
            'visual_quality_score': 0.0,
            'relevance_score': 0.0,
            'recommendations': []
        }
        
        try:
            if not images:
                results['recommendations'].append("No images found in presentation")
                return results
            
            # Analyze each image
            for i, image_data in enumerate(images):
                analysis = self._analyze_single_image(image_data, i)
                results['image_analysis'].append(analysis)
                
                # Categorize image
                self._categorize_image(analysis, results)
            
            # Calculate scores
            results['technical_depth_score'] = self._calculate_technical_depth(results)
            results['visual_quality_score'] = self._calculate_visual_quality(results)
            results['relevance_score'] = self._calculate_relevance_score(results)
            results['overall_image_score'] = self._calculate_overall_image_score(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            logger.error(f"Error in image analysis: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_single_image(self, image_data: Dict[str, Any], index: int) -> Dict[str, Any]:
        """
        Analyze a single image for technical content and quality
        """
        analysis = {
            'index': index,
            'type': image_data.get('type', 'unknown'),
            'format': image_data.get('format', 'unknown'),
            'description': image_data.get('description', ''),
            'slide_number': image_data.get('slide_number', 0),
            'has_base64': bool(image_data.get('base64')),
            'technical_score': 0.0,
            'quality_score': 0.0,
            'complexity_score': 0.0,
            'classification': 'other',
            'detected_elements': [],
            'ai_analysis': None,
            'issues': []
        }
        
        try:
            # Basic image info analysis
            analysis['technical_score'] = self._analyze_image_technical_content(image_data)
            analysis['quality_score'] = self._analyze_image_quality(image_data)
            analysis['complexity_score'] = self._analyze_image_complexity(image_data)
            
            # Classify image type
            analysis['classification'] = self._classify_image_type(image_data)
            
            # Detect technical elements
            analysis['detected_elements'] = self._detect_technical_elements(image_data)
            
            # AI-powered analysis (if available and image has base64)
            if self.client and image_data.get('base64'):
                analysis['ai_analysis'] = self._ai_image_analysis(image_data)
            
            # Check for issues
            analysis['issues'] = self._identify_image_issues(image_data, analysis)
            
        except Exception as e:
            logger.error(f"Error analyzing image {index}: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_image_technical_content(self, image_data: Dict[str, Any]) -> float:
        """Analyze technical content in image based on metadata and description"""
        try:
            score = 0.0
            
            # Check image type
            img_type = image_data.get('type', '').lower()
            if img_type in ['chart', 'diagram', 'flowchart']:
                score += 0.4
            elif img_type == 'image':
                score += 0.1
            
            # Check description for technical keywords
            description = image_data.get('description', '').lower()
            if description:
                technical_keywords = [
                    'architecture', 'diagram', 'flowchart', 'workflow', 'process',
                    'system', 'database', 'api', 'algorithm', 'model', 'framework',
                    'component', 'module', 'interface', 'protocol', 'schema'
                ]
                
                keyword_count = sum(1 for keyword in technical_keywords if keyword in description)
                score += min(keyword_count * 0.1, 0.4)
            
            # Check format appropriateness
            img_format = image_data.get('format', '').lower()
            if img_format in ['svg', 'png']:  # Good for diagrams
                score += 0.1
            elif img_format in ['jpg', 'jpeg']:  # Photos, less technical
                score += 0.05
            
            # Check if it's a chart
            if image_data.get('chart_type'):
                score += 0.3
                chart_type = image_data.get('chart_type', '').lower()
                if chart_type in ['bar', 'line', 'pie', 'scatter', 'flowchart']:
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Technical content analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_image_quality(self, image_data: Dict[str, Any]) -> float:
        """Analyze image quality based on available data"""
        try:
            score = 0.5  # Base score
            
            # Check if has base64 data (properly extracted)
            if image_data.get('base64'):
                score += 0.2
                
                # Try to analyze actual image if possible
                try:
                    base64_data = image_data['base64']
                    if base64_data.startswith('data:image'):
                        image_data_clean = base64_data.split(',')[1]
                        image_bytes = base64.b64decode(image_data_clean)
                        
                        # Open image with PIL
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Check image dimensions
                        width, height = image.size
                        if width >= 300 and height >= 200:  # Reasonable size
                            score += 0.2
                        
                        # Check if image is not too small
                        if width * height >= 50000:  # Decent resolution
                            score += 0.1
                            
                        # Basic quality metrics using PIL
                        if image.mode in ['RGB', 'RGBA']:
                            stat = ImageStat.Stat(image)
                            # Check if image has good color variation (not blank)
                            if any(std > 10 for std in stat.stddev):
                                score += 0.1
                
                except Exception as e:
                    logger.warning(f"Detailed image analysis failed: {str(e)}")
            
            # Check format quality
            img_format = image_data.get('format', '').lower()
            if img_format in ['png', 'svg']:  # Lossless formats
                score += 0.1
            elif img_format in ['jpg', 'jpeg', 'webp']:
                score += 0.05
            
            # Check if has description/alt text
            if image_data.get('description') or image_data.get('alt_text'):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Image quality analysis failed: {str(e)}")
            return 0.0
    
    def _analyze_image_complexity(self, image_data: Dict[str, Any]) -> float:
        """Analyze complexity of image content"""
        try:
            score = 0.0
            
            # Type-based complexity
            img_type = image_data.get('type', '').lower()
            type_complexity = {
                'flowchart': 0.8,
                'diagram': 0.7,
                'chart': 0.6,
                'wireframe': 0.7,
                'screenshot': 0.4,
                'image': 0.3
            }
            
            score += type_complexity.get(img_type, 0.3)
            
            # Description-based complexity
            description = image_data.get('description', '').lower()
            if description:
                complexity_indicators = [
                    'complex', 'detailed', 'multiple', 'various', 'several',
                    'interconnected', 'layered', 'hierarchical', 'nested'
                ]
                
                complexity_count = sum(1 for indicator in complexity_indicators 
                                     if indicator in description)
                score += min(complexity_count * 0.1, 0.3)
            
            # Chart complexity
            if image_data.get('chart_type'):
                chart_type = image_data.get('chart_type', '').lower()
                chart_complexity = {
                    'pie': 0.2,
                    'bar': 0.3,
                    'line': 0.4,
                    'scatter': 0.5,
                    'flowchart': 0.8,
                    'network': 0.9
                }
                score += chart_complexity.get(chart_type, 0.4)
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Image complexity analysis failed: {str(e)}")
            return 0.0
    
    def _classify_image_type(self, image_data: Dict[str, Any]) -> str:
        """Classify image into technical categories"""
        try:
            # Check explicit type first
            img_type = image_data.get('type', '').lower()
            if img_type in ['flowchart', 'diagram', 'chart', 'wireframe']:
                return img_type
            
            # Check description for classification clues
            description = image_data.get('description', '').lower()
            title = image_data.get('title', '').lower()
            combined_text = f"{description} {title}".lower()
            
            # Classification rules
            if any(keyword in combined_text for keyword in ['flowchart', 'flow chart', 'flow diagram']):
                return 'flowchart'
            elif any(keyword in combined_text for keyword in ['architecture', 'system diagram', 'er diagram', 'uml']):
                return 'technical_diagram'
            elif any(keyword in combined_text for keyword in ['wireframe', 'mockup', 'prototype', 'ui design']):
                return 'wireframe'
            elif any(keyword in combined_text for keyword in ['screenshot', 'screen shot', 'app screen']):
                return 'screenshot'
            elif any(keyword in combined_text for keyword in ['chart', 'graph', 'plot', 'bar chart', 'pie chart']):
                return 'chart'
            elif image_data.get('chart_type'):
                return 'chart'
            else:
                return 'other'
                
        except Exception as e:
            logger.error(f"Image classification failed: {str(e)}")
            return 'other'
    
    def _detect_technical_elements(self, image_data: Dict[str, Any]) -> List[str]:
        """Detect technical elements in image based on metadata"""
        elements = []
        
        try:
            description = image_data.get('description', '').lower()
            title = image_data.get('title', '').lower()
            combined_text = f"{description} {title}"
            
            # Technical elements to detect
            technical_elements = {
                'database': ['database', 'db', 'sql', 'table', 'schema'],
                'api': ['api', 'rest', 'endpoint', 'service', 'microservice'],
                'user_interface': ['ui', 'interface', 'button', 'form', 'menu'],
                'server': ['server', 'backend', 'infrastructure', 'cloud'],
                'workflow': ['workflow', 'process', 'step', 'procedure'],
                'algorithm': ['algorithm', 'logic', 'decision', 'condition'],
                'data_flow': ['data flow', 'pipeline', 'stream', 'transfer'],
                'network': ['network', 'connection', 'protocol', 'communication']
            }
            
            for element_type, keywords in technical_elements.items():
                if any(keyword in combined_text for keyword in keywords):
                    elements.append(element_type)
            
        except Exception as e:
            logger.error(f"Technical element detection failed: {str(e)}")
        
        return elements
    
    def _ai_image_analysis(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze image content (if OpenAI available)"""
        try:
            base64_data = image_data.get('base64', '')
            if not base64_data or not base64_data.startswith('data:image'):
                return {'error': 'No valid base64 image data'}
            
            # Use OpenAI Vision API for image analysis
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Analyze this image for technical content. Identify:
                                1. Type of diagram/image (flowchart, architecture, wireframe, etc.)
                                2. Technical elements present
                                3. Complexity level (1-10)
                                4. Quality assessment
                                5. Relevance to software/technical projects
                                
                                Respond in JSON format."""
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": base64_data}
                            }
                        ]
                    }
                ],
                max_tokens=300
            )
            
            ai_analysis = response.choices[0].message.content
            
            return {
                'ai_response': ai_analysis,
                'model_used': 'gpt-4-vision-preview',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"AI image analysis failed: {str(e)}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _identify_image_issues(self, image_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Identify potential issues with images"""
        issues = []
        
        try:
            # Check if image has no base64 data
            if not image_data.get('base64'):
                issues.append("Image not properly extracted or corrupted")
            
            # Check if no description
            if not image_data.get('description') and not image_data.get('alt_text'):
                issues.append("Missing description or alt text")
            
            # Check quality score
            if analysis.get('quality_score', 0) < 0.3:
                issues.append("Low image quality detected")
            
            # Check technical relevance
            if analysis.get('technical_score', 0) < 0.2:
                issues.append("Low technical relevance")
            
            # Check format
            img_format = image_data.get('format', '').lower()
            if img_format in ['bmp', 'tiff', 'gif']:
                issues.append("Suboptimal image format for presentations")
            
            # Check classification
            if analysis.get('classification') == 'other':
                issues.append("Could not classify image type")
            
        except Exception as e:
            logger.error(f"Issue identification failed: {str(e)}")
        
        return issues
    
    def _categorize_image(self, analysis: Dict[str, Any], results: Dict[str, Any]):
        """Categorize analyzed image"""
        classification = analysis.get('classification', 'other')
        
        if classification == 'flowchart':
            results['flowcharts'] += 1
        elif classification in ['technical_diagram', 'diagram']:
            results['technical_diagrams'] += 1
        elif classification == 'wireframe':
            results['wireframes'] += 1
        elif classification == 'screenshot':
            results['screenshots'] += 1
        else:
            results['other_images'] += 1
    
    def _calculate_technical_depth(self, results: Dict[str, Any]) -> float:
        """Calculate overall technical depth score"""
        try:
            total_images = results.get('total_images', 0)
            if total_images == 0:
                return 0.0
            
            # Weight different image types
            weights = {
                'flowcharts': 0.4,
                'technical_diagrams': 0.35,
                'wireframes': 0.2,
                'screenshots': 0.1,
                'other_images': 0.05
            }
            
            weighted_score = 0.0
            for img_type, weight in weights.items():
                count = results.get(img_type, 0)
                weighted_score += (count / total_images) * weight
            
            # Bonus for having technical elements
            technical_elements_found = 0
            for analysis in results.get('image_analysis', []):
                technical_elements_found += len(analysis.get('detected_elements', []))
            
            element_bonus = min(technical_elements_found * 0.05, 0.3)
            
            return min(weighted_score + element_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Technical depth calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_visual_quality(self, results: Dict[str, Any]) -> float:
        """Calculate overall visual quality score"""
        try:
            image_analyses = results.get('image_analysis', [])
            if not image_analyses:
                return 0.0
            
            total_quality = sum(analysis.get('quality_score', 0) for analysis in image_analyses)
            avg_quality = total_quality / len(image_analyses)
            
            return avg_quality
            
        except Exception as e:
            logger.error(f"Visual quality calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_relevance_score(self, results: Dict[str, Any]) -> float:
        """Calculate relevance score for technical projects"""
        try:
            image_analyses = results.get('image_analysis', [])
            if not image_analyses:
                return 0.0
            
            total_technical = sum(analysis.get('technical_score', 0) for analysis in image_analyses)
            avg_technical = total_technical / len(image_analyses)
            
            # Bonus for having diverse technical images
            technical_types = results['flowcharts'] + results['technical_diagrams'] + results['wireframes']
            total_images = results.get('total_images', 0)
            
            if total_images > 0:
                diversity_bonus = min((technical_types / total_images), 0.3)
            else:
                diversity_bonus = 0
            
            return min(avg_technical + diversity_bonus, 1.0)
            
        except Exception as e:
            logger.error(f"Relevance score calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_overall_image_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall image score"""
        weights = {
            'technical_depth_score': 0.4,
            'visual_quality_score': 0.3,
            'relevance_score': 0.3
        }
        
        overall_score = 0.0
        total_weight = 0.0
        
        for metric, weight in weights.items():
            if metric in results:
                overall_score += results[metric] * weight
                total_weight += weight
        
        if total_weight > 0:
            return overall_score / total_weight
        else:
            return 0.0
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on image analysis"""
        recommendations = []
        
        total_images = results.get('total_images', 0)
        overall_score = results.get('overall_image_score', 0.0)
        
        # Overall recommendations
        if overall_score >= 0.8:
            recommendations.append("Excellent use of technical diagrams and images")
        elif overall_score >= 0.6:
            recommendations.append("Good image quality with minor improvements possible")
        elif overall_score >= 0.4:
            recommendations.append("Average image usage. Consider adding more technical diagrams")
        else:
            recommendations.append("Poor image quality/relevance. Major improvements needed")
        
        # Specific recommendations
        if total_images == 0:
            recommendations.append("Add technical diagrams, flowcharts, or architecture diagrams")
        elif total_images < 3:
            recommendations.append("Consider adding more visual elements to support your solution")
        
        if results.get('flowcharts', 0) == 0:
            recommendations.append("Add flowcharts to illustrate processes or algorithms")
        
        if results.get('technical_diagrams', 0) == 0:
            recommendations.append("Include system architecture or technical diagrams")
        
        if results.get('technical_depth_score', 0) < 0.5:
            recommendations.append("Increase technical depth of visual content")
        
        if results.get('visual_quality_score', 0) < 0.5:
            recommendations.append("Improve image quality and resolution")
        
        # Check for common issues
        issues_count = 0
        for analysis in results.get('image_analysis', []):
            issues_count += len(analysis.get('issues', []))
        
        if issues_count > 0:
            recommendations.append(f"Fix {issues_count} image-related issues detected")
        
        return recommendations