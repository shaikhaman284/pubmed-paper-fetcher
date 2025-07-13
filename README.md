# PubMed Paper Fetcher

A Python tool to fetch research papers from PubMed that have at least one author affiliated with pharmaceutical or biotech companies.

## Features

- Fetch papers from PubMed using flexible query syntax
- Identify papers with pharmaceutical/biotech company authors
- Filter out academic-only papers
- Export results to CSV format
- Command-line interface with multiple options
- Comprehensive logging and error handling

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. **Clone the repository:**
   ```bash
   git clone (https://github.com/shaikhaman284/pubmed-paper-fetcher.git)
   cd pubmed-paper-fetcher
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

## Usage

### Command Line Interface

The tool provides a command-line interface accessible via the `get-papers-list` command:

```bash
get-papers-list "your search query" [options]
```

### Options

- `-h, --help`: Show help message
- `-f, --file FILENAME`: Save results to CSV file (default: output to console)
- `-d, --debug`: Enable debug logging
- `--max-results N`: Maximum number of results to fetch (default: 100)
- `--email EMAIL`: Your email address (recommended by NCBI)
- `--no-stats`: Skip printing summary statistics

### Examples

1. **Basic search with console output:**
   ```bash
   get-papers-list "cancer AND drug development"
   ```

2. **Search with file output:**
   ```bash
   get-papers-list "COVID-19 vaccine" -f results.csv
   ```

3. **Debug mode with file output:**
   ```bash
   get-papers-list "immunotherapy" -d -f output.csv
   ```

4. **Advanced PubMed query:**
   ```bash
   get-papers-list "CRISPR[Title] AND gene therapy" --max-results 50 --file crispr_papers.csv
   ```

### PubMed Query Syntax

The tool supports full PubMed query syntax:

- **Boolean operators**: AND, OR, NOT
- **Field tags**: [Title], [Author], [Journal], [Abstract]
- **Exact phrases**: Use quotes "exact phrase"
- **Wildcards**: Use * for partial matches
- **Date ranges**: 2023[PDAT] for publication date

**Example queries:**
- `"machine learning"[Title] AND "drug discovery"`
- `(cancer OR tumor) AND immunotherapy`
- `Smith J[Author] AND "Nature"[Journal]`
- `COVID-19 AND vaccine AND 2023[PDAT]`

## Code Organization

The project is organized into the following modules:

```
pubmed_paper_fetcher/
├── __init__.py           # Package initialization
├── api_client.py         # PubMed API client
├── parser.py             # Paper filtering and parsing
├── csv_writer.py         # CSV output handling
└── main.py              # Command-line interface
```

### Module Descriptions

- **`api_client.py`**: Handles all interactions with the PubMed API, including searching for papers and fetching detailed information.
- **`parser.py`**: Contains logic to identify pharmaceutical/biotech company affiliations and filter papers accordingly.
- **`csv_writer.py`**: Manages CSV output formatting and file writing.
- **`main.py`**: Provides the command-line interface and orchestrates the entire workflow.

## Output Format

The tool generates CSV files with the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Title of the paper
- **Publication Date**: Date the paper was published
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies
- **Corresponding Author Email**: Email address of the corresponding author

## Company Identification

The tool identifies pharmaceutical and biotech companies using:

1. **Known company database**: Extensive list of major pharmaceutical and biotech companies
2. **Keyword matching**: Identifies affiliations containing terms like "pharmaceutical", "biotech", "therapeutics"
3. **Academic filtering**: Excludes clearly academic institutions (universities, hospitals, research centers)

## Dependencies

The project uses the following key dependencies:

- **requests**: HTTP library for API calls
- **lxml**: XML parsing library for PubMed responses
- **click**: Command-line interface framework
- **typing**: Type hints support

## Development

### Adding New Companies

To add new pharmaceutical or biotech companies to the filter:

1. Edit `pubmed_paper_fetcher/parser.py`
2. Add company names to the `_load_pharma_companies()` or `_load_biotech_companies()` methods
3. Use lowercase names for consistency

### Testing

Run tests using:
```bash
poetry run pytest
```

### Code Quality

The project uses:
- **Type hints** throughout the codebase
- **Comprehensive logging** for debugging
- **Error handling** for robust operation
- **Modular design** for maintainability

## API Usage Guidelines

- The tool respects PubMed's rate limits (3 requests per second)
- Providing an email address is recommended for API usage tracking
- Large queries may take time due to rate limiting

## Troubleshooting

### Common Issues

1. **No papers found**: Check your query syntax and try broader search terms
2. **API errors**: Ensure internet connectivity and try again later
3. **Empty results**: The query may not match papers with pharma/biotech authors

### Debug Mode

Use the `--debug` flag to see detailed logging:
```bash
get-papers-list "your query" --debug
```

## Tools and Resources Used

This project was built with assistance from:

- **Claude AI** (Anthropic) - For code generation and problem-solving assistance
- **PubMed E-utilities API** - [Documentation](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- **Poetry** - [Documentation](https://python-poetry.org/docs/)
- **Python Type Hints** - [Documentation](https://docs.python.org/3/library/typing.html)

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues or questions, please open an issue on the GitHub repository.
