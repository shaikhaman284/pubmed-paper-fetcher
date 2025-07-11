# PubMed Paper Fetcher

A tool to fetch PubMed papers from pharmaceutical/biotech companies.

## Description

This project provides a command-line interface to search and fetch research papers from PubMed, specifically focusing on publications from pharmaceutical and biotechnology companies.

## Installation

1. Clone this repository
2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

## Usage

```bash
poetry run python -m pubmed_paper_fetcher --help
```

## Dependencies

- **requests**: For making HTTP requests to PubMed API
- **lxml**: For XML parsing of PubMed responses
- **click**: For creating the command-line interface

## Requirements

- Python ^3.12
- Poetry for dependency management

## License

MIT License

## Author

Shaikh Aman (shaikhamanksf@gmail.com)