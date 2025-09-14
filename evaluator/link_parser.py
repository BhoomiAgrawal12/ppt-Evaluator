import logging
import requests
import re
from typing import Dict, List, Any
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


class LinkParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
    
    def analyze_links(self, links: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all links found in the PPT
        """
        results = {
            'total_links': len(links),
            'link_analysis': [],
            'demo_videos': [],
            'github_repos': [],
            'documentation': [],
            'other_links': [],
            'broken_links': [],
            'link_quality_score': 0.0,
            'recommendations': []
        }
        
        try:
            if not links:
                results['recommendations'].append("No links found in presentation")
                return results
            
            # Analyze each link
            for link_info in links:
                analysis = self._analyze_single_link(link_info)
                results['link_analysis'].append(analysis)
                
                # Categorize links
                self._categorize_link(analysis, results)
                
                # Small delay to avoid overwhelming servers
                time.sleep(0.5)
            
            # Calculate overall quality score
            results['link_quality_score'] = self._calculate_link_quality_score(results)
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
        except Exception as e:
            logger.error(f"Error in link analysis: {str(e)}")
            results['error'] = str(e)
        
        return results
    
    def _analyze_single_link(self, link_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single link for accessibility, relevance, and quality
        """
        url = link_info.get('url', '')
        link_type = link_info.get('type', 'other')
        
        analysis = {
            'url': url,
            'original_type': link_type,
            'status': 'unknown',
            'response_time': None,
            'final_url': url,
            'title': '',
            'description': '',
            'is_accessible': False,
            'content_analysis': {},
            'quality_score': 0.0,
            'issues': []
        }
        
        try:
            # Basic URL validation
            if not self._is_valid_url(url):
                analysis['status'] = 'invalid_url'
                analysis['issues'].append('Invalid URL format')
                return analysis
            
            # Check if URL is accessible
            start_time = time.time()
            response = self._make_request(url)
            
            if response:
                analysis['response_time'] = time.time() - start_time
                analysis['status'] = f"status_{response.status_code}"
                analysis['final_url'] = response.url
                analysis['is_accessible'] = response.status_code == 200
                
                if response.status_code == 200:
                    # Extract content information
                    content_info = self._extract_content_info(response, url)
                    analysis.update(content_info)
                    
                    # Analyze content based on link type
                    analysis['content_analysis'] = self._analyze_link_content(response, link_type, url)
                else:
                    analysis['issues'].append(f"HTTP {response.status_code}")
            else:
                analysis['status'] = 'request_failed'
                analysis['issues'].append('Failed to access URL')
            
            # Calculate quality score
            analysis['quality_score'] = self._calculate_single_link_quality(analysis)
            
        except Exception as e:
            analysis['status'] = 'error'
            analysis['issues'].append(f"Analysis error: {str(e)}")
            logger.warning(f"Error analyzing link {url}: {str(e)}")
        
        return analysis
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def _make_request(self, url: str) -> requests.Response:
        """Make HTTP request with error handling"""
        try:
            # Ensure URL has scheme
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            return response
        except requests.RequestException as e:
            logger.warning(f"Request failed for {url}: {str(e)}")
            return None
    
    def _extract_content_info(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Extract basic content information from response"""
        info = {
            'title': '',
            'description': '',
            'content_type': response.headers.get('content-type', ''),
            'content_length': response.headers.get('content-length', 0)
        }
        
        try:
            if 'text/html' in info['content_type']:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    info['title'] = title_tag.get_text().strip()
                
                # Extract description
                desc_tag = soup.find('meta', attrs={'name': 'description'})
                if desc_tag:
                    info['description'] = desc_tag.get('content', '').strip()
                
                # Extract Open Graph data
                og_title = soup.find('meta', property='og:title')
                if og_title and not info['title']:
                    info['title'] = og_title.get('content', '').strip()
                
                og_desc = soup.find('meta', property='og:description')
                if og_desc and not info['description']:
                    info['description'] = og_desc.get('content', '').strip()
        
        except Exception as e:
            logger.warning(f"Error extracting content info from {url}: {str(e)}")
        
        return info
    
    def _analyze_link_content(self, response: requests.Response, link_type: str, url: str) -> Dict[str, Any]:
        """Analyze content based on link type"""
        analysis = {
            'relevance_score': 0.0,
            'content_quality': 0.0,
            'specific_analysis': {}
        }
        
        try:
            if link_type == 'github':
                analysis['specific_analysis'] = self._analyze_github_repo(response, url)
            elif link_type == 'demo_video':
                analysis['specific_analysis'] = self._analyze_video_link(response, url)
            elif link_type == 'google_drive':
                analysis['specific_analysis'] = self._analyze_drive_link(response, url)
            else:
                analysis['specific_analysis'] = self._analyze_general_link(response, url)
            
            # Calculate relevance and quality scores
            analysis['relevance_score'] = self._calculate_content_relevance(response, url)
            analysis['content_quality'] = self._calculate_content_quality(response, url)
            
        except Exception as e:
            logger.warning(f"Error analyzing link content {url}: {str(e)}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _analyze_github_repo(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Analyze GitHub repository"""
        analysis = {
            'is_valid_repo': False,
            'has_readme': False,
            'has_commits': False,
            'language_detected': '',
            'repo_activity': 'unknown'
        }
        
        try:
            if 'github.com' in url and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Check if it's a valid repo page
                if soup.find('div', {'class': 'repository-content'}):
                    analysis['is_valid_repo'] = True
                
                # Check for README
                if soup.find('div', {'id': 'readme'}):
                    analysis['has_readme'] = True
                
                # Check for commits
                commit_count = soup.find('span', {'class': 'num text-emphasized'})
                if commit_count:
                    analysis['has_commits'] = True
                
                # Detect primary language
                lang_element = soup.find('span', {'class': 'color-fg-default text-bold mr-1'})
                if lang_element:
                    analysis['language_detected'] = lang_element.get_text().strip()
        
        except Exception as e:
            logger.warning(f"Error analyzing GitHub repo {url}: {str(e)}")
        
        return analysis
    
    def _analyze_video_link(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Analyze video link (YouTube, etc.)"""
        analysis = {
            'platform': 'unknown',
            'is_accessible': False,
            'title': '',
            'duration': '',
            'view_count': ''
        }
        
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                analysis['platform'] = 'youtube'
                
                if response.status_code == 200:
                    analysis['is_accessible'] = True
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract title
                    title_element = soup.find('meta', property='og:title')
                    if title_element:
                        analysis['title'] = title_element.get('content', '')
                    
                    # Try to extract other metadata
                    duration_element = soup.find('meta', {'itemprop': 'duration'})
                    if duration_element:
                        analysis['duration'] = duration_element.get('content', '')
        
        except Exception as e:
            logger.warning(f"Error analyzing video link {url}: {str(e)}")
        
        return analysis
    
    def _analyze_drive_link(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Analyze Google Drive link"""
        analysis = {
            'is_accessible': False,
            'file_type': 'unknown',
            'is_public': False
        }
        
        try:
            if 'drive.google.com' in url:
                analysis['is_accessible'] = response.status_code == 200
                
                if 'sharing' in response.text.lower():
                    analysis['is_public'] = True
                
                # Try to detect file type from URL
                if '/document/' in url:
                    analysis['file_type'] = 'document'
                elif '/presentation/' in url:
                    analysis['file_type'] = 'presentation'
                elif '/spreadsheets/' in url:
                    analysis['file_type'] = 'spreadsheet'
        
        except Exception as e:
            logger.warning(f"Error analyzing Drive link {url}: {str(e)}")
        
        return analysis
    
    def _analyze_general_link(self, response: requests.Response, url: str) -> Dict[str, Any]:
        """Analyze general web link"""
        analysis = {
            'content_type': response.headers.get('content-type', ''),
            'has_meaningful_content': False,
            'word_count': 0
        }
        
        try:
            if 'text/html' in analysis['content_type']:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                words = text.split()
                analysis['word_count'] = len(words)
                
                if len(words) > 100:  # Arbitrary threshold for meaningful content
                    analysis['has_meaningful_content'] = True
        
        except Exception as e:
            logger.warning(f"Error analyzing general link {url}: {str(e)}")
        
        return analysis
    
    def _calculate_content_relevance(self, response: requests.Response, url: str) -> float:
        """Calculate how relevant the content is to a technical project"""
        relevance_keywords = [
            'project', 'demo', 'prototype', 'implementation', 'code',
            'github', 'repository', 'documentation', 'api', 'tutorial',
            'technology', 'solution', 'development', 'programming'
        ]
        
        try:
            content_text = response.text.lower()
            keyword_count = sum(1 for keyword in relevance_keywords if keyword in content_text)
            
            # Normalize score
            max_score = len(relevance_keywords)
            return min(keyword_count / max_score, 1.0)
        
        except:
            return 0.0
    
    def _calculate_content_quality(self, response: requests.Response, url: str) -> float:
        """Calculate content quality score"""
        quality_score = 0.5  # Base score
        
        try:
            # Check response time (faster = better)
            if hasattr(response, 'elapsed'):
                response_time = response.elapsed.total_seconds()
                if response_time < 2:
                    quality_score += 0.1
                elif response_time > 10:
                    quality_score -= 0.2
            
            # Check if HTTPS
            if response.url.startswith('https://'):
                quality_score += 0.1
            
            # Check content length
            content_length = len(response.content)
            if content_length > 1000:  # Has substantial content
                quality_score += 0.2
            
            # Check if it's a known reliable domain
            reliable_domains = [
                'github.com', 'youtube.com', 'drive.google.com', 'docs.google.com',
                'medium.com', 'dev.to', 'stackoverflow.com'
            ]
            
            parsed_url = urlparse(response.url)
            if any(domain in parsed_url.netloc for domain in reliable_domains):
                quality_score += 0.2
            
        except Exception as e:
            logger.warning(f"Error calculating content quality for {url}: {str(e)}")
        
        return min(quality_score, 1.0)
    
    def _calculate_single_link_quality(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall quality score for a single link"""
        score = 0.0
        
        # Accessibility score (40% weight)
        if analysis['is_accessible']:
            score += 0.4
        
        # Response time score (20% weight)
        if analysis['response_time'] is not None:
            if analysis['response_time'] < 2:
                score += 0.2
            elif analysis['response_time'] < 5:
                score += 0.1
        
        # Content analysis score (40% weight)
        content_analysis = analysis.get('content_analysis', {})
        if content_analysis:
            relevance = content_analysis.get('relevance_score', 0)
            quality = content_analysis.get('content_quality', 0)
            score += (relevance + quality) * 0.2
        
        return min(score, 1.0)
    
    def _categorize_link(self, analysis: Dict[str, Any], results: Dict[str, Any]):
        """Categorize analyzed link into appropriate category"""
        url = analysis['url']
        link_type = analysis['original_type']
        
        if not analysis['is_accessible']:
            results['broken_links'].append(analysis)
            return
        
        if link_type == 'github':
            results['github_repos'].append(analysis)
        elif link_type == 'demo_video':
            results['demo_videos'].append(analysis)
        elif link_type in ['google_drive', 'document']:
            results['documentation'].append(analysis)
        else:
            results['other_links'].append(analysis)
    
    def _calculate_link_quality_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall link quality score"""
        if results['total_links'] == 0:
            return 0.0
        
        total_score = 0.0
        scored_links = 0
        
        for link_analysis in results['link_analysis']:
            if 'quality_score' in link_analysis:
                total_score += link_analysis['quality_score']
                scored_links += 1
        
        if scored_links == 0:
            return 0.0
        
        avg_quality = total_score / scored_links
        
        # Bonus for having diverse link types
        link_types = set()
        if results['github_repos']:
            link_types.add('github')
        if results['demo_videos']:
            link_types.add('demo')
        if results['documentation']:
            link_types.add('docs')
        
        diversity_bonus = len(link_types) * 0.05
        
        # Penalty for broken links
        broken_penalty = len(results['broken_links']) * 0.1
        
        final_score = avg_quality + diversity_bonus - broken_penalty
        
        return max(0.0, min(final_score, 1.0))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on link analysis"""
        recommendations = []
        
        # Overall link quality
        quality_score = results.get('link_quality_score', 0.0)
        
        if quality_score >= 0.8:
            recommendations.append("Excellent link quality and diversity")
        elif quality_score >= 0.6:
            recommendations.append("Good link quality with room for improvement")
        elif quality_score >= 0.4:
            recommendations.append("Average link quality. Consider improving links")
        else:
            recommendations.append("Poor link quality. Review and update links")
        
        # Specific recommendations
        if not results['demo_videos']:
            recommendations.append("Consider adding demo video links to showcase the project")
        
        if not results['github_repos']:
            recommendations.append("Add GitHub repository links to demonstrate code implementation")
        
        if results['broken_links']:
            broken_count = len(results['broken_links'])
            recommendations.append(f"Fix {broken_count} broken link(s)")
        
        if results['total_links'] == 0:
            recommendations.append("Add relevant links (GitHub, demo videos, documentation)")
        elif results['total_links'] < 3:
            recommendations.append("Consider adding more supporting links for better credibility")
        
        return recommendations