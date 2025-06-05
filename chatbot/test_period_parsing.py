#!/usr/bin/env python3
"""
Test script to verify the period parsing fix for the finance chatbot
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finance_chatbot import FinanceChatbot

def test_period_parsing():
    """Test the period parsing for different time periods"""
    print("Testing Period Parsing Fix")
    print("=" * 40)
    
    # Initialize the chatbot
    chatbot = FinanceChatbot()
    
    # Test queries with different periods
    test_queries = [
        "how has ICICI bank performed over last 8 months?",
        "how has RELIANCE performed over last 6 months?", 
        "how has TCS performed over last 1 year?",
        "how has INFY performed over last 2 years?"
    ]
    
    for query in test_queries:
        print(f"\nTesting: {query}")
        print("-" * 30)
        
        response = chatbot.get_response(query)
        if response:
            # Look for the period mentioned in the response
            print("Response snippet:")
            lines = response.split('\n')
            for line in lines[:10]:  # Show first 10 lines
                if 'period' in line.lower() or 'over' in line.lower() or 'months' in line.lower() or 'years' in line.lower():
                    print(f"  {line}")
        else:
            print("  No response received")

if __name__ == "__main__":
    test_period_parsing()
