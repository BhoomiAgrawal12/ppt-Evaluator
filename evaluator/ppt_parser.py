import os
import base64
import logging
from typing import Dict, List, Any
from llama_cloud_services import LlamaParse
from config import Config
import re
import json

logger = logging.getLogger(__name__)


class PPTParser:
    def __init__(self):
        self.llama_parser = LlamaParse(
            api_key=Config.LLAMA_CLOUD_API_KEY,
            num_workers=4,
            verbose=True,
            language="en"
        )
    
    def parse_ppt(self, file_path: str) -> Dict[str, Any]:
        """
        Parse PPT file and extract all content including text, images, and links
        """
        try:
            logger.info(f"Parsing PPT file: {file_path}")
            
            # Parse using LlamaParse - correct method
            result = self.llama_parser.parse(file_path)
            
            parsed_content = {
                'text': '',
                'images': [],
                'links': [],
                'slides': [],
                'metadata': {}
            }
            
            # Extract text content using get_markdown_documents
            markdown_documents = result.get_markdown_documents(split_by_page=True)
            
            # Process each page/document
            all_text = ""
            for i, doc in enumerate(markdown_documents):
                # Extract markdown text
                doc_text = doc.markdown if hasattr(doc, 'markdown') else str(doc)
                all_text += doc_text + "\n\n"
                
                # Create slide information
                slide_info = {
                    'slide_number': i + 1,
                    'content': doc_text,
                    'word_count': len(doc_text.split()),
                    'has_bullet_points': bool(re.search(r'[•\-\*]\s+', doc_text)),
                    'title': self._extract_slide_title(doc_text)
                }
                parsed_content['slides'].append(slide_info)
            
            parsed_content['text'] = all_text
            
            # Try to extract images if available
            try:
                image_documents = result.get_image_documents(
                    include_screenshot_images=True,
                    include_object_images=True
                )
                
                for img_doc in image_documents:
                    if hasattr(img_doc, 'image_bytes'):
                        # Convert image bytes to base64
                        img_b64 = base64.b64encode(img_doc.image_bytes).decode('utf-8')
                        image_info = {
                            'type': 'image',
                            'data': img_doc.image_bytes,
                            'format': 'unknown',
                            'slide_number': 0,
                            'description': getattr(img_doc, 'description', ''),
                            'base64': f"data:image/png;base64,{img_b64}"
                        }
                        parsed_content['images'].append(image_info)
            except Exception as img_error:
                logger.warning(f"Could not extract images: {str(img_error)}")
            
            # Extract links from text
            parsed_content['links'] = self._extract_links_from_text(parsed_content['text'])
            
            # Clean and structure the text
            parsed_content['text'] = self._clean_text(parsed_content['text'])
            
            logger.info(f"Successfully parsed PPT. Found {len(parsed_content['slides'])} slides, "
                       f"{len(parsed_content['images'])} images, {len(parsed_content['links'])} links")
            logger.info(f"Extracted text length: {len(parsed_content['text'])} characters")
            
            return parsed_content
            
        except Exception as e:
            error_msg = str(e)
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Error parsing PPT file: {error_msg}")
            logger.error(f"Traceback: {tb}")
            
            # Provide specific error messages for common issues
            if 'DNS resolution failed' in error_msg or 'Name or service not known' in error_msg:
                raise Exception("DNS resolution failed. Cannot reach LlamaParse API. Check internet connection and DNS settings.")
            elif '401' in error_msg or 'Unauthorized' in error_msg or 'Invalid token format' in error_msg:
                raise Exception("LlamaParse API key is invalid or expired. Please check your LLAMA_CLOUD_API_KEY in .env file.")
            elif not Config.LLAMA_CLOUD_API_KEY:
                raise Exception("LlamaParse API key not set. Please set LLAMA_CLOUD_API_KEY in your .env file.")
            else:
                raise Exception(f"Failed to parse PPT: {error_msg}")
    
    def _extract_images_from_extra_info(self, extra_info: Dict) -> List[Dict]:
        """Extract images from extra_info metadata"""
        images = []
        
        try:
            if 'images' in extra_info:
                for img_data in extra_info['images']:
                    image_info = {
                        'type': 'image',
                        'data': img_data.get('data', ''),
                        'format': img_data.get('format', 'unknown'),
                        'slide_number': img_data.get('slide', 0),
                        'description': img_data.get('alt_text', ''),
                        'size': img_data.get('size', {}),
                        'base64': self._convert_to_base64(img_data.get('data', ''))
                    }
                    images.append(image_info)
            
            # Also check for charts, diagrams, etc.
            if 'charts' in extra_info:
                for chart_data in extra_info['charts']:
                    chart_info = {
                        'type': 'chart',
                        'data': chart_data.get('data', ''),
                        'chart_type': chart_data.get('type', 'unknown'),
                        'slide_number': chart_data.get('slide', 0),
                        'title': chart_data.get('title', ''),
                        'base64': self._convert_to_base64(chart_data.get('data', ''))
                    }
                    images.append(chart_info)
                    
        except Exception as e:
            logger.warning(f"Error extracting images: {str(e)}")
        
        return images
    
    def _convert_to_base64(self, image_data: Any) -> str:
        """Convert image data to base64 string"""
        try:
            if isinstance(image_data, bytes):
                return base64.b64encode(image_data).decode('utf-8')
            elif isinstance(image_data, str) and image_data.startswith('data:image'):
                return image_data
            else:
                return ''
        except Exception:
            return ''
    
    def _extract_links_from_text(self, text: str) -> List[Dict]:
        """Extract URLs from text content"""
        links = []
        
        # URL patterns
        url_patterns = [
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            r'www\.(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            r'(?:github\.com|youtube\.com|youtu\.be|drive\.google\.com)[-\w./?&=%#]*'
        ]
        
        for pattern in url_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                link_info = {
                    'url': match,
                    'type': self._classify_link_type(match),
                    'context': self._get_link_context(text, match)
                }
                links.append(link_info)
        
        # Remove duplicates
        seen_urls = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def _classify_link_type(self, url: str) -> str:
        """Classify the type of link"""
        url_lower = url.lower()
        
        if 'github.com' in url_lower:
            return 'github'
        elif any(domain in url_lower for domain in ['youtube.com', 'youtu.be']):
            return 'demo_video'
        elif 'drive.google.com' in url_lower:
            return 'google_drive'
        elif any(domain in url_lower for domain in ['.pdf', '.doc', '.ppt']):
            return 'document'
        else:
            return 'other'
    
    def _get_link_context(self, text: str, url: str) -> str:
        """Get context around the link in the text"""
        try:
            url_index = text.find(url)
            if url_index == -1:
                return ""
            
            start = max(0, url_index - 100)
            end = min(len(text), url_index + len(url) + 100)
            context = text[start:end].strip()
            
            return context
        except Exception:
            return ""
    
    def _process_slides(self, text: str) -> List[Dict]:
        """Process and structure slide information"""
        slides = []
        
        # Simple slide detection based on common patterns
        slide_patterns = [
            r'slide\s+(\d+)',
            r'page\s+(\d+)',
            r'---+',  # Markdown-style slide separator
        ]
        
        # Split text into potential slides
        slide_parts = re.split(r'\n\s*---+\s*\n|\n\s*slide\s+\d+\s*\n', text, flags=re.IGNORECASE)
        
        for i, slide_content in enumerate(slide_parts):
            if slide_content.strip():
                slide_info = {
                    'slide_number': i + 1,
                    'content': slide_content.strip(),
                    'word_count': len(slide_content.split()),
                    'has_bullet_points': bool(re.search(r'[•\-\*]\s+', slide_content)),
                    'title': self._extract_slide_title(slide_content)
                }
                slides.append(slide_info)
        
        return slides
    
    def _extract_slide_title(self, slide_content: str) -> str:
        """Extract the title from slide content"""
        lines = slide_content.split('\n')
        
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if line and len(line) < 100:  # Likely a title
                return line
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize the extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with analysis
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]\"\'\/]', ' ', text)
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        return text.strip()