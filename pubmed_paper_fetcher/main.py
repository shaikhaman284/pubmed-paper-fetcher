"""
Main command-line interface for the PubMed paper fetcher.
"""

import argparse
import logging
import sys
from typing import Optional

from .api_client import PubMedAPIClient
from .parser import parse_papers
from .csv_writer import write_papers_to_csv, print_summary_stats


def setup_logging(debug: bool = False) -> None:
    """
    Set up logging configuration.
    
    Args:
        debug: Enable debug logging
    """
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description='Fetch PubMed papers with pharmaceutical/biotech company authors',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  get-papers-list "cancer AND drug development"
  get-papers-list "COVID-19 vaccine" -f results.csv
  get-papers-list "immunotherapy" -d -f output.csv
  get-papers-list "CRISPR[Title]" --debug --file crispr_papers.csv

Query Syntax:
  Supports full PubMed query syntax:
  - Use AND, OR, NOT operators
  - Use [Field] tags like [Title], [Author], [Journal]
  - Use quotes for exact phrases
  - Use wildcards with *
  
Examples of PubMed queries:
  - "machine learning"[Title] AND "drug discovery"
  - (cancer OR tumor) AND immunotherapy
  - Smith J[Author] AND "Nature"[Journal]
  - COVID-19 AND vaccine AND 2023[PDAT]
        """
    )
    
    parser.add_argument(
        'query',
        help='PubMed search query (supports full PubMed syntax)'
    )
    
    parser.add_argument(
        '-f', '--file',
        help='Output filename for CSV results (if not specified, output to console)'
    )
    
    parser.add_argument(
        '-d', '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of results to fetch (default: 100)'
    )
    
    parser.add_argument(
        '--email',
        help='Your email address (recommended by NCBI for API usage tracking)'
    )
    
    parser.add_argument(
        '--no-stats',
        action='store_true',
        help='Skip printing summary statistics'
    )
    
    return parser


def main() -> None:
    """Main entry point for the CLI application."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize API client
        logger.info("Initializing PubMed API client...")
        client = PubMedAPIClient(email=args.email)
        
        # Search for papers
        logger.info(f"Searching for papers with query: {args.query}")
        pubmed_ids = client.search_papers(args.query, args.max_results)
        
        if not pubmed_ids:
            print("No papers found for the given query.")
            return
        
        logger.info(f"Found {len(pubmed_ids)} papers")
        
        # Fetch paper details
        logger.info("Fetching paper details...")
        papers = client.fetch_paper_details(pubmed_ids)
        
        if not papers:
            print("No paper details could be fetched.")
            return
        
        logger.info(f"Fetched details for {len(papers)} papers")
        
        # Filter papers with pharma/biotech authors
        logger.info("Filtering papers with pharmaceutical/biotech authors...")
        filtered_papers = parse_papers(papers)
        
        if not filtered_papers:
            print("No papers found with pharmaceutical/biotech company authors.")
            return
        
        logger.info(f"Found {len(filtered_papers)} papers with pharma/biotech authors")
        
        # Output results
        if args.file:
            logger.info(f"Writing results to {args.file}")
            write_papers_to_csv(filtered_papers, args.file)
            print(f"Results written to {args.file}")
        else:
            logger.info("Writing results to console")
            write_papers_to_csv(filtered_papers)
        
        # Print summary statistics
        if not args.no_stats:
            print_summary_stats(filtered_papers)
        
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        if args.debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()