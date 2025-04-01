"""
Main module for FusionAiAutoCoder.
Provides core functionality for generating, optimizing and analyzing code.
"""

from typing import Dict, Any, List, Awaitable
import os
import logging
import asyncio

from src.config.config_multi_agents import setup_agents
from src.utils import setup_logging
from src.integration.azure_foundry import AzureAIFoundry

# Setup logging
logger: logging.Logger = setup_logging()


def hybrid_workflow(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a hybrid workflow combining local and cloud processing."""
    # Initialize Azure AI Foundry client
    azure_foundry: AzureAIFoundry = AzureAIFoundry()
    use_cloud: bool = os.environ.get("USE_CLOUD", "true").lower() == "true"

    # Initialize the agent orchestrator for local processing
    orchestrator = setup_agents()

    try:
        result: Dict[str, Any] = {}

        if use_cloud and task_data.get("complexity", "medium") == "high":
            try:
                cloud_result: Dict[str, Any] = await _process_cloud_task(
                    azure_foundry, task_type, task_data
                )
                if "error" not in cloud_result:
                    result = cloud_result
                else:
                    result = orchestrator.create_workflow(task_type, task_data)
            except Exception as cloud_error:
                logger.error(f"Error in cloud processing: {str(cloud_error)}")
                logger.warning("Falling back to local agent processing")
                result = orchestrator.create_workflow(task_type, task_data)
        else:
            result = orchestrator.create_workflow(task_type, task_data)

        return result
    except Exception as e:
        logger.error(f"Error in hybrid workflow: {str(e)}")
        return {"error": str(e)}


async def batch_process(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process multiple tasks in parallel."""
    results: List[Dict[str, Any]] = []
    tasks_futures: List[Awaitable[Dict[str, Any]]] = [
        hybrid_workflow(task["type"], task["data"]) for task in tasks
    ]

    completed_tasks: List[Dict[str, Any]] = await asyncio.gather(
        *tasks_futures, return_exceptions=True
    )

    for task_result in completed_tasks:
        if isinstance(task_result, Exception):
            results.append({"error": str(task_result)})
        else:
            results.append(task_result)

    return results


def run_workflow(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """Synchronous wrapper for hybrid_workflow."""
    return asyncio.run(hybrid_workflow(task_type, task_data))


def run_batch_process(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Synchronous wrapper for batch_process."""
    return asyncio.run(batch_process(tasks))


async def _process_cloud_task(
    azure_foundry: AzureAIFoundry, task_type: str, task_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Process a task using Azure AI Foundry."""
    if task_type == "code_generation":
        return await azure_foundry.process_code_generation(
            prompt=task_data.get("prompt", ""),
            options={
                "language": task_data.get("language", "python"),
                "temperature": task_data.get("temperature", 0.7),
                "max_tokens": task_data.get("max_tokens", 1000),
            },
        )
    elif task_type == "code_optimization":
        return await azure_foundry.process_code_optimization(
            code=task_data.get("code", ""),
            options={
                "target": task_data.get("target", "performance"),
                "language": task_data.get("language", "python"),
            },
        )
    else:
        raise ValueError(f"Unsupported task type: {task_type}")


if __name__ == "__main__":
    # Example usage
    result: Dict[str, Any] = run_workflow(
        task_type="code_generation",
        task_data={
            "prompt": "Create a function to validate email addresses",
            "language": "python",
            "complexity": "medium",
        },
    )
    print(result)
