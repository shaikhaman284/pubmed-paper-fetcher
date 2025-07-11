"""
PubMed API Client for fetching research papers.
"""

import requests
import time
from typing import List, Dict, Optional, Any
from lxml import etree
import logging

logger = logging.getLogger(__name__)


class PubMedAPIClient:
    """Client for interacting with PubMed API (E-utilities)."""
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    def __init__(self, email: Optional[str] = None, tool: str = "pubmed-paper-fetcher"):
        """
        Initialize the PubMed API client.
        
        Args:
            email: Your email address (recommended by NCBI)
            tool: Name of your tool (for NCBI usage tracking)
        """
        self.email = email
        self.tool = tool
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> requests.Response:
        """
        Make a request to the PubMed API with rate limiting.
        
        Args:
            endpoint: API endpoint (esearch, efetch, etc.)
            params: Query parameters
            
        Returns:
            Response object
        """
        url = f"{self.BASE_URL}/{endpoint}.fcgi"
        
        # Add common parameters
        params.update({
            'tool': self.tool,
            'email': self.email or 'user@example.com'
        })
        
        logger.debug(f"Making request to {url} with params: {params}")
        
        # Rate limiting: NCBI allows 3 requests per second
        time.sleep(0.34)  # ~3 requests per second
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers using PubMed and return PubMed IDs.
        
        Args:
            query: Search query (supports PubMed syntax)
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        params = {
            'db': 'pubmed',
            'term': query,
            'retmax': max_results,
            'retmode': 'xml'
        }
        
        response = self._make_request('esearch', params)
        
        # Parse XML response
        root = etree.fromstring(response.content)
        
        # Extract PubMed IDs
        pubmed_ids = []
        for id_elem in root.xpath('.//Id'):
            if id_elem.text:
                pubmed_ids.append(id_elem.text)
        
        logger.info(f"Found {len(pubmed_ids)} papers for query: {query}")
        return pubmed_ids
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch detailed information for papers by their PubMed IDs.
        
        Args:
            pubmed_ids: List of PubMed IDs
            
        Returns:
            List of paper details
        """
        if not pubmed_ids:
            return []
        
        # Process IDs in batches to avoid URL length limits
        batch_size = 200
        all_papers = []
        
        for i in range(0, len(pubmed_ids), batch_size):
            batch_ids = pubmed_ids[i:i + batch_size]
            id_list = ','.join(batch_ids)
            
            params = {
                'db': 'pubmed',
                'id': id_list,
                'retmode': 'xml',
                'rettype': 'abstract'
            }
            
            response = self._make_request('efetch', params)
            papers = self._parse_paper_details(response.content)
            all_papers.extend(papers)
        
        return all_papers
    
    def _parse_paper_details(self, xml_content: bytes) -> List[Dict[str, Any]]:
        """
        Parse XML response from efetch to extract paper details.
        
        Args:
            xml_content: XML response content
            
        Returns:
            List of paper details dictionaries
        """
        root = etree.fromstring(xml_content)
        papers = []
        
        # Find all PubmedArticle elements
        for article in root.xpath('.//PubmedArticle'):
            paper_data = {}
            
            # Extract PubMed ID
            pmid_elem = article.xpath('.//PMID')[0]
            paper_data['pubmed_id'] = pmid_elem.text
            
            # Extract title
            title_elem = article.xpath('.//ArticleTitle')
            if title_elem:
                paper_data['title'] = self._extract_text(title_elem[0])
            else:
                paper_data['title'] = 'No title available'
            
            # Extract publication date
            pub_date = self._extract_publication_date(article)
            paper_data['publication_date'] = pub_date
            
            # Extract authors and affiliations
            authors = self._extract_authors(article)
            paper_data['authors'] = authors
            
            # Extract corresponding author email
            paper_data['corresponding_author_email'] = self._extract_corresponding_author_email(article)
            
            papers.append(paper_data)
        
        return papers
    
    def _extract_text(self, element) -> str:
        """Extract all text from an XML element, handling nested tags."""
        if element is None:
            return ""
        
        # Get text content including nested elements
        text_parts = []
        if element.text:
            text_parts.append(element.text)
        
        for child in element:
            text_parts.append(self._extract_text(child))
            if child.tail:
                text_parts.append(child.tail)
        
        return ''.join(text_parts).strip()
    
    def _extract_publication_date(self, article) -> str:
        """Extract publication date from article XML."""
        # Try different date elements
        date_elements = [
            './/PubDate',
            './/ArticleDate',
            './/DateCompleted',
            './/DateRevised'
        ]
        
        for date_path in date_elements:
            date_elem = article.xpath(date_path)
            if date_elem:
                date_elem = date_elem[0]
                
                # Try to extract year, month, day
                year = self._get_element_text(date_elem, 'Year')
                month = self._get_element_text(date_elem, 'Month')
                day = self._get_element_text(date_elem, 'Day')
                
                if year:
                    date_parts = [year]
                    if month:
                        date_parts.append(month.zfill(2))
                    if day:
                        date_parts.append(day.zfill(2))
                    
                    return '-'.join(date_parts)
        
        return 'Unknown'
    
    def _extract_authors(self, article) -> List[Dict[str, str]]:
        """Extract author information from article XML."""
        authors = []
        
        # Find all authors
        for author_elem in article.xpath('.//Author'):
            author_data = {}
            
            # Extract name
            last_name = self._get_element_text(author_elem, 'LastName')
            first_name = self._get_element_text(author_elem, 'ForeName')
            initials = self._get_element_text(author_elem, 'Initials')
            
            if last_name:
                full_name = last_name
                if first_name:
                    full_name = f"{first_name} {last_name}"
                elif initials:
                    full_name = f"{initials} {last_name}"
                author_data['name'] = full_name
            else:
                continue
            
            # Extract affiliations
            affiliations = []
            for affiliation_elem in author_elem.xpath('.//Affiliation'):
                if affiliation_elem.text:
                    affiliations.append(affiliation_elem.text)
            
            author_data['affiliations'] = affiliations
            authors.append(author_data)
        
        return authors
    
    def _extract_corresponding_author_email(self, article) -> str:
        """Extract corresponding author email from article XML."""
        # Look for email in various places
        email_patterns = [
            './/AuthorList//Author//Affiliation',
            './/Abstract//AbstractText',
            './/ArticleTitle'
        ]
        
        import re
        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        for pattern in email_patterns:
            elements = article.xpath(pattern)
            for elem in elements:
                if elem.text:
                    emails = re.findall(email_regex, elem.text)
                    if emails:
                        return emails[0]
        
        return 'No email found'
    
    def _get_element_text(self, parent, tag_name: str) -> str:
        """Helper method to get text from child element."""
        elem = parent.xpath(f'.//{tag_name}')
        if elem and elem[0].text:
            return elem[0].text
        return ''