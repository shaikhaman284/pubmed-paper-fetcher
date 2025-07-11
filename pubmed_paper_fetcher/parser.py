"""
Parser and filter for PubMed papers to identify pharmaceutical/biotech company affiliations.
"""

import re
from typing import List, Dict, Any, Set
import logging

logger = logging.getLogger(__name__)


class PharmaFilter:
    """Filter for identifying pharmaceutical and biotech company affiliations."""
    
    def __init__(self):
        """Initialize the filter with known pharmaceutical and biotech companies."""
        self.pharma_companies = self._load_pharma_companies()
        self.biotech_companies = self._load_biotech_companies()
        self.academic_keywords = self._load_academic_keywords()
        
    def _load_pharma_companies(self) -> Set[str]:
        """Load list of known pharmaceutical companies."""
        companies = {
            # Big Pharma
            'pfizer', 'johnson & johnson', 'roche', 'novartis', 'merck', 'abbvie',
            'bristol-myers squibb', 'bms', 'astrazeneca', 'glaxosmithkline', 'gsk',
            'sanofi', 'takeda', 'boehringer ingelheim', 'eli lilly', 'lilly',
            'amgen', 'gilead', 'biogen', 'celgene', 'regeneron', 'vertex',
            'alexion', 'incyte', 'shire', 'allergan', 'teva', 'mylan',
            'viatris', 'sandoz', 'hospira', 'actavis', 'watson',
            
            # Additional companies
            'bayer', 'servier', 'actelion', 'endo', 'mallinckrodt', 'purdue pharma',
            'otsuka', 'daiichi sankyo', 'eisai', 'astellas', 'chugai', 'sumitomo',
            'kyowa kirin', 'mitsubishi tanabe', 'shionogi', 'ono pharmaceutical',
            'ajinomoto', 'fujifilm', 'recordati', 'almirall', 'ipsen', 'pierre fabre',
            'ucb', 'lundbeck', 'novo nordisk', 'leo pharma', 'ferring',
            'nycomed', 'gedeon richter', 'krka', 'sandoz', 'hexal', 'stada',
            'ratiopharm', 'zentiva', 'egis', 'pliva', 'dr. reddy', 'sun pharma',
            'lupin', 'cipla', 'aurobindo', 'zydus', 'torrent', 'cadila',
            'biocon', 'wockhardt', 'glenmark', 'alkem', 'mankind', 'intas',
            'hetero', 'natco', 'divis', 'laurus', 'granules', 'suven',
            'dishman', 'piramal', 'jubilant', 'syngene', 'neuland',
            
            # Chinese companies
            'sinopharm', 'jiangsu hengrui', 'beigene', 'wuxi biologics', 'wuxi apptec',
            'hansoh', 'innovent', 'junshi', 'henlius', 'zaai', 'genscript',
            'mindray', 'shenzhen kangtai', 'sinovac', 'fosun pharma',
            
            # Other international
            'takeda', 'astellas', 'daiichi sankyo', 'eisai', 'chugai', 'ono',
            'kyowa kirin', 'mitsubishi tanabe', 'shionogi', 'sumitomo dainippon',
            'otsuka', 'teijin', 'ajinomoto', 'fujifilm', 'asahi kasei'
        }
        
        return companies
    
    def _load_biotech_companies(self) -> Set[str]:
        """Load list of known biotech companies."""
        companies = {
            # Major biotech
            'genentech', 'amgen', 'gilead', 'biogen', 'regeneron', 'vertex',
            'alexion', 'incyte', 'moderna', 'biontech', 'illumina', 'seagen',
            'seattle genetics', 'bluebird bio', 'crispr therapeutics', 'editas',
            'intellia', 'sangamo', 'spark therapeutics', 'biomarin', 'sarepta',
            'ionis', 'alnylam', 'arrowhead', 'dicerna', 'silence therapeutics',
            'arcturus', 'translate bio', 'acuitas', 'genevant', 'precision nanosystems',
            
            # CAR-T and cell therapy
            'kite pharma', 'juno therapeutics', 'bluebird bio', 'fate therapeutics',
            'bristol-myers squibb', 'novartis', 'gilead', 'legend biotech',
            'janssen', 'autolus', 'precision biosciences', 'caribou biosciences',
            'allogene therapeutics', 'celyad', 'cellectis', 'adaptimmune',
            'tcr2 therapeutics', 'iovance', 'cullinan oncology', 'sorrento',
            
            # Gene therapy
            'bluebird bio', 'spark therapeutics', 'uniqure', 'voyager therapeutics',
            'regenxbio', 'adverum', 'nightstar', 'meiragtx', 'homology medicines',
            'logicbio', 'audentes', 'solid biosciences', 'sarepta', 'pfizer',
            'roche', 'novartis', 'biogen', 'takeda', 'ultragenyx', 'biomarin',
            'alexion', 'shire', 'genzyme', 'lysogene', 'orchard therapeutics',
            'avrobio', 'magenta therapeutics', 'rocket pharmaceuticals',
            'amicus', 'protalix', 'pharming', 'synageva', 'vtesse', 'leadiant',
            
            # Immunotherapy
            'bristol-myers squibb', 'merck', 'roche', 'astrazeneca', 'pfizer',
            'novartis', 'sanofi', 'regeneron', 'seattle genetics', 'immunomedics',
            'gilead', 'abbvie', 'takeda', 'celgene', 'juno', 'kite', 'car-t',
            'adaptimmune', 'immunocore', 'kymab', 'repertoire immune medicines',
            'hookin', 'puretech', 'compass therapeutics', 'pieris', 'molecular templates',
            'sutro', 'cue biopharma', 'generon', 'targovax', 'bavarian nordic',
            'transgene', 'psioxus', 'oncolytics', 'sillajen', 'replimune',
            'istari oncology', 'oncosec', 'inovio', 'advaxis', 'heat biologics',
            'immune design', 'agenus', 'genocea', 'selecta', 'ziopharm',
            'intrexon', 'precigen', 'synthetic biologics', 'synlogic', 'second genome',
            'seres', 'vedanta', 'rebiotix', 'finch therapeutics', 'enterome',
            'eligo bioscience', 'locus biosciences', 'osel', 'symbiotix',
            'microbiome therapeutics', 'microbiotica', 'pendulum therapeutics',
            'seed health', 'sun genomics', 'viome', 'thryve', 'psomagen',
            'ubiome', 'american gut', 'british gut', 'australian gut', 'global gut',
            
            # Smaller biotech
            'moderna', 'biontech', 'curevac', 'arcturus', 'translate bio',
            'acuitas', 'genevant', 'precision nanosystems', 'ethris', 'strand',
            'gritstone', 'neon therapeutics', 'personalis', 'adaptive biotechnologies',
            'immune design', 'agenus', 'genocea', 'selecta', 'ziopharm',
            'intrexon', 'precigen', 'synthetic biologics', 'synlogic', 'second genome',
            'seres', 'vedanta', 'rebiotix', 'finch therapeutics', 'enterome',
            'eligo bioscience', 'locus biosciences', 'osel', 'symbiotix',
            'microbiome therapeutics', 'microbiotica', 'pendulum therapeutics',
            'seed health', 'sun genomics', 'viome', 'thryve', 'psomagen',
            'ubiome', 'american gut', 'british gut', 'australian gut', 'global gut'
        }
        
        return companies
    
    def _load_academic_keywords(self) -> Set[str]:
        """Load keywords that indicate academic institutions."""
        keywords = {
            'university', 'college', 'school', 'institute', 'hospital', 'medical center',
            'research center', 'laboratory', 'lab', 'department', 'faculty',
            'academia', 'academic', 'educational', 'clinic', 'health system',
            'medical school', 'dental school', 'veterinary school', 'pharmacy school',
            'nursing school', 'public health', 'research institute', 'cancer center',
            'children\'s hospital', 'veterans affairs', 'va medical', 'national institutes',
            'nih', 'cdc', 'fda', 'government', 'federal', 'state university',
            'community college', 'technical college', 'seminary', 'conservatory'
        }
        
        return keywords
    
    def is_pharma_biotech_affiliation(self, affiliation: str) -> bool:
        """
        Check if an affiliation is with a pharmaceutical or biotech company.
        
        Args:
            affiliation: Author affiliation string
            
        Returns:
            True if affiliation is with pharma/biotech company
        """
        if not affiliation:
            return False
        
        affiliation_lower = affiliation.lower()
        
        # First check if it's clearly academic
        if self._is_academic_affiliation(affiliation_lower):
            return False
        
        # Check for pharma/biotech company names
        all_companies = self.pharma_companies.union(self.biotech_companies)
        
        for company in all_companies:
            if company.lower() in affiliation_lower:
                return True
        
        # Check for common pharma/biotech keywords
        pharma_keywords = {
            'pharmaceutical', 'pharmaceuticals', 'pharma', 'biotech', 'biotechnology',
            'biopharmaceutical', 'biopharma', 'therapeutics', 'medicines',
            'drug development', 'clinical development', 'r&d', 'research and development',
            'life sciences', 'biosciences', 'medical affairs', 'clinical research',
            'preclinical', 'translational medicine', 'drug discovery'
        }
        
        for keyword in pharma_keywords:
            if keyword in affiliation_lower:
                return True
        
        return False
    
    def _is_academic_affiliation(self, affiliation: str) -> bool:
        """Check if affiliation is clearly academic."""
        for keyword in self.academic_keywords:
            if keyword in affiliation:
                return True
        return False
    
    def extract_company_name(self, affiliation: str) -> str:
        """
        Extract the company name from an affiliation string.
        
        Args:
            affiliation: Author affiliation string
            
        Returns:
            Company name if found, otherwise the affiliation string
        """
        if not affiliation:
            return 'Unknown'
        
        affiliation_lower = affiliation.lower()
        
        # Check for exact company matches
        all_companies = self.pharma_companies.union(self.biotech_companies)
        
        for company in all_companies:
            if company.lower() in affiliation_lower:
                return company.title()
        
        # If no exact match, try to extract the organization name
        # This is a simple heuristic - look for the first part before comma or period
        parts = affiliation.split(',')
        if parts:
            potential_company = parts[0].strip()
            if len(potential_company) > 3:  # Avoid very short matches
                return potential_company
        
        return affiliation
    
    def filter_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter papers to only include those with pharmaceutical/biotech authors.
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Filtered list of papers with pharma/biotech authors
        """
        filtered_papers = []
        
        for paper in papers:
            authors = paper.get('authors', [])
            non_academic_authors = []
            company_affiliations = []
            
            for author in authors:
                affiliations = author.get('affiliations', [])
                
                for affiliation in affiliations:
                    if self.is_pharma_biotech_affiliation(affiliation):
                        non_academic_authors.append(author['name'])
                        company_name = self.extract_company_name(affiliation)
                        if company_name not in company_affiliations:
                            company_affiliations.append(company_name)
            
            # Only include papers with at least one pharma/biotech author
            if non_academic_authors:
                paper['non_academic_authors'] = list(set(non_academic_authors))
                paper['company_affiliations'] = list(set(company_affiliations))
                filtered_papers.append(paper)
        
        logger.info(f"Filtered {len(filtered_papers)} papers with pharma/biotech authors from {len(papers)} total papers")
        return filtered_papers


def parse_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse and filter papers to identify those with pharmaceutical/biotech authors.
    
    Args:
        papers: List of paper dictionaries from PubMed API
        
    Returns:
        List of filtered papers with pharma/biotech authors
    """
    filter_engine = PharmaFilter()
    return filter_engine.filter_papers(papers)