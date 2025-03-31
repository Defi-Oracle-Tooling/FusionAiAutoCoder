"""
Main module for FusionAiAutoCoder.
Provides core functionality for generating, optimizing and analyzing code.
"""
import os
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union

from src.config.config_multi_agents import setup_agents
from src.utils import setup_logging, is_gpu_available, get_version_info
from src.integration.azure_foundry import AzureAIFoundry

# Setup logging
logger = setup_logging()

async def hybrid_workflow(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the hybrid workflow that combines local and cloud processing.
    
    Args:
        task_type: Type of task to perform (code_generation, code_optimization, language_understanding)
        task_data: Dictionary containing task-specific data
        
    Returns:
        Dictionary containing the result of the workflow
    """
    start_time = time.time()
    logger.info(f"Starting hybrid workflow for task type: {task_type}")
    
    # Check if GPU acceleration is available and requested
    use_gpu = task_data.get('use_gpu', False) and is_gpu_available()
    if use_gpu:
        logger.info("GPU acceleration enabled")
    else:
        logger.info("Using CPU for processing")
    
    # Check for cloud processing preference
    use_cloud = task_data.get('use_cloud', True)
    logger.info(f"Cloud processing: {'enabled' if use_cloud else 'disabled'}")
    
    # Initialize the Azure AI Foundry client
    azure_foundry = AzureAIFoundry()
    
    # Initialize the agent orchestrator for local processing
    orchestrator = setup_agents()
    
    try:
        result = {}
        
        # Determine whether to use cloud or local processing based on task requirements
        if use_cloud and task_data.get('complexity', 'medium') == 'high':
            # For high complexity tasks, try cloud first, then fall back to local
            logger.info("Using cloud-first processing strategy for high complexity task")
            try:
                if task_type == "code_generation":
                    cloud_result = await azure_foundry.process_code_generation(
                        prompt=task_data.get('prompt', ''),
                        options={
                            'language': task_data.get('language', 'python'),
                            'temperature': task_data.get('temperature', 0.7),
                            'max_tokens': task_data.get('max_tokens', 1000)
                        }
                    )
                    if 'error' not in cloud_result:
                        logger.info("Successfully processed task in the cloud")
                        result = cloud_result
                    else:
                        logger.warning("Cloud processing failed, falling back to local agents")
                        result = orchestrator.create_workflow(task_type, task_data)
                elif task_type == "code_optimization":
                    cloud_result = await azure_foundry.process_code_optimization(
                        code=task_data.get('code', ''),
                        options={
                            'language': task_data.get('language', 'python'),
                            'optimization_target': task_data.get('optimization_target', 'performance')
                        }
                    )
                    if 'error' not in cloud_result:
                        logger.info("Successfully processed optimization in the cloud")
                        result = cloud_result
                    else:
                        logger.warning("Cloud optimization failed, falling back to local agents")
                        result = orchestrator.create_workflow(task_type, task_data)
                else:
                    # For other task types, use local processing
                    logger.info(f"No cloud implementation for task type {task_type}, using local processing")
                    result = orchestrator.create_workflow(task_type, task_data)
            except Exception as cloud_error:
                logger.error(f"Error in cloud processing: {str(cloud_error)}")
                logger.warning("Falling back to local agent processing")
                result = orchestrator.create_workflow(task_type, task_data)
        elif use_cloud and task_data.get('parallel_execution', False):
            # For tasks that can benefit from parallel execution
            logger.info("Using parallel execution strategy (cloud + local)")
            
            # Execute both cloud and local processing in parallel
            cloud_task = None
            if task_type == "code_generation":
                cloud_task = azure_foundry.process_code_generation(
                    prompt=task_data.get('prompt', ''),
                    options={
                        'language': task_data.get('language', 'python'),
                        'temperature': task_data.get('temperature', 0.7),
                        'max_tokens': task_data.get('max_tokens', 1000)
                    }
                )
            elif task_type == "code_optimization":
                cloud_task = azure_foundry.process_code_optimization(
                    code=task_data.get('code', ''),
                    options={
                        'language': task_data.get('language', 'python'),
                        'optimization_target': task_data.get('optimization_target', 'performance')
                    }
                )
            
            # Start local processing
            local_result = orchestrator.create_workflow(task_type, task_data)
            
            # If cloud processing is available for this task type
            if cloud_task:
                try:
                    cloud_result = await cloud_task
                    
                    # Compare results and choose the better one based on confidence or other metrics
                    if 'error' not in cloud_result and cloud_result.get('confidence', 0) > local_result.get('confidence', 0):
                        logger.info("Selected cloud result based on higher confidence")
                        result = cloud_result
                        # Add local result as alternative
                        result['alternative'] = local_result
                    else:
                        logger.info("Selected local result")
                        result = local_result
                        # Add cloud result as alternative if it was successful
                        if 'error' not in cloud_result:
                            result['alternative'] = cloud_result
                except Exception as cloud_error:
                    logger.error(f"Error in parallel cloud processing: {str(cloud_error)}")
                    result = local_result
            else:
                result = local_result
        else:
            # Default to local processing for simpler tasks or when cloud is disabled
            logger.info("Using local agent processing")
            result = orchestrator.create_workflow(task_type, task_data)
        
        # Add metadata to the result
        result['metadata'] = {
            'execution_time': time.time() - start_time,
            'gpu_used': use_gpu,
            'cloud_used': use_cloud,
            'version_info': get_version_info()
        }
        
        logger.info(f"Completed {task_type} workflow in {result['metadata']['execution_time']:.2f} seconds")
        return result
        
    except Exception as e:
        logger.error(f"Error in hybrid workflow: {str(e)}", exc_info=True)
        # Return error information
        return {
            'error': str(e),
            'task_type': task_type,
            'metadata': {
                'execution_time': time.time() - start_time,
                'success': False,
                'gpu_used': use_gpu,
                'cloud_used': use_cloud
            }
        }

async def batch_process(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple tasks in batch mode.
    
    Args:
        tasks: List of task dictionaries, each containing 'task_type' and 'task_data'
        
    Returns:
        List of results corresponding to each task
    """
    logger.info(f"Starting batch processing of {len(tasks)} tasks")
    results = []
    
    for i, task in enumerate(tasks):
        logger.info(f"Processing batch task {i+1}/{len(tasks)}")
        task_type = task.get('task_type')
        task_data = task.get('task_data', {})
        
        if not task_type:
            results.append({'error': 'Missing task_type in batch task'})
            continue
            
        result = await hybrid_workflow(task_type, task_data)
        results.append(result)
    
    logger.info(f"Completed batch processing of {len(tasks)} tasks")
    return results

def run_workflow(task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for the async hybrid_workflow function.
    
    Args:
        task_type: Type of task to perform
        task_data: Dictionary containing task-specific data
        
    Returns:
        Dictionary containing the result of the workflow
    """
    return asyncio.run(hybrid_workflow(task_type, task_data))

def run_batch_process(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Synchronous wrapper for the async batch_process function.
    
    Args:
        tasks: List of task dictionaries
        
    Returns:
        List of results corresponding to each task
    """
    return asyncio.run(batch_process(tasks))

if __name__ == "__main__":
    # Example usage
    result = run_workflow(
        task_type="code_generation",
        task_data={
            "prompt": "Create a function to validate email addresses",
            "language": "python",
            "complexity": "low"
        }
    )
    
    print("Generated code:")
    print(result.get('code', 'No code generated'))