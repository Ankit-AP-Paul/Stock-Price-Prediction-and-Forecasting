from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import uvicorn
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="FinBERT Sentiment Analysis API",
    description="API for financial sentiment analysis using fine-tuned FinBERT model",
    version="1.0.0"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global variables for model and tokenizer
model = None
tokenizer = None
sentiment_pipeline = None

# Pydantic models for request/response


class TextInput(BaseModel):
    text: str = Field(..., description="Text to analyze for sentiment",
                      min_length=1, max_length=512)


class BatchTextInput(BaseModel):
    texts: List[str] = Field(..., description="List of texts to analyze for sentiment",
                             min_items=1, max_items=100)


class SentimentResponse(BaseModel):
    text: str
    label: str
    score: float


class BatchSentimentResponse(BaseModel):
    results: List[SentimentResponse]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

# Model loading function


def load_model(model_path: str = "finbert-sentiment/"):
    """Load the fine-tuned FinBERT model and tokenizer"""
    global model, tokenizer, sentiment_pipeline

    try:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model directory {model_path} not found")

        logger.info(f"Loading model from {model_path}")

        # Load tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForSequenceClassification.from_pretrained(model_path)

        # Create pipeline
        sentiment_pipeline = pipeline(
            'sentiment-analysis',
            model=model,
            tokenizer=tokenizer,
            return_all_scores=True
        )

        logger.info("Model loaded successfully")
        return True

    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False


@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    success = load_model()
    if not success:
        logger.warning(
            "Failed to load model on startup. Model will need to be loaded manually.")


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "FinBERT Sentiment Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "/predict": "POST - Analyze sentiment of a single text",
            "/predict/batch": "POST - Analyze sentiment of multiple texts",
            "/health": "GET - Check API and model health",
            "/reload-model": "POST - Reload the model"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if sentiment_pipeline is not None else "model_not_loaded",
        model_loaded=sentiment_pipeline is not None
    )


@app.post("/predict", response_model=SentimentResponse)
async def predict_sentiment(input_data: TextInput):
    """Predict sentiment for a single text"""
    if sentiment_pipeline is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please check /health endpoint.")

    try:
        # Get prediction
        results = sentiment_pipeline(input_data.text)

        # Find the prediction with highest score
        best_result = max(results[0], key=lambda x: x['score'])

        return SentimentResponse(
            text=input_data.text,
            label=best_result['label'],
            score=best_result['score']
        )

    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchSentimentResponse)
async def predict_sentiment_batch(input_data: BatchTextInput):
    """Predict sentiment for multiple texts"""
    if sentiment_pipeline is None:
        raise HTTPException(
            status_code=503, detail="Model not loaded. Please check /health endpoint.")

    try:
        # Get predictions for all texts
        all_results = sentiment_pipeline(input_data.texts)

        # Process results
        processed_results = []
        for i, text in enumerate(input_data.texts):
            best_result = max(all_results[i], key=lambda x: x['score'])
            processed_results.append(SentimentResponse(
                text=text,
                label=best_result['label'],
                score=best_result['score']
            ))

        return BatchSentimentResponse(results=processed_results)

    except Exception as e:
        logger.error(f"Error during batch prediction: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post("/reload-model")
async def reload_model(model_path: Optional[str] = "finbert-sentiment/"):
    """Reload the model (useful for updating the model without restarting the server)"""
    try:
        success = load_model(model_path)
        if success:
            return {"message": "Model reloaded successfully", "status": "success"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to reload model")
    except Exception as e:
        logger.error(f"Error reloading model: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Model reload failed: {str(e)}")


@app.get("/labels")
async def get_labels():
    """Get the available sentiment labels"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "labels": list(model.config.id2label.values()),
        "label_mapping": model.config.id2label
    }

# Exception handlers


@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "message": "Please check the available endpoints at /"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "Something went wrong on the server"}
