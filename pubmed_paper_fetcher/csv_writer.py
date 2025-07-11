"""
CSV writer for PubMed paper results.
"""

import csv
import sys
from typing import List, Dict, Any, Optional, TextIO
import logging

logger = logging.getLogger(__name__)


class CSVWriter:
    """Writer for outputting PubMed paper results to CSV format."""
    
    # Required CSV columns as per the task requirements
    REQUIRED_COLUMNS = [
        'PubmedID',
        'Title',
        'Publication Date',
        'Non-academic Author(s)',
        'Company Affiliation(s)',
        'Corresponding Author Email'
    ]
    
    def __init__(self):
        """Initialize the CSV writer."""
        pass
    
    def write_to_file(self, papers: List[Dict[str, Any]], filename: str) -> None:
        """
        Write papers to a CSV file.
        
        Args:
            papers: List of paper dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                self._write_papers(papers, csvfile)
            logger.info(f"Successfully wrote {len(papers)} papers to {filename}")
        except IOError as e:
            logger.error(f"Error writing to file {filename}: {e}")
            raise
    
    def write_to_console(self, papers: List[Dict[str, Any]]) -> None:
        """
        Write papers to console (stdout).
        
        Args:
            papers: List of paper dictionaries
        """
        self._write_papers(papers, sys.stdout)
    
    def _write_papers(self, papers: List[Dict[str, Any]], output: TextIO) -> None:
        """
        Write papers to the specified output stream.
        
        Args:
            papers: List of paper dictionaries
            output: Output stream (file or stdout)
        """
        if not papers:
            logger.warning("No papers to write")
            return
        
        writer = csv.DictWriter(
            output,
            fieldnames=self.REQUIRED_COLUMNS,
            quoting=csv.QUOTE_ALL
        )
        
        # Write header
        writer.writeheader()
        
        # Write paper data
        for paper in papers:
            row = self._convert_paper_to_row(paper)
            writer.writerow(row)
    
    def _convert_paper_to_row(self, paper: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert a paper dictionary to a CSV row.
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Dictionary with CSV column names as keys
        """
        # Convert lists to comma-separated strings
        non_academic_authors = paper.get('non_academic_authors', [])
        company_affiliations = paper.get('company_affiliations', [])
        
        non_academic_authors_str = '; '.join(non_academic_authors) if non_academic_authors else 'None'
        company_affiliations_str = '; '.join(company_affiliations) if company_affiliations else 'None'
        
        return {
            'PubmedID': paper.get('pubmed_id', ''),
            'Title': paper.get('title', ''),
            'Publication Date': paper.get('publication_date', ''),
            'Non-academic Author(s)': non_academic_authors_str,
            'Company Affiliation(s)': company_affiliations_str,
            'Corresponding Author Email': paper.get('corresponding_author_email', '')
        }
    
    def get_summary_stats(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for the papers.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Dictionary with summary statistics
        """
        if not papers:
            return {
                'total_papers': 0,
                'total_companies': 0,
                'total_non_academic_authors': 0,
                'companies': []
            }
        
        all_companies = set()
        all_authors = set()
        
        for paper in papers:
            companies = paper.get('company_affiliations', [])
            authors = paper.get('non_academic_authors', [])
            
            all_companies.update(companies)
            all_authors.update(authors)
        
        return {
            'total_papers': len(papers),
            'total_companies': len(all_companies),
            'total_non_academic_authors': len(all_authors),
            'companies': sorted(list(all_companies))
        }


def write_papers_to_csv(papers: List[Dict[str, Any]], filename: Optional[str] = None) -> None:
    """
    Write papers to CSV file or console.
    
    Args:
        papers: List of paper dictionaries
        filename: Output filename (if None, write to console)
    """
    writer = CSVWriter()
    
    if filename:
        writer.write_to_file(papers, filename)
    else:
        writer.write_to_console(papers)


def print_summary_stats(papers: List[Dict[str, Any]]) -> None:
    """
    Print summary statistics for the papers.
    
    Args:
        papers: List of paper dictionaries
    """
    writer = CSVWriter()
    stats = writer.get_summary_stats(papers)
    
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total papers found: {stats['total_papers']}")
    print(f"Total companies: {stats['total_companies']}")
    print(f"Total non-academic authors: {stats['total_non_academic_authors']}")
    
    if stats['companies']:
        print(f"\nCompanies found:")
        for company in stats['companies']:
            print(f"  - {company}")
    
    print("=" * 26)