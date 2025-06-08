# 🚀 Finance LLM Chatbot

A comprehensive financial analysis chatbot that combines the power of Large Language Models (LLMs) with real-time stock data analysis, technical indicators, and intelligent investment recommendations. Built with a modular architecture supporting both command-line interface and web API for seamless integration.

![Finance Chatbot Banner](static/banner.png)

## ✨ Features

### 📊 **Advanced Stock Analysis**

- **Real-time Stock Data**: Current prices, historical data, and market trends
- **Technical Indicators**: RSI, Moving Averages (SMA/EMA), MACD, Bollinger Bands
- **Price Charts**: Interactive visualizations with customizable time periods
- **Volume Analysis**: Trading volume trends and patterns
- **Market Performance**: Comprehensive stock performance metrics

### 🤖 **AI-Powered Investment Advice**

- **Technical Analysis**: Algorithm-based buy/sell/hold recommendations
- **Risk Assessment**: Volatility analysis and risk indicators
- **Market Sentiment**: Trend analysis and momentum indicators
- **Investment Signals**: Clear actionable investment recommendations
- **Portfolio Insights**: Multi-stock analysis and comparison

### 💬 **Natural Language Interface**

- **Conversational AI**: Chat naturally about stocks and investments
- **Context Awareness**: Understands financial terminology and context
- **Multiple Query Types**: Support for various question formats
- **Intelligent Parsing**: Smart extraction of stock tickers and time periods

### 🌐 **Multi-Platform Support**

- **Command Line Interface**: Direct terminal interaction
- **REST API**: FastAPI-based web service
- **Web Dashboard**: HTML demo interface
- **Next.js Integration**: Ready-to-use React components
- **Image Server**: Dedicated visualization hosting

### 📈 **Visual Analytics**

- **Dynamic Charts**: Auto-generated stock plots and comparisons
- **Technical Overlays**: Moving averages, trend lines, and indicators
- **Comparison Charts**: Side-by-side stock performance analysis
- **Export Capabilities**: Save charts as high-quality images

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Hugging Face API key ([Get one here](https://huggingface.co/settings/tokens))

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/neo-deus/Finance-LLM-Chatbot.git
cd Finance-LLM-Chatbot
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up your API key:**

```bash
# Windows
set HF_API_KEY=your_hugging_face_api_key

# Linux/Mac
export HF_API_KEY=your_hugging_face_api_key
```

4. **Run the chatbot:**

```bash
# Command line interface
python main.py

# Or with specific API key
python main.py --api-key your_hugging_face_api_key
```

## 🌐 Web API & Integration

### Starting the API Server

```bash
# Start the FastAPI server
uvicorn api:app --host 0.0.0.0 --port 8001 --reload
or
python api.py

# Start the image server (for serving generated charts)
python image_server.py
```

### API Endpoints

#### Chat Endpoint

```http
POST /chat
Content-Type: application/json

{
  "message": "What is the current price of TCS?",
  "api_key": "your_hugging_face_api_key",
  "model_name": "microsoft/DialoGPT-medium"
}
```

#### Stock Price Endpoint

```http
POST /stock-price
Content-Type: application/json

{
  "ticker": "TCS.NS"
}
```

#### Get Generated Images

```http
GET /images
```

### Next.js Integration

The project includes a complete Next.js component for easy frontend integration:

```tsx
import FinanceChatbot from "./components/FinanceChatbot";

export default function HomePage() {
  return (
    <div>
      <h1>My Indian Stock Market Dashboard</h1>
      <FinanceChatbot apiKey="your_api_key" />
    </div>
  );
}
```

### Web Demo

Open `demo.html` in your browser for a complete web interface:

```bash
# After starting the API server
open demo.html  # or simply double-click the file
```

## 🏗️ Architecture

### Project Structure

```
Finance-LLM-Chatbot/
├── main.py                          # CLI entry point
├── api.py                          # FastAPI web server
├── image_server.py                 # Static file server for charts
├── demo.html                       # Web demo interface
├── nextjs-integration-example.tsx  # React/Next.js component
├── requirements.txt                # Python dependencies
├── static/                         # Generated charts and images
├── modules/
│   ├── finance_chatbot.py         # Core chatbot logic
│   ├── stock_data.py              # Stock data retrieval
│   ├── stock_analysis.py          # Technical analysis
│   ├── visualization.py           # Chart generation
│   ├── llm_client.py              # LLM integration
│   ├── company_mapper.py          # Company name mapping
│   └── config.py                  # Configuration settings
└── tests/                         # Test files
```

### Key Modules

#### `FinanceChatbot` (Core Engine)

- Main orchestrator combining all components
- Natural language processing and intent detection
- Response generation and formatting

#### `StockData` (Data Layer)

- Real-time stock data from Yahoo Finance
- Historical price data retrieval
- Market data validation and cleaning

#### `StockAnalysis` (Analysis Engine)

- Technical indicator calculations
- Investment recommendation algorithms
- Risk assessment and scoring

#### `Visualization` (Chart Engine)

- Dynamic chart generation with matplotlib
- Technical indicator overlays
- Comparison and trend visualizations

#### `LLMClient` (AI Integration)

- Hugging Face API integration
- Context-aware response generation
- Model management and optimization

## 🔧 Configuration

### Environment Variables

```bash
# Required
HF_API_KEY=your_hugging_face_api_key

# Optional
DEFAULT_MODEL=microsoft/DialoGPT-medium
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --api-key TEXT     Hugging Face API key
  --model TEXT       Model name (default: google/flan-t5-small)
  --help            Show this message and exit
```

### API Configuration

```bash
uvicorn api:app [OPTIONS]

Options:
  --host TEXT        Host address (default: 0.0.0.0)
  --port INTEGER     Port number (default: 8001)
  --reload          Enable auto-reload for development
```

## 📊 Supported Features

### Stock Data Sources

- ✅ Yahoo Finance (Primary source for Indian stocks)
- ✅ Real-time pricing for NSE/BSE listed companies
- ✅ Historical data (up to 10 years)
- ✅ Indian stock markets (NSE, BSE)
- ✅ Major Indian indices (NIFTY, SENSEX) and ETFs

### Technical Indicators

- ✅ Simple Moving Average (SMA)
- ✅ Exponential Moving Average (EMA)
- ✅ Relative Strength Index (RSI)
- ✅ MACD (Moving Average Convergence Divergence)
- ✅ Bollinger Bands
- ✅ Volume analysis
- ✅ Price momentum

### Investment Analysis

- ✅ Buy/Sell/Hold recommendations
- ✅ Risk assessment scores
- ✅ Volatility analysis
- ✅ Trend identification
- ✅ Support/Resistance levels
- ✅ Entry/Exit point suggestions

### Visualization Types

- ✅ Historical Price charts
- ✅ Technical indicator overlays
- ✅ Comparison charts

## 🚀 Deployment

### Local Development

```bash
# Terminal 1: API Server
uvicorn api:app --reload --port 8001

# Terminal 2: Image Server
python image_server.py

# Terminal 3: CLI Interface
python main.py
```

### Production Deployment

#### Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Cloud Platforms

- **Heroku**: Deploy with included `Procfile`
- **AWS Lambda**: Serverless deployment ready
- **Google Cloud Run**: Container-ready
- **Azure Container Instances**: Full compatibility

### Environment Setup

```bash
# Production environment variables
export HF_API_KEY=your_production_api_key
export ENVIRONMENT=production
export LOG_LEVEL=INFO
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test categories
python test_api.py                    # API functionality
python test_stock_data.py            # Stock data retrieval
python test_investment_advice.py     # Investment analysis
python test_visualization.py         # Chart generation
```

### Test Coverage

- ✅ Stock data retrieval and validation
- ✅ Technical indicator calculations
- ✅ Investment recommendation logic
- ✅ API endpoint functionality
- ✅ Chart generation and saving
- ✅ Error handling and edge cases

## 📚 API Documentation

### Interactive API Docs

Once the server is running, visit:

- **Swagger UI**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

## ⚠️ Important Notes

### Data & Accuracy

- Stock data is sourced from Yahoo Finance and may have slight delays
- Technical indicators are calculated using standard formulas
- Investment advice is algorithmic and not professional financial advice
- Always consult qualified financial advisors for investment decisions

### Rate Limits

- Yahoo Finance: No official limits, but respectful usage recommended
- Hugging Face API: Depends on your subscription tier
- Consider implementing caching for production use

### Legal Disclaimer

This software is for educational and informational purposes only. The investment advice generated by this chatbot is based on technical analysis algorithms and should not be considered as professional financial advice. Always consult with qualified financial advisors before making investment decisions.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Fork and clone the repo
git clone https://github.com/your-username/Finance-LLM-Chatbot.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Hugging Face](https://huggingface.co/)** - For providing access to state-of-the-art language models
- **[Yahoo Finance](https://finance.yahoo.com/)** - For comprehensive financial data
- **[yfinance](https://github.com/ranaroussi/yfinance)** - Python library for Yahoo Finance data
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern web framework for building APIs
- **[Matplotlib](https://matplotlib.org/)** - Comprehensive plotting library
- **Open Source Community** - For the amazing libraries that make this project possible

---

⭐ **Star this repository if you find it helpful!** ⭐
