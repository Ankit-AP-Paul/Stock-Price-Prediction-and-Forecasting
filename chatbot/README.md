# Finance LLM Chatbot

A modular financial chatbot that integrates stock analysis and LLM capabilities to provide financial information and advice.

![TCS vs RELIANCE Comparison](TCS_vs_RELIANCE_comparison.png)

## Features

- **Stock Analysis** - Get detailed information about stocks including price history, technical indicators, and performance metrics
- **Investment Advice** - Receive technical analysis-based investment signals and recommendations
- **Stock Comparison** - Compare performance metrics between different stocks
- **Natural Language Interface** - Interact with the chatbot using natural language queries
- **Visualization** - Generate charts and graphs for better data understanding

## Screenshots

### Stock Analysis

![TCS Stock Plot](TCS_stock_plot.png)

### Custom Historical Chart (Any Duration)

![Historical Chart](INFY_stock_plot.png)

## Installation

1. Clone this repository:

```bash
git clone https://github.com/neo-deus/Finance-LLM-Chatbot.git
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Get a Hugging Face API key from [Hugging Face](https://huggingface.co/settings/tokens)

## Usage

Run the chatbot with your Hugging Face API key:

```bash
python main.py --api_key YOUR_HUGGING_FACE_API_KEY
```

Or set the API key as an environment variable:

```bash
# On Windows
set HF_API_KEY=YOUR_HUGGING_FACE_API_KEY
python main.py

# On Linux/Mac
export HF_API_KEY=YOUR_HUGGING_FACE_API_KEY
python main.py
```

### Command-line Arguments

- `--api_key` or `--api-key`: Your Hugging Face API key
- `--model`: Model name to use (default: "google/flan-t5-small")

## Example Commands

Here are some example queries you can ask the chatbot:

### Stock Information

- "What is the current price of Apple?"
- "Show me a chart for Tesla"
- "How has Amazon performed over the past year?"

### Technical Analysis

- "What are the moving averages for Microsoft?"
- "What is the RSI for Google?"
- "Should I buy Netflix stock?"

### Stock Comparison

- "Compare Apple and Microsoft"

## Project Structure

The project follows a modular architecture for improved maintainability:

- `main.py`: Application entry point
- `modules/config.py`: Configuration settings
- `modules/stock_data.py`: Stock data retrieval service
- `modules/company_mapper.py`: Company name to ticker symbol mapping
- `modules/visualization.py`: Plotting and visualization utilities
- `modules/stock_analysis.py`: Stock analysis and investment advice
- `modules/llm_client.py`: LLM integration with Hugging Face API
- `modules/finance_chatbot.py`: Core chatbot integrating all components

## Requirements

- Python 3.9+
- pandas
- numpy
- matplotlib
- yfinance
- requests
- fuzzywuzzy
- python-Levenshtein (optional, for faster fuzzy matching)

## Limitations

- Stock data is retrieved via public APIs which may have rate limits or occasional downtime
- LLM responses depend on the model used and connection to Hugging Face's servers
- Investment advice is based on technical indicators only and should not be considered professional financial advice

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Hugging Face](https://huggingface.co/) for providing access to LLMs
- [Yahoo Finance](https://finance.yahoo.com/) for stock data
- All the open-source libraries used in this project
