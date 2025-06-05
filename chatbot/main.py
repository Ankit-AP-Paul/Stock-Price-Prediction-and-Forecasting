#!/usr/bin/env python3
import os
import argparse
from modules.finance_chatbot import FinanceChatbot

def main():
    """Main entry point for the Finance LLM Chatbot application"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Finance LLM Chatbot")
    parser.add_argument("--model", dest="model_name", default="google/flan-t5-small",
                      help="Hugging Face model to use (default: google/flan-t5-small)")
    parser.add_argument("--api-key", "--api_key", dest="api_key", default=None,
                      help="Hugging Face API key (default: uses HF_API_KEY environment variable)")
    
    args = parser.parse_args()
    
    # Get API key from environment variable if not provided
    api_key = args.api_key or os.environ.get("HF_API_KEY")
    
    # Print welcome message
    print("\n" + "=" * 60)
    print("Welcome to the Finance LLM Chatbot!")
    print("=" * 60)
    print("This chatbot can help you with stock analysis")
    print("and general finance questions using the power of LLMs.")
    print("\nType 'exit' or 'quit' to end the chat session.")
    print("=" * 60 + "\n")
    
    # Initialize the chatbot
    chatbot = FinanceChatbot(
        api_key=api_key,
        model_name=args.model_name
    )
    
    # Main chat loop
    while True:
        # Get user input
        user_input = input("\n> ")
        
        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\nThank you for using the Finance LLM Chatbot. Goodbye!")
            break
        
        # Get response from chatbot
        try:
            response = chatbot.get_response(user_input)
            print("\n" + response)
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Sorry, I encountered an error processing your request. Please try again.")

if __name__ == "__main__":
    main()