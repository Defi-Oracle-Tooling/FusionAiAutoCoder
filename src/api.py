"""
API module for FusionAiAutoCoder.
Provides HTTP endpoints for accessing the core functionality.
"""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime

from .config.config_multi_agents import AgentOrchestrator
from .utils import setup_logging, validate_request

# Setup logging
logger = setup_logging()

# Initialize FastAPI
app = FastAPI(
    title="FusionAiAutoCoder API",
    description="API for AI-assisted code generation and optimization",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task storage for background tasks
tasks = {}

# Models for request/response schema
class TaskRequest(BaseModel):
    task_type: str
    task_data: Dict[str, Any]

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class GenerateCodeRequest(BaseModel):
    prompt: str
    language: str = "python"
    complexity: str = "low"
    use_gpu: bool = False
    framework: Optional[str] = None

class OptimizeCodeRequest(BaseModel):
    code: str
    optimization_target: str = "performance"
    language: str = "python"

class BatchRequest(BaseModel):
    tasks: List[TaskRequest]

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float

class WorkflowRequest(BaseModel):
    workflow_type: str
    requirements: List[str]
    scale: str = "medium"
    constraints: Dict[str, Any] = {}
    timeout: Optional[int] = 300
    priority: Optional[str] = "normal"

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

@app.post("/api/v1/workflow", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    request_context: Request
):
    """
    Create and execute a new workflow with enhanced error handling and monitoring.
    """
    try:
        workflow_id = f"wf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{id(request)}"
        
        # Validate and preprocess the request
        validate_request(request)
        
        # Initialize workflow context
        workflow_context = {
            "id": workflow_id,
            "start_time": datetime.utcnow(),
            "client_info": {
                "ip": request_context.client.host,
                "user_agent": request_context.headers.get("user-agent")
            }
        }
        
        # Initialize orchestrator with appropriate configuration
        orchestrator = AgentOrchestrator(
            config_path="config/agent_config.json",
            workflow_context=workflow_context
        )
        
        # Schedule the workflow execution
        background_tasks.add_task(
            execute_workflow,
            orchestrator=orchestrator,
            workflow_id=workflow_id,
            request=request
        )
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status="scheduled",
            metadata={
                "estimated_completion": datetime.utcnow().timestamp() + request.timeout,
                "priority": request.priority
            }
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Workflow creation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/v1/workflow/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get the current status and results of a workflow.
    """
    try:
        result = await workflow_store.get_workflow(workflow_id)
        if not result:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(
            workflow_id=workflow_id,
            status=result["status"],
            results=result.get("results"),
            errors=result.get("errors", []),
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logging.error(f"Error retrieving workflow {workflow_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

async def execute_workflow(
    orchestrator: AgentOrchestrator,
    workflow_id: str,
    request: WorkflowRequest
) -> None:
    """
    Execute a workflow with comprehensive error handling and monitoring.
    """
    try:
        # Initialize workflow monitoring
        monitor = WorkflowMonitor(workflow_id)
        monitor.start()
        
        # Execute the workflow based on type
        if request.workflow_type == "architecture_design":
            results = await orchestrator._architecture_design_workflow(request.dict())
        elif request.workflow_type == "code_generation":
            results = await orchestrator._code_generation_workflow(request.dict())
        else:
            results = await orchestrator._default_workflow(request.dict())
        
        # Update workflow status
        await workflow_store.update_workflow(
            workflow_id,
            status="completed",
            results=results
        )
        
    except asyncio.TimeoutError:
        error_details = {
            "type": "timeout",
            "message": f"Workflow execution exceeded timeout of {request.timeout}s"
        }
        await handle_workflow_error(workflow_id, error_details)
        
    except Exception as e:
        error_details = {
            "type": "execution_error",
            "message": str(e),
            "traceback": logging.format_exc()
        }
        await handle_workflow_error(workflow_id, error_details)
    
    finally:
        monitor.stop()

async def handle_workflow_error(workflow_id: str, error_details: Dict[str, Any]) -> None:
    """
    Handle workflow errors with proper logging and status updates.
    """
    logging.error(f"Workflow {workflow_id} failed: {error_details}")
    
    await workflow_store.update_workflow(
        workflow_id,
        status="failed",
        errors=[error_details],
        metadata={
            "failure_time": datetime.utcnow().timestamp(),
            "recovery_attempted": False
        }
    )

class WorkflowMonitor:
    """
    Monitor workflow execution and collect metrics.
    """
    def __init__(self, workflow_id: str):
        self.workflow_id = workflow_id
        self.start_time = None
        self.metrics = {}
    
    def start(self):
        self.start_time = datetime.utcnow()
        logging.info(f"Started monitoring workflow {self.workflow_id}")
    
    def stop(self):
        if self.start_time:
            duration = (datetime.utcnow() - self.start_time).total_seconds()
            self.metrics["duration"] = duration
            logging.info(f"Workflow {self.workflow_id} completed in {duration}s")

# Run the app if executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("src.api:app", host="0.0.0.0", port=port, reload=True)