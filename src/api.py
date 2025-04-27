"""FastAPI application module."""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from pydantic import BaseModel, Field, validator
import logging
import json
from datetime import datetime, timezone  # type: ignore
import os
import redis
from celery import Celery
import asyncio

from src.main import hybrid_workflow, run_batch_process
from src.utils import get_version_info, setup_logging
from src.config.config_multi_agents import setup_agents

logger: logging.Logger = setup_logging()
app: FastAPI = FastAPI()

AGENT_WORKFLOW_TRIGGER_TOPIC = "agent.workflow.triggers"


# --- Persistent Storage: Redis ---
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# --- Distributed Workers: Celery ---
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/1")
celery_app = Celery("fusion_ai_agents", broker=CELERY_BROKER_URL)


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


# --- Advanced Validation for AgentTriggerRequest ---
class AgentTriggerRequest(BaseModel):
    agentType: str = Field(..., description="Type of agent to trigger (e.g., compliance, grant_review, court_triage, security)")
    countryCode: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    payload: Dict[str, Any] = Field(..., description="Payload for the agent workflow")

    @validator("countryCode")
    def validate_country_code(cls, v):
        if len(v) != 2 or not v.isalpha():
            raise ValueError("countryCode must be a valid ISO 3166-1 alpha-2 code")
        return v.upper()

    @validator("agentType")
    def validate_agent_type(cls, v):
        allowed = {"compliance", "grant_review", "court_triage", "security"}
        if v.lower() not in allowed:
            raise ValueError(f"agentType must be one of {allowed}")
        return v.lower()


class AgentStatusResponse(BaseModel):
    workflowId: str
    status: str
    result: Optional[Dict[str, Any]] = None


class AgentInfoResponse(BaseModel):
    agentKey: str
    countryCode: str
    agentType: str
    description: str
    capabilities: List[str]
    owners: List[str]


class AgentWorkflowResult(BaseModel):
    workflowId: str
    agentKey: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    startedAt: Optional[str] = None
    completedAt: Optional[str] = None


# --- Redis-backed workflow status store ---
def set_workflow_status(*, workflow_id: str, status: str, result: Optional[Any] = None, error: str = None, started_at: str = None, completed_at: str = None):
    # Always convert result to dict if it's a Pydantic model
    if result is not None:
        if hasattr(result, 'dict'):
            result = result.dict()
        elif hasattr(result, 'model_dump'):
            result = result.model_dump()
        elif not isinstance(result, dict):
            result = dict(result)
    data = {
        "status": status,
        "result": json.dumps(result) if result is not None else None,
        "error": error,
        "startedAt": started_at,
        "completedAt": completed_at
    }
    redis_client.hmset(f"workflow:{workflow_id}", {k: v for k, v in data.items() if v is not None})

def get_workflow_status(workflow_id: str):
    data = redis_client.hgetall(f"workflow:{workflow_id}")
    if not data:
        return None
    return {
        "status": data.get("status"),
        "result": json.loads(data["result"]) if data.get("result") else None,
        "error": data.get("error"),
        "startedAt": data.get("startedAt"),
        "completedAt": data.get("completedAt")
    }


# --- Celery distributed worker for agent workflows ---
@celery_app.task
def process_agent_workflow(event: dict):
    orchestrator = setup_agents()
    workflow_id = event.get("workflowId")
    payload = event.get("payload", {})
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        result = orchestrator.create_workflow(event.get("agentType"), payload)
        if hasattr(result, 'dict'):
            result = result.dict()
        elif hasattr(result, 'model_dump'):
            result = result.model_dump()
        if not isinstance(result, dict):
            logger.warning(f"Result for workflow {workflow_id} is not a dict, got {type(result)}. Setting result to None.")
            result = None
        completed_at = datetime.now(timezone.utc).isoformat()
        set_workflow_status(
            workflow_id=workflow_id,
            status="completed",
            result=result,
            started_at=started_at,
            completed_at=completed_at
        )
    except Exception as e:
        set_workflow_status(
            workflow_id=workflow_id,
            status="failed",
            result=None,
            error=str(e),
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat()
        )


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
    current_time = datetime.now(timezone.utc)
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
        result: Dict[str, Any] = await hybrid_workflow(
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
        result: Dict[str, Any] = await hybrid_workflow(
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


@app.post("/api/v1/agents/trigger", response_model=AgentStatusResponse)
async def trigger_agent_workflow(request: AgentTriggerRequest, _: None = Depends(verify_api_key)) -> AgentStatusResponse:
    """Trigger an agent workflow (event-driven)."""
    import uuid
    workflow_id = str(uuid.uuid4())
    orchestrator = setup_agents()
    agent_key = f"{request.countryCode}_{request.agentType.lower()}"
    if agent_key not in orchestrator.agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_key} not found in registry")
    event = {
        "workflowId": workflow_id,
        "agentType": request.agentType,
        "countryCode": request.countryCode,
        "payload": request.payload,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await orchestrator.send_event(topic=AGENT_WORKFLOW_TRIGGER_TOPIC, message=event)
    set_workflow_status(workflow_id=workflow_id, status="queued")
    # Optionally, trigger Celery worker directly for demo (in prod, use event bus)
    process_agent_workflow.delay(event)
    return AgentStatusResponse(workflowId=workflow_id, status="queued")


@app.get("/api/v1/agents/status/{workflow_id}", response_model=AgentStatusResponse)
async def get_agent_workflow_status(workflow_id: str, _: None = Depends(verify_api_key)) -> AgentStatusResponse:
    """Get the status of an agent workflow."""
    status = get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return AgentStatusResponse(workflowId=workflow_id, status=status["status"], result=status["result"])


@app.get("/api/v1/agents/registry", response_model=List[AgentInfoResponse])
async def list_agents(_: None = Depends(verify_api_key)) -> List[AgentInfoResponse]:
    """List all registered agents."""
    orchestrator = setup_agents()
    agents = []
    for key, agent in orchestrator.agents.items():
        country, agent_type = key.split("_", 1)
        agents.append(AgentInfoResponse(
            agentKey=key,
            countryCode=country,
            agentType=agent_type,
            description=agent.description,
            capabilities=agent.capabilities,
            owners=agent.parameters.get("owners", [])
        ))
    return agents


@app.post("/api/v1/agents/cancel/{workflow_id}", response_model=AgentStatusResponse)
async def cancel_agent_workflow(workflow_id: str, _: None = Depends(verify_api_key)) -> AgentStatusResponse:
    """Cancel an agent workflow (if supported)."""
    status = get_workflow_status(workflow_id)
    if not status:
        raise HTTPException(status_code=404, detail="Workflow not found")
    if status["status"] in ("completed", "cancelled"):
        return AgentStatusResponse(workflowId=workflow_id, status=status["status"], result=status["result"])
    set_workflow_status(
        workflow_id=workflow_id,
        status="cancelled",
        result=status["result"],
        started_at=status["startedAt"],
        completed_at=status["completedAt"]
    )
    return AgentStatusResponse(workflowId=workflow_id, status="cancelled")


# --- Production-Grade Event Processing ---
from concurrent.futures import ThreadPoolExecutor
import threading

def start_agent_event_listener():
    loop = asyncio.get_event_loop()
    orchestrator = setup_agents()
    async def process_events():
        async for event in orchestrator.receive_events(topic=AGENT_WORKFLOW_TRIGGER_TOPIC):
            workflow_id = event.get("workflowId")
            payload = event.get("payload", {})
            started_at = datetime.now(timezone.utc).isoformat()
            try:
                result = orchestrator.create_workflow(event.get("agentType"), payload)
                if hasattr(result, 'dict'):
                    result = result.dict()
                elif hasattr(result, 'model_dump'):
                    result = result.model_dump()
                if not isinstance(result, dict):
                    logger.warning(f"Result for workflow {workflow_id} is not a dict, got {type(result)}. Setting result to None.")
                    result = None
                completed_at = datetime.now(timezone.utc).isoformat()
                set_workflow_status(
                    workflow_id=workflow_id,
                    status="completed",
                    result=result,
                    started_at=started_at,
                    completed_at=completed_at
                )
            except Exception as e:
                set_workflow_status(
                    workflow_id=workflow_id,
                    status="failed",
                    result=None,
                    error=str(e),
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc).isoformat()
                )
    def run():
        loop.run_until_complete(process_events())
    thread = threading.Thread(target=run, daemon=True)
    thread.start()

# Example: background event-driven agent trigger processor (for demo)
async def agent_event_listener():
    orchestrator = setup_agents()
    async for event in orchestrator.receive_events(topic=AGENT_WORKFLOW_TRIGGER_TOPIC):
        workflow_id = event.get("workflowId")
        payload = event.get("payload", {})
        result = orchestrator.create_workflow(event.get("agentType"), payload)
        if hasattr(result, 'dict'):
            result = result.dict()
        elif hasattr(result, 'model_dump'):
            result = result.model_dump()
        if not isinstance(result, dict):
            logger.warning(f"Result for workflow {workflow_id} is not a dict, got {type(result)}. Setting result to None.")
            result = None
        set_workflow_status(
            workflow_id=workflow_id,
            status="completed",
            result=result,
            completed_at=datetime.now(timezone.utc).isoformat()
        )
