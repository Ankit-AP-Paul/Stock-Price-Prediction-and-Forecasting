import re
from fuzzywuzzy import process, fuzz
import requests
from modules.config import Config

class CompanyMapper:
    """Maps company names to ticker symbols and vice versa"""
    
    def __init__(self):
        """Initialize the company mapper with dictionaries for lookups"""
        self._init_company_mappings()
        
    def extract_ticker_symbol(self, text):
        """
        Extract ticker symbol from text
        
        Args:
            text (str): Text to extract ticker from
            
        Returns:
            str or None: Extracted ticker symbol or None
        """
        # Use our more robust company name extraction method
        company_info = self.extract_company_name(text)
        
        if company_info:
            ticker, full_name, exchange = company_info
            print(f"Found company: {full_name} ({ticker})")
            return ticker
        
        # Legacy extraction method as fallback
        # Look for ticker patterns like $AAPL or "AAPL"
        ticker_match = re.search(r'\$([A-Za-z]{1,5})', text) or re.search(r'["\'](([A-Za-z]{1,5}))["\']', text)
        if ticker_match:
            return ticker_match.group(1).upper()
        
        # Check for standalone uppercase words that could be tickers
        words = text.upper().split()
        for word in words:
            if word.isalpha() and len(word) <= 5 and word not in ["A", "I", "THE", "AND", "FOR", "WHAT", "HOW", "CAN", "YOU", "GET", "ME", "MY"]:
                # This might be a ticker symbol
                return word
        
        return None
        
    def extract_company_name(self, text):
        """
        Extract company name from text
        This is a more robust version that looks for various patterns
        
        Args:
            text (str): Text to extract company from
            
        Returns:
            tuple or None: (ticker, company_name, exchange) or None
        """
        text_lower = text.lower()
        
        # First try the ticker symbol extraction (for existing users who know tickers)
        ticker_match = re.search(r'\$([A-Za-z]{1,5})', text) or re.search(r'["\'](([A-Za-z]{1,5}))["\']', text)
        if ticker_match:
            ticker = ticker_match.group(1).upper()
            return ticker, ticker, None  # Return ticker as both ticker and name
        
        # Define stop words that should never be considered as company names
        stop_words = [
            'the', 'this', 'that', 'these', 'those', 'there', 'here', 'today', 'tomorrow', 
            'yesterday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'it', 
            'we', 'they', 'you', 'i', 'he', 'she', 'a', 'an', 'my', 'your', 'our',
            'should', 'would', 'could', 'can', 'will', 'shall', 'may', 'might', 'must',
            'about', 'for', 'on', 'from', 'by', 'with', 'at', 'to', 'in', 'of',
            'and', 'or', 'not', 'but', 'so', 'if', 'because', 'while', 'when',
            'have', 'has', 'had', 'do', 'does', 'did', 'is', 'am', 'are', 'was', 'were',
            'been', 'being', 'get', 'got', 'getting', 'make', 'made', 'making',
            'what', 'why', 'who', 'how', 'where', 'which', 'whom', 'whose', 'price', 'current'
        ]
        
        # Special cases for common bank/company name confusion
        # Check specifically for HDFC Bank vs HDFC first - this is a special case
        if "hdfc bank" in text_lower:
            return "HDFCBANK", "HDFC Bank Ltd.", "NSE"
        elif "hdfc" in text_lower and "bank" not in text_lower:
            return "HDFC", "Housing Development Finance Corporation Ltd.", "NSE"
        
        # Special case for price queries
        price_match = re.search(r'(?:current\s+)?price\s+of\s+([a-z\s]+?)(?:$|\?|\.|,)', text_lower)
        if price_match:
            company_name = price_match.group(1).strip()
            # Replace hyphens or underscores with spaces for better matching
            company_name = company_name.replace('-', ' ').replace('_', ' ')
            # Pre-process to handle common naming variations
            if company_name == "sunpharma":
                company_name = "sun pharma"
            elif company_name == "hdfcbank":
                company_name = "hdfc bank"
            
            company_info = self.company_name_to_ticker(company_name)
            if company_info:
                return company_info
        
        # First try to extract specific company patterns - these are more reliable
        
        # "Buy/Sell X" pattern - Most direct and reliable
        buy_pattern = re.search(r'(?:buy|sell|invest in|purchase|hold|analyze)\s+([A-Za-z][A-Za-z\s&\'\-\.]+?)(?:\s+(?:stock|shares|company))?(?:$|\s+(?:now|today|this month|right now|in the future))?', text_lower)
        if buy_pattern:
            company_name = buy_pattern.group(1).strip()
            # Make sure it's not just a stop word
            if company_name not in stop_words and len(company_name) > 2:
                # Check specifically for banks to avoid confusion
                if company_name == "hdfc bank":
                    return "HDFCBANK", "HDFC Bank Ltd.", "NSE"
                elif company_name == "hdfc" and "bank" not in text_lower:
                    return "HDFC", "Housing Development Finance Corporation Ltd.", "NSE"
                
                company_info = self.company_name_to_ticker(company_name)
                if company_info:
                    return company_info
        
        # Extract all possible n-grams (1-4 words) that could be company names
        words = text_lower.split()
        candidates = []
        
        # Generate n-grams (1-4 words)
        for n in range(1, min(5, len(words) + 1)):
            for i in range(len(words) - n + 1):
                candidate = " ".join(words[i:i+n])
                # Basic filtering
                if (len(candidate) > 2 and  # At least 3 chars
                    not all(word in stop_words for word in candidate.split()) and
                    not candidate.isdigit()):
                    candidates.append(candidate)
        
        # Sort candidates by length (descending) - prefer longer company names
        candidates.sort(key=len, reverse=True)
        
        # Try to match each candidate
        for candidate in candidates:
            # Pre-process to handle common naming variations
            candidate_processed = candidate
            if candidate == "sunpharma":
                candidate_processed = "sun pharma"
            elif candidate == "hdfcbank":
                candidate_processed = "hdfc bank"
                
            company_info = self.company_name_to_ticker(candidate_processed)
            if company_info:
                ticker, full_name, exchange = company_info
                return ticker, full_name, exchange
        
        # Last resort: look for direct company mentions in the original text
        # Often queries will just have the company name directly
        for word in words:
            if word not in stop_words and len(word) >= 3 and word.isalpha():
                # Pre-process to handle common naming variations
                word_processed = word
                if word == "sunpharma":
                    word_processed = "sun pharma"
                elif word == "hdfcbank":
                    word_processed = "hdfc bank"
                    
                company_info = self.company_name_to_ticker(word_processed)
                if company_info:
                    ticker, full_name, exchange = company_info
                    return ticker, full_name, exchange
        
        return None
        
    def company_name_to_ticker(self, company_name):
        """
        Convert a company name to a ticker symbol using various methods
        
        Args:
            company_name (str): Company name to convert to ticker
            
        Returns:
            tuple: (ticker, company_name, exchange) or (None, None, None) if not found
        """
        company_name = company_name.lower().strip()
        
        # Try direct dictionary lookup first (fastest method)
        # This covers most major companies that users will ask about
        ticker_info = self._lookup_company_in_dict(company_name)
        if ticker_info:
            return ticker_info
            
        # Try fuzzy matching with company dictionary
        ticker_info = self._fuzzy_match_company(company_name)
        if ticker_info:
            return ticker_info
        
        # Try online search as a last resort
        # This will handle companies not in our dictionary
        return self._search_company_online(company_name)
        
    def _lookup_company_in_dict(self, company_name):
        """Look up company in our dictionary mappings"""
        
        # Major US Companies
        us_companies = {
            # Tech
            "apple": ("AAPL", "Apple Inc.", "NASDAQ"),
            "microsoft": ("MSFT", "Microsoft Corporation", "NASDAQ"),
            "google": ("GOOGL", "Alphabet Inc.", "NASDAQ"),
            "alphabet": ("GOOGL", "Alphabet Inc.", "NASDAQ"),
            "amazon": ("AMZN", "Amazon.com Inc.", "NASDAQ"),
            "meta": ("META", "Meta Platforms Inc.", "NASDAQ"),
            "facebook": ("META", "Meta Platforms Inc.", "NASDAQ"),
            "netflix": ("NFLX", "Netflix Inc.", "NASDAQ"),
            "tesla": ("TSLA", "Tesla Inc.", "NASDAQ"),
            "nvidia": ("NVDA", "NVIDIA Corporation", "NASDAQ"),
            "intel": ("INTC", "Intel Corporation", "NASDAQ"),
            "amd": ("AMD", "Advanced Micro Devices Inc.", "NASDAQ"),
            "ibm": ("IBM", "International Business Machines", "NYSE"),
            "oracle": ("ORCL", "Oracle Corporation", "NYSE"),
            "salesforce": ("CRM", "Salesforce Inc.", "NYSE"),
            "adobe": ("ADBE", "Adobe Inc.", "NASDAQ"),
            
            # Finance
            "jpmorgan": ("JPM", "JPMorgan Chase & Co.", "NYSE"),
            "jp morgan": ("JPM", "JPMorgan Chase & Co.", "NYSE"),
            "bank of america": ("BAC", "Bank of America Corporation", "NYSE"),
            "bofa": ("BAC", "Bank of America Corporation", "NYSE"),
            "wells fargo": ("WFC", "Wells Fargo & Company", "NYSE"),
            "morgan stanley": ("MS", "Morgan Stanley", "NYSE"),
            "goldman sachs": ("GS", "The Goldman Sachs Group, Inc.", "NYSE"),
            "visa": ("V", "Visa Inc.", "NYSE"),
            "mastercard": ("MA", "Mastercard Incorporated", "NYSE"),
            "american express": ("AXP", "American Express Company", "NYSE"),
            "amex": ("AXP", "American Express Company", "NYSE"),
            
            # Retail
            "walmart": ("WMT", "Walmart Inc.", "NYSE"),
            "costco": ("COST", "Costco Wholesale Corporation", "NASDAQ"),
            "target": ("TGT", "Target Corporation", "NYSE"),
            "home depot": ("HD", "The Home Depot, Inc.", "NYSE"),
            "lowe's": ("LOW", "Lowe's Companies, Inc.", "NYSE"),
            "lowes": ("LOW", "Lowe's Companies, Inc.", "NYSE"),
            "nike": ("NKE", "NIKE, Inc.", "NYSE"),
            "starbucks": ("SBUX", "Starbucks Corporation", "NASDAQ"),
            "mcdonald's": ("MCD", "McDonald's Corporation", "NYSE"),
            "mcdonalds": ("MCD", "McDonald's Corporation", "NYSE"),
            
            # Healthcare
            "johnson & johnson": ("JNJ", "Johnson & Johnson", "NYSE"),
            "johnson and johnson": ("JNJ", "Johnson & Johnson", "NYSE"),
            "pfizer": ("PFE", "Pfizer Inc.", "NYSE"),
            "merck": ("MRK", "Merck & Co., Inc.", "NYSE"),
            "unitedhealth": ("UNH", "UnitedHealth Group Incorporated", "NYSE"),
            "abbott": ("ABT", "Abbott Laboratories", "NYSE"),
            "abbott labs": ("ABT", "Abbott Laboratories", "NYSE"),
            "moderna": ("MRNA", "Moderna, Inc.", "NASDAQ"),
            
            # Telecom
            "verizon": ("VZ", "Verizon Communications Inc.", "NYSE"),
            "at&t": ("T", "AT&T Inc.", "NYSE"),
            "att": ("T", "AT&T Inc.", "NYSE"),
            "t-mobile": ("TMUS", "T-Mobile US, Inc.", "NASDAQ"),
            "tmobile": ("TMUS", "T-Mobile US, Inc.", "NASDAQ"),
        }
        
        # Indian Companies
        indian_companies = {
            # Tech
            "tcs": ("TCS", "Tata Consultancy Services Ltd.", "NSE"),
            "tata consultancy": ("TCS", "Tata Consultancy Services Ltd.", "NSE"),
            "infosys": ("INFY", "Infosys Ltd.", "NSE"),
            "wipro": ("WIPRO", "Wipro Ltd.", "NSE"),
            "tech mahindra": ("TECHM", "Tech Mahindra Ltd.", "NSE"),
            "hcl technologies": ("HCLTECH", "HCL Technologies Ltd.", "NSE"),
            "hcl tech": ("HCLTECH", "HCL Technologies Ltd.", "NSE"),
            
            # Conglomerates
            "reliance": ("RELIANCE", "Reliance Industries Ltd.", "NSE"),
            "reliance industries": ("RELIANCE", "Reliance Industries Ltd.", "NSE"),
            "tata motors": ("TATAMOTORS", "Tata Motors Ltd.", "NSE"),
            "tata steel": ("TATASTEEL", "Tata Steel Ltd.", "NSE"),
            "tata power": ("TATAPOWER", "Tata Power Co. Ltd.", "NSE"),
            "adani": ("ADANIENT", "Adani Enterprises Ltd.", "NSE"),
            "adani enterprises": ("ADANIENT", "Adani Enterprises Ltd.", "NSE"),
            "adani ports": ("ADANIPORTS", "Adani Ports and Special Economic Zone Ltd.", "NSE"),
            "larsen & toubro": ("LT", "Larsen & Toubro Ltd.", "NSE"),
            "l&t": ("LT", "Larsen & Toubro Ltd.", "NSE"),
            
            # Banking & Finance
            "hdfc": ("HDFC", "Housing Development Finance Corporation Ltd.", "NSE"),
            "hdfc bank": ("HDFCBANK", "HDFC Bank Ltd.", "NSE"),
            "icici": ("ICICIBANK", "ICICI Bank Ltd.", "NSE"),
            "icici bank": ("ICICIBANK", "ICICI Bank Ltd.", "NSE"),
            "sbi": ("SBIN", "State Bank of India", "NSE"),
            "state bank of india": ("SBIN", "State Bank of India", "NSE"),
            "kotak": ("KOTAKBANK", "Kotak Mahindra Bank Ltd.", "NSE"),
            "kotak mahindra": ("KOTAKBANK", "Kotak Mahindra Bank Ltd.", "NSE"),
            "axis bank": ("AXISBANK", "Axis Bank Ltd.", "NSE"),
            
            # Consumer Goods
            "hindustan unilever": ("HINDUNILVR", "Hindustan Unilever Ltd.", "NSE"),
            "itc": ("ITC", "ITC Ltd.", "NSE"),
            "britannia": ("BRITANNIA", "Britannia Industries Ltd.", "NSE"),
            "nestle india": ("NESTLEIND", "Nestle India Ltd.", "NSE"),
            "dabur": ("DABUR", "Dabur India Ltd.", "NSE"),
            
            # Pharma
            "sun pharma": ("SUNPHARMA", "Sun Pharmaceutical Industries Ltd.", "NSE"),
            "dr reddy's": ("DRREDDY", "Dr. Reddy's Laboratories Ltd.", "NSE"),
            "cipla": ("CIPLA", "Cipla Ltd.", "NSE"),
            "divis laboratories": ("DIVISLAB", "Divi's Laboratories Ltd.", "NSE"),
            "divis labs": ("DIVISLAB", "Divi's Laboratories Ltd.", "NSE"),
            
            # Automotive
            "maruti suzuki": ("MARUTI", "Maruti Suzuki India Ltd.", "NSE"),
            "mahindra": ("M&M", "Mahindra & Mahindra Ltd.", "NSE"),
            "mahindra and mahindra": ("M&M", "Mahindra & Mahindra Ltd.", "NSE"),
            "hero motocorp": ("HEROMOTOCO", "Hero MotoCorp Ltd.", "NSE"),
            "bajaj auto": ("BAJAJ-AUTO", "Bajaj Auto Ltd.", "NSE"),
        }
        
        # UK Companies
        uk_companies = {
            "hsbc": ("HSBA.L", "HSBC Holdings plc", "LSE"),
            "barclays": ("BARC.L", "Barclays PLC", "LSE"),
            "bp": ("BP.L", "BP p.l.c.", "LSE"),
            "vodafone": ("VOD.L", "Vodafone Group Plc", "LSE"),
            "unilever": ("ULVR.L", "Unilever PLC", "LSE"),
            "astrazeneca": ("AZN.L", "AstraZeneca PLC", "LSE"),
            "gsk": ("GSK.L", "GSK plc", "LSE"),
            "glaxosmithkline": ("GSK.L", "GSK plc", "LSE"),
            "lloyds": ("LLOY.L", "Lloyds Banking Group plc", "LSE"),
            "british airways": ("IAG.L", "International Consolidated Airlines Group, S.A.", "LSE"),
            "rolls-royce": ("RR.L", "Rolls-Royce Holdings plc", "LSE"),
            "rolls royce": ("RR.L", "Rolls-Royce Holdings plc", "LSE"),
            "tesco": ("TSCO.L", "Tesco PLC", "LSE"),
            "sainsbury": ("SBRY.L", "J Sainsbury plc", "LSE"),
            "sainsburys": ("SBRY.L", "J Sainsbury plc", "LSE"),
        }
        
        # Combine all company dictionaries
        combined_companies = {**us_companies, **indian_companies, **uk_companies}
        
        # Try direct lookup
        if company_name in combined_companies:
            ticker, full_name, exchange = combined_companies[company_name]
            return ticker, full_name, exchange
        
        # Try to match parts of company names (e.g., "apple company" should match "apple")
        for key, value in combined_companies.items():
            if key in company_name or company_name in key:
                return value
        
        return None

    def _fuzzy_match_company(self, company_name, threshold=80):
        """Use fuzzy matching to find the closest company name"""
        
        # Get all company names from our dictionary
        all_companies = {}
        
        # Combine from all our company dictionaries
        for dict_func in [self._lookup_company_in_dict]:
            result = dict_func("")  # Empty query to just access the dictionary
            if result and hasattr(result, "items"):
                all_companies.update(result)
        
        if not all_companies:
            # Fallback to just the basic Indian stocks we had before
            all_companies = {
                "tcs": ("TCS", "Tata Consultancy Services", "NSE"),
                "infosys": ("INFY", "Infosys Ltd.", "NSE"),
                "wipro": ("WIPRO", "Wipro Ltd.", "NSE"),
                "reliance": ("RELIANCE", "Reliance Industries", "NSE"),
                "tata motors": ("TATAMOTORS", "Tata Motors Ltd.", "NSE")
            }
        
        # Get all company names
        company_names = list(all_companies.keys())
        
        # Find the closest match
        best_match, score = process.extractOne(
            company_name, 
            company_names,
            scorer=fuzz.token_sort_ratio
        )
        
        # Return the match if it's good enough
        if score >= threshold:
            return all_companies[best_match]
        
        return None

    def _search_company_online(self, company_name):
        """
        Search for a company ticker online as a last resort
        Use Yahoo Finance search API to find company information
        
        Args:
            company_name (str): Company name to search for
            
        Returns:
            tuple: (ticker, company_name, exchange) or (None, None, None) if not found
        """
        try:
            print(f"Searching online for company: {company_name}")
            # Yahoo Finance API endpoint
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={company_name}&quotesCount=1&newsCount=0"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got any quotes
                if 'quotes' in data and len(data['quotes']) > 0:
                    # Get the first (most relevant) quote
                    quote = data['quotes'][0]
                    
                    # Extract ticker, company name and exchange
                    ticker = quote.get('symbol')
                    full_name = quote.get('longname') or quote.get('shortname')
                    exchange = quote.get('exchange')
                    
                    if ticker:
                        print(f"Found company via online search: {ticker} - {full_name}")
                        return ticker, full_name, exchange
            
            print(f"No company found online for: {company_name}")
            return None
        except Exception as e:
            print(f"Error searching for company online: {e}")
            return None

    def _init_company_mappings(self):
        """Initialize company to ticker and ticker to company mappings"""
        # Initialize company mappings
        self.company_to_ticker = {}
        self.ticker_to_company = {}
        
        # Major US Companies
        us_companies = {
            # Tech
            "apple": ("AAPL", "Apple Inc.", "NASDAQ"),
            "microsoft": ("MSFT", "Microsoft Corporation", "NASDAQ"),
            "google": ("GOOGL", "Alphabet Inc.", "NASDAQ"),
            "alphabet": ("GOOGL", "Alphabet Inc.", "NASDAQ"),
            "amazon": ("AMZN", "Amazon.com Inc.", "NASDAQ"),
            "meta": ("META", "Meta Platforms Inc.", "NASDAQ"),
            "facebook": ("META", "Meta Platforms Inc.", "NASDAQ"),
            "netflix": ("NFLX", "Netflix Inc.", "NASDAQ"),
            "tesla": ("TSLA", "Tesla Inc.", "NASDAQ"),
            "nvidia": ("NVDA", "NVIDIA Corporation", "NASDAQ"),
            # ... other companies
        }
        
        # Indian Companies
        indian_companies = {
            "tcs": ("TCS", "Tata Consultancy Services Ltd.", "NSE"),
            "tata consultancy": ("TCS", "Tata Consultancy Services Ltd.", "NSE"),
            "infosys": ("INFY", "Infosys Ltd.", "NSE"),
            "wipro": ("WIPRO", "Wipro Ltd.", "NSE"),
            "reliance": ("RELIANCE", "Reliance Industries Ltd.", "NSE"),
            "reliance industries": ("RELIANCE", "Reliance Industries Ltd.", "NSE"),
            "tata motors": ("TATAMOTORS", "Tata Motors Ltd.", "NSE"),
            # ... other companies
        }
        
        # Combine all companies into the mappings
        all_companies = {**us_companies, **indian_companies}
        
        # Create both mappings
        for company_name, (ticker, full_name, exchange) in all_companies.items():
            self.company_to_ticker[company_name] = ticker
            self.ticker_to_company[ticker] = (full_name, exchange)