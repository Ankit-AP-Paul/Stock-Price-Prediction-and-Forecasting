#!/usr/bin/env python3
"""
Debug script to test the regex pattern for period parsing
"""
import re

def test_regex_patterns():
    """Test the regex patterns for different time periods"""
    print("Testing Regex Patterns for Period Parsing")
    print("=" * 50)
    
    test_queries = [
        "how has ICICI bank performed over last 8 months?",
        "how has RELIANCE performed over last 6 months?", 
        "how has TCS performed over last 1 year?",
        "how has INFY performed over last 2 years?",
        "performance of apple over 3 months",
        "show me 5 days data",
        "last 12 months performance"
    ]
    
    pattern = r'(\d+)\s*(day|days|week|weeks|month|months|year|years)'
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        user_input_lower = query.lower()
        duration_match = re.search(pattern, user_input_lower)
        
        if duration_match:
            duration = int(duration_match.group(1))
            unit = duration_match.group(2)
            print(f"  ✓ Found: {duration} {unit}")
            
            # Apply the logic
            if unit in ['month', 'months']:
                yfinance_period = f"{duration}mo"
                display_period = f"{duration} {'month' if duration == 1 else 'months'}"
            elif unit in ['year', 'years']:
                yfinance_period = f"{duration}y"
                display_period = f"{duration} {'year' if duration == 1 else 'years'}"
            elif unit in ['day', 'days']:
                yfinance_period = f"{duration}d"
                display_period = f"{duration} {'day' if duration == 1 else 'days'}"
            else:
                yfinance_period = "1y"
                display_period = "1 year"
                
            print(f"  → yfinance_period: {yfinance_period}")
            print(f"  → display_period: {display_period}")
        else:
            print("  ✗ No match found")

if __name__ == "__main__":
    test_regex_patterns()
