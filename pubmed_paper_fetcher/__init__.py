"""
PubMed Paper Fetcher - A tool to fetch research papers from pharmaceutical/biotech companies.
"""

from .api_client import PubMedAPIClient
from .parser import parse_papers, PharmaFilter
from .csv_writer import write_papers_to_csv, print_summary_stats
from .main import main

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    'PubMedAPIClient',
    'parse_papers',
    'PharmaFilter',
    'write_papers_to_csv',
    'print_summary_stats',
    'main'
]