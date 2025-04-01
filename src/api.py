"""FastAPI application module."""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field
import logging
import json
from datetime import datetime  # type: ignore

from src.main import run_workflow, run_batch_process
from src.utils import get_version_info, setup_logging

logger: logging.Logger = setup_logging()
app: FastAPI = FastAPI()


class GenerateCodeRequest(BaseModel):
    """Request model for code generation."""

    prompt: str = Field(..., description="The prompt describing the code to generate")
    language: str = Field("python", description="Target programming language")
    complexity: str = Field("medium", description="Expected complexity of the task")
    use_gpu: bool = Field(False, description="Whether to use GPU acceleration")
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")


class OptimizeCodeRequest(BaseModel):
    """Request model for code optimization."""

    code: str = Field(..., description="The code to optimize")
    language: str = Field("python", description="Programming language of the code")
    target: str = Field(
        "performance", description="Optimization target (performance/memory)"
    )
    options: Optional[Dict[str, Any]] = Field(None, description="Additional options")


class BatchRequest(BaseModel):
    """Request model for batch processing."""

    tasks: List[Dict[str, Any]] = Field(..., description="List of tasks to process")
    parallel: bool = Field(True, description="Whether to process tasks in parallel")


def verify_api_key(x_api_key: str = Header(...)) -> None:
    """Verify the API key from headers."""
    valid_key: str = "your-api-key"  # In production, use secure storage
    if x_api_key != valid_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
async def read_root() -> Dict[str, Any]:
    """Root endpoint returning version information."""
    version_info: Dict[str, str] = get_version_info()
    return {
        "name": "FusionAiAutoCoder API",
        "version": version_info["version"],
        "status": "operational",
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    version_info: Dict[str, str] = get_version_info()
    current_time = datetime.now(datetime.timezone.utc)
    return {
        "status": "healthy",
        "timestamp": current_time.isoformat(),
        "version": version_info["version"],
    }


@app.post("/api/v1/generate")
async def generate_code(
    request: GenerateCodeRequest, _: None = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Generate code based on the provided prompt."""
    try:
        result: Dict[str, Any] = run_workflow(
            task_type="code_generation", task_data=request.model_dump()
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in code generation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/optimize")
async def optimize_code(
    request: OptimizeCodeRequest, _: None = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Optimize the provided code."""
    try:
        result: Dict[str, Any] = run_workflow(
            task_type="code_optimization", task_data=request.model_dump()
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in code optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/batch")
async def batch_process_tasks(
    request: BatchRequest, _: None = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """Process multiple tasks in batch."""
    try:
        results: List[Dict[str, Any]] = run_batch_process(request.tasks)
        return results
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
