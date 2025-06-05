#!/usr/bin/env python3
"""
Test the fixed LLM functionality with general financial questions
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.finance_chatbot import FinanceChatbot

def test_general_questions():
    """Test general financial questions that should now work properly"""
    print("🧪 Testing Fixed LLM Functionality")
    print("=" * 50)
    
    # Initialize the chatbot
    chatbot = FinanceChatbot()
    
    # Test queries that should NOT try to find companies
    test_queries = [
        "what is inflation?",
        "what is a recession?", 
        "what is diversification?",
        "how do interest rates work?",
        "what is a bull market?",
        "explain risk management"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        
        response = chatbot.get_response(query)
        if response:
            # Show first few lines of response
            lines = response.split('\n')
            for i, line in enumerate(lines[:5]):  # Show first 5 lines
                if line.strip():
                    print(f"  {line}")
            if len(lines) > 5:
                print("  ... (response continues)")
        else:
            print("  ❌ No response received")
        
        print()

if __name__ == "__main__":
    test_general_questions()
