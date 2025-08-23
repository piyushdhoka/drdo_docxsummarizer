from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import uvicorn
from backend import summarize_text

# Initialize FastAPI app
app = FastAPI(
    title="Document Summarizer API",
    description="AI-powered document summarization using Google Gemini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Pydantic models for request/response
class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    style: Literal["bullet", "abstract", "detailed"] = Field(
        default="bullet", 
        description="Summary style: bullet, abstract, or detailed"
    )

class SummarizeResponse(BaseModel):
    summary: str = Field(..., description="Generated summary")
    style: str = Field(..., description="Style used for summarization")
    success: bool = Field(..., description="Whether summarization was successful")

class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status")
    message: str = Field(..., description="Health check message")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return HealthResponse(
        status="healthy",
        message="Document Summarizer API is running. Use /docs for interactive documentation."
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        message="API is operational and ready to process requests"
    )

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_document(request: SummarizeRequest):
    """
    Summarize text using AI with specified style.
    
    - **text**: The text content to summarize
    - **style**: Summary format (bullet, abstract, or detailed)
    
    Returns the generated summary with metadata.
    """
    try:
        # Validate input text
        if not request.text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Text cannot be empty"
            )
        
        # Generate summary using backend
        summary = summarize_text(request.text, request.style)
        
        # Check if summarization was successful
        if summary.startswith("Error"):
            raise HTTPException(
                status_code=500,
                detail=f"Summarization failed: {summary}"
            )
        
        return SummarizeResponse(
            summary=summary,
            style=request.style,
            success=True
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/styles")
async def get_available_styles():
    """Get available summary styles."""
    return {
        "styles": [
            {
                "id": "bullet",
                "name": "Bullet Points",
                "description": "Key points in bullet format"
            },
            {
                "id": "abstract", 
                "name": "Abstract",
                "description": "3-4 line concise summary"
            },
            {
                "id": "detailed",
                "name": "Detailed",
                "description": "Comprehensive narrative summary"
            }
        ]
    }

@app.get("/models")
async def get_available_models():
    """Get available Gemini models."""
    try:
        from backend import get_available_models
        models = get_available_models()
        return {"models": models}
    except Exception as e:
        return {"models": [], "error": str(e)}

if __name__ == "__main__":
    # Run with uvicorn when script is executed directly
    uvicorn.run(
        "fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
