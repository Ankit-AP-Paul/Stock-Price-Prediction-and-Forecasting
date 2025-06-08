"""
FastAPI server for Finance LLM Chatbot
Provides REST API endpoints for Next.js frontend integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import os
import sys
import glob

# Add the current directory to Python path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.finance_chatbot import FinanceChatbot

# Initialize FastAPI app
app = FastAPI(
    title="Finance LLM Chatbot API",
    description="REST API for Finance LLM Chatbot with stock analysis and financial advice",
    version="1.0.0"
)

# Configure CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://localhost:3001",  # Alternative Next.js port
        "https://your-domain.com"  # Add your production domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving plot images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global chatbot instance
chatbot = None

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    model_name: Optional[str] = "microsoft/DialoGPT-medium"

class StockPriceRequest(BaseModel):
    ticker: str

class StockAnalysisRequest(BaseModel):
    ticker: str
    analysis_type: str = "basic"  # "basic", "technical", "investment_advice"

class InitRequest(BaseModel):
    api_key: Optional[str] = None
    model_name: Optional[str] = "microsoft/DialoGPT-medium"

class HealthResponse(BaseModel):
    status: str
    message: str
    chatbot_initialized: bool

class StockPriceResponse(BaseModel):
    ticker: str
    company_name: str
    current_price: float
    currency: str
    change_percent: Optional[float] = None
    status: str

class StockAnalysisResponse(BaseModel):
    ticker: str
    company_name: str
    analysis: Dict[str, Any]
    status: str
    image_url: Optional[str] = None  # URL to generated plot image

class StockComparisonResponse(BaseModel):
    ticker1: str
    ticker2: str
    company1_name: str
    company2_name: str
    comparison: Dict[str, Any]
    status: str
    image_url: Optional[str] = None  # URL to comparison plot

class ChatResponse(BaseModel):
    response: str
    status: str
    message_type: str
    image_url: Optional[str] = None  # URL to generated plot if available

class ImageListResponse(BaseModel):
    images: List[Dict[str, str]]  # List of {filename, url, type, created_at}
    count: int

# Initialize chatbot on startup
@app.on_event("startup")
async def startup_event():
    global chatbot
    # Initialize with environment variable if available
    api_key = os.environ.get("HF_API_KEY")
    chatbot = FinanceChatbot(api_key=api_key)
    print("✅ Finance Chatbot API initialized")

# Helper functions for image management
def get_latest_image(pattern: str) -> Optional[str]:
    """Get the most recently created image matching the pattern"""
    try:
        # Search in the static directory since images are now saved there directly
        static_pattern = os.path.join("static", pattern)
        images = glob.glob(static_pattern)
        if not images:
            return None
        # Get the most recent image
        latest_image = max(images, key=os.path.getctime)
        return latest_image
    except Exception as e:
        print(f"Error finding image: {e}")
        return None

def move_image_to_static(image_path: str) -> Optional[str]:
    """Return URL for image already in static directory"""
    try:
        if not image_path or not os.path.exists(image_path):
            return None
        
        filename = os.path.basename(image_path)
        # Images are already in static directory, just return the URL
        return f"/static/{filename}"
    except Exception as e:
        print(f"Error getting image URL: {e}")
        return None

def get_all_images() -> List[Dict[str, str]]:
    """Get all available images with metadata"""
    images = []
    try:
        # Get all PNG files in current directory and static directory
        current_dir_images = glob.glob("*.png")
        static_dir_images = glob.glob("static/*.png")
        
        for img_path in current_dir_images + static_dir_images:
            if os.path.exists(img_path):
                filename = os.path.basename(img_path)
                
                # Determine image type from filename
                img_type = "unknown"
                if "_vs_" in filename or "comparison" in filename:
                    img_type = "comparison"
                elif "_stock_plot" in filename:
                    img_type = "stock_analysis"
                elif "performance" in filename:
                    img_type = "performance"
                
                # Get creation time
                created_at = os.path.getctime(img_path)
                
                images.append({
                    "filename": filename,
                    "url": f"/static/{filename}" if img_path.startswith("static/") else f"/static/{filename}",
                    "type": img_type,
                    "created_at": str(created_at)
                })
    except Exception as e:
        print(f"Error getting images: {e}")
    
    return images

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API status"""
    return HealthResponse(
        status="healthy",
        message="Finance LLM Chatbot API is running",
        chatbot_initialized=chatbot is not None
    )

# Initialize chatbot with custom settings
@app.post("/init")
async def initialize_chatbot(request: InitRequest):
    """Initialize or reinitialize chatbot with custom API key and model"""
    global chatbot
    try:
        chatbot = FinanceChatbot(
            api_key=request.api_key,
            model_name=request.model_name
        )
        return {
            "status": "success",
            "message": f"Chatbot initialized with model: {request.model_name}",
            "api_key_provided": bool(request.api_key)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize chatbot: {str(e)}")

# Main chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint for general questions and stock analysis"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        # Reinitialize with new API key if provided
        if request.api_key and request.api_key != chatbot.llm_client.api_key:
            chatbot = FinanceChatbot(
                api_key=request.api_key,                model_name=request.model_name
            )
        
        # Get response from chatbot
        response = chatbot.get_response(request.message)
        
        # Determine message type based on content
        message_type = "general"
        message_lower = request.message.lower()
        if any(word in message_lower for word in ["price", "current", "trading at"]):
            message_type = "price_query"
        elif any(word in message_lower for word in ["analyze", "analysis", "technical", "moving average", "moving averages", "ma", "rsi", "macd", "bollinger", "indicators", "chart", "plot"]):
            message_type = "stock_analysis"
        elif any(word in message_lower for word in ["should i buy", "should i invest", "investment", "advice", "good investment", "buy recommendation", "invest in"]):
            message_type = "investment_advice"
        elif any(word in message_lower for word in ["compare", "vs", "versus"]):
            message_type = "stock_comparison"
        elif any(word in message_lower for word in ["performance", "how has"]):
            message_type = "performance_analysis"
        
        # Check for generated images based on message type
        image_url = None
        if message_type in ["stock_comparison", "performance_analysis", "stock_analysis", "investment_advice"]:
            if message_type == "stock_comparison":
                latest_image = get_latest_image("*comparison*.png")
            elif message_type == "performance_analysis":
                latest_image = get_latest_image("*stock_plot*.png")  # Performance analysis generates stock_plot files
            else:  # stock_analysis or investment_advice
                latest_image = get_latest_image("*stock_plot*.png")
            
            if latest_image:
                image_url = move_image_to_static(latest_image)
        
        return ChatResponse(
            response=response,
            status="success",
            message_type=message_type,
            image_url=image_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

# Dedicated stock price endpoint
@app.post("/stock/price", response_model=StockPriceResponse)
async def get_stock_price(request: StockPriceRequest):
    """Get current stock price for a specific ticker"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        # Get company info
        company_info = chatbot.company_mapper.extract_company_name(request.ticker.upper())
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Ticker {request.ticker} not found")
        
        ticker, company_name, _ = company_info
        
        # Get current price
        current_price = chatbot.stock_data_service.get_current_price(ticker)
        if current_price is None:
            raise HTTPException(status_code=404, detail=f"Could not retrieve price for {ticker}")
        
        # Get currency symbol
        currency = "₹" if chatbot.stock_data_service._is_indian_stock(ticker) else "$"
        
        # Try to get daily change
        change_percent = None
        try:
            data = chatbot.stock_data_service.get_stock_data(ticker, "5d")
            if data is not None and not data.empty and len(data) >= 2:
                change_percent = ((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
        except:
            pass
        
        return StockPriceResponse(
            ticker=ticker,
            company_name=company_name,
            current_price=current_price,
            currency=currency,
            change_percent=change_percent,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stock price: {str(e)}")

# Stock analysis endpoint
@app.post("/stock/analysis", response_model=StockAnalysisResponse)
async def get_stock_analysis(request: StockAnalysisRequest):
    """Get detailed stock analysis"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        # Get company info
        company_info = chatbot.company_mapper.extract_company_name(request.ticker.upper())
        if not company_info:
            raise HTTPException(status_code=404, detail=f"Ticker {request.ticker} not found")
        
        ticker, company_name, _ = company_info
        
        # Get analysis based on type
        if request.analysis_type == "technical":
            analysis = chatbot.stock_analyzer.get_technical_analysis(ticker)
        elif request.analysis_type == "investment_advice":
            analysis = chatbot.stock_analyzer.get_investment_advice(ticker)
        else:  # basic
            analysis = chatbot.stock_analyzer.analyze_stock(ticker)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return StockAnalysisResponse(
            ticker=ticker,
            company_name=company_name,
            analysis=analysis,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stock analysis: {str(e)}")

# Stock comparison endpoint
@app.post("/stock/compare", response_model=StockComparisonResponse)
async def compare_stocks(ticker1: str, ticker2: str):
    """Compare two stocks"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    try:
        # Get company info for both tickers
        company1_info = chatbot.company_mapper.extract_company_name(ticker1.upper())
        company2_info = chatbot.company_mapper.extract_company_name(ticker2.upper())
        
        if not company1_info:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker1} not found")
        if not company2_info:
            raise HTTPException(status_code=404, detail=f"Ticker {ticker2} not found")
        
        ticker1, company1_name, _ = company1_info
        ticker2, company2_name, _ = company2_info
        
        # Get comparison data
        comparison = chatbot.stock_analyzer.get_stock_comparison(ticker1, ticker2)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return StockComparisonResponse(
            ticker1=ticker1,
            ticker2=ticker2,
            company1_name=company1_name,
            company2_name=company2_name,
            comparison=comparison,
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing stocks: {str(e)}")

# Image management endpoints
@app.get("/images", response_model=ImageListResponse)
async def list_images():
    """List all available generated images"""
    try:
        images = get_all_images()
        return ImageListResponse(
            images=images,
            count=len(images)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

@app.get("/images/latest/{image_type}")
async def get_latest_image_by_type(image_type: str):
    """Get the latest image of a specific type (comparison, stock_analysis, performance)"""
    try:
        pattern_map = {
            "comparison": "*comparison*.png",
            "stock_analysis": "*stock_plot*.png", 
            "performance": "*performance*.png",
            "all": "*.png"
        }
        
        pattern = pattern_map.get(image_type, "*.png")
        latest_image = get_latest_image(pattern)
        
        if not latest_image:
            raise HTTPException(status_code=404, detail=f"No {image_type} images found")
        
        # Move to static directory and get URL
        image_url = move_image_to_static(latest_image)
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to serve image")
        
        return {
            "image_url": image_url,
            "filename": os.path.basename(latest_image),
            "type": image_type
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting latest image: {str(e)}")

# List available endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Finance LLM Chatbot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "GET /health - Check API status",
            "chat": "POST /chat - General chat and financial questions",
            "init": "POST /init - Initialize chatbot with custom settings",
            "stock_price": "POST /stock/price - Get current stock price",
            "stock_analysis": "POST /stock/analysis - Get stock analysis",
            "stock_compare": "POST /stock/compare - Compare two stocks",
            "docs": "GET /docs - Interactive API documentation"
        },
        "frontend_integration": {
            "cors_enabled": True,
            "supported_origins": ["http://localhost:3000", "http://localhost:3001"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
