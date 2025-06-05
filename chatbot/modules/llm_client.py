"""
LLM Client for Finance Chatbot
Handles communication with Hugging Face API for LLM responses
"""
import requests
import json
from typing import Optional, Dict, Any


class LLMClient:
    """Client for interacting with Hugging Face LLM API"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialize LLM client
        
        Args:
            api_key: Hugging Face API key
            model_name: Name of the model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        self.headers = {
            "Authorization": f"Bearer {api_key}" if api_key else None,
            "Content-Type": "application/json"
        }
    
    def generate_response(self, prompt: str, max_length: int = 150) -> str:
        """
        Generate response using LLM
        
        Args:
            prompt: Input prompt for the model
            max_length: Maximum length of generated response
            
        Returns:
            Generated response text
        """
        if not self.api_key:
            return self.get_fallback_response(prompt)
        
        try:
            # Format prompt for the model
            formatted_prompt = self._format_prompt(prompt)
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_length": max_length,
                    "temperature": 0.7,
                    "do_sample": True,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 404:
                print(f"Warning: Model {self.model_name} not found. Using fallback response.")
                return self.get_fallback_response(prompt)
            elif response.status_code != 200:
                print(f"API Error {response.status_code}: {response.text}")
                return self.get_fallback_response(prompt)
            
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
                # Clean up the response
                return self._clean_response(generated_text, formatted_prompt)
            else:
                return self.get_fallback_response(prompt)
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return self.get_fallback_response(prompt)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return self.get_fallback_response(prompt)
    
    def _format_prompt(self, prompt: str) -> str:
        """Format prompt for the model"""
        return f"Question: {prompt}\nAnswer:"
    
    def _clean_response(self, generated_text: str, original_prompt: str) -> str:
        """Clean and format the generated response"""
        # Remove the original prompt from the response
        if original_prompt in generated_text:
            response = generated_text.replace(original_prompt, "").strip()
        else:
            response = generated_text.strip()
        
        # Remove common artifacts
        response = response.replace("Question:", "").replace("Answer:", "").strip()
        
        # If response is empty or too short, provide fallback
        if len(response) < 10:
            return self.get_fallback_response(original_prompt.replace("Question:", "").replace("Answer:", "").strip())
        
        return response
    
    def get_fallback_response(self, prompt: str) -> str:
        """
        Provide fallback responses for common financial questions
        
        Args:
            prompt: User's question
            
        Returns:
            Fallback response
        """
        prompt_lower = prompt.lower()
        
        # Common financial topics with detailed responses
        if any(word in prompt_lower for word in ['inflation', 'inflat']):
            return """Inflation is the rate at which the general level of prices for goods and services rises, 
eroding purchasing power. It's measured by indices like CPI (Consumer Price Index). 
Moderate inflation (2-3% annually) is generally healthy for economic growth, while high inflation 
can reduce consumer spending power and investment returns."""
        
        elif any(word in prompt_lower for word in ['recession', 'economic downturn']):
            return """A recession is a significant decline in economic activity lasting more than a few months, 
typically visible in GDP, employment, and industrial production. It's often defined as two consecutive 
quarters of negative GDP growth. Recessions can be caused by various factors including high inflation, 
reduced consumer confidence, or external shocks."""
        
        elif any(word in prompt_lower for word in ['diversification', 'diversify', 'portfolio']):
            return """Diversification is a risk management strategy that involves spreading investments 
across various financial instruments, industries, and asset classes. The goal is to reduce portfolio 
risk by ensuring that poor performance in one area doesn't significantly impact overall returns. 
A well-diversified portfolio might include stocks, bonds, real estate, and international investments."""
        
        elif any(word in prompt_lower for word in ['interest rate', 'fed rate', 'central bank']):
            return """Interest rates are the cost of borrowing money, set by central banks like the Federal Reserve. 
They influence economic activity by affecting borrowing costs for consumers and businesses. 
Lower rates typically stimulate economic growth and can boost stock prices, while higher rates 
can slow growth but help control inflation."""
        
        elif any(word in prompt_lower for word in ['bull market', 'bear market']):
            return """A bull market refers to a period of rising stock prices, typically characterized by 
investor optimism and strong economic fundamentals. A bear market is the opposite - a period of 
declining prices (usually 20% or more from recent highs) marked by pessimism and economic concerns. 
These cycles are natural parts of market behavior."""
        
        elif any(word in prompt_lower for word in ['risk management', 'risk tolerance']):
            return """Risk management in investing involves identifying, assessing, and controlling threats 
to your investment portfolio. Key strategies include diversification, asset allocation based on 
risk tolerance, regular portfolio rebalancing, and understanding your investment timeline. 
Risk tolerance varies by individual based on age, income, goals, and psychological comfort with volatility."""
        
        elif any(word in prompt_lower for word in ['compound interest', 'compounding']):
            return """Compound interest is earning interest on both your initial investment and previously 
earned interest. Often called the 'eighth wonder of the world,' it allows investments to grow 
exponentially over time. The key factors are the principal amount, interest rate, compounding frequency, 
and time. Starting early maximizes the power of compounding."""
        
        elif any(word in prompt_lower for word in ['market volatility', 'volatile']):
            return """Market volatility refers to the degree of price fluctuation in financial markets. 
High volatility means larger price swings, while low volatility indicates more stable prices. 
Volatility is influenced by economic news, geopolitical events, corporate earnings, and investor sentiment. 
While concerning short-term, volatility is normal and can create opportunities for long-term investors."""
        
        else:
            return """I'd be happy to help with your financial question, but I need a bit more context. 
Could you please provide more specific details about what you'd like to know? I can assist with 
topics like stock analysis, investment strategies, market concepts, economic indicators, and 
general financial planning."""
