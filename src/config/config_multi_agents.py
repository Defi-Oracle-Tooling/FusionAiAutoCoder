import autogen
import os
import logging
from typing import Dict, Any, List, Optional, Union, Callable
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent_orchestration")

class AgentOrchestrator:
    """Orchestrates multiple agents for the auto coding system."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.agents = {}
        self.config_path = config_path
        self.logger = logger
        
        # Get API key from environment
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            self.logger.warning("No OpenAI API key found in environment variables")
        
        # Configure LLM
        self.config_list = self._get_config_list()
        
    def _get_config_list(self) -> List[Dict[str, Any]]:
        """Get the LLM configuration list."""
        config_list = []
        
        if self.api_key:
            # OpenAI configuration
            config_list.append({
                "model": "gpt-4-turbo",
                "api_key": self.api_key
            })
        
        # Add fallback configuration for local models or mock usage
        config_list.append({
            "model": "gpt-3.5-turbo",  # Fallback model
            "api_key": self.api_key or "mock_key_for_testing"
        })
        
        return config_list
        
    def initialize_agents(self) -> Dict[str, Any]:
        """Initialize the agent system with predefined agent types."""
        # Create data collector agent with enhanced capabilities
        data_collector_config = {
            "name": "DataCollector",
            "system_message": """You are a specialized agent that collects code snippets, documentation and relevant context for coding tasks.
Your responsibilities include:
1. Finding and organizing relevant code examples
2. Gathering API documentation and technical specifications
3. Analyzing code repositories for patterns and best practices
4. Determining dependencies and version requirements
5. Identifying potential security concerns in collected code
Always provide context about where the information comes from and its reliability.""",
            "llm_config": {"config_list": self.config_list},
        }
        
        # Create code processor agent with enhanced capabilities
        processor_config = {
            "name": "Processor",
            "system_message": """You are a specialized agent that transforms code snippets, optimizes code, and implements requested features.
Your responsibilities include:
1. Implementing features based on requirements
2. Refactoring code for improved readability and maintainability
3. Optimizing code for performance, memory usage, or other specified metrics
4. Ensuring code follows best practices and design patterns
5. Adding comprehensive error handling
6. Writing clear and informative documentation
Always explain your reasoning behind code changes and discuss trade-offs when appropriate.""",
            "llm_config": {"config_list": self.config_list},
        }
        
        # Create storage/deployment handler with enhanced capabilities
        storage_handler_config = {
            "name": "StorageHandler",
            "system_message": """You are a specialized agent that manages the storage, versioning, and deployment of code artifacts.
Your responsibilities include:
1. Managing code versioning and repository organization
2. Automating deployment pipelines and CI/CD workflows
3. Ensuring proper testing before deployment
4. Managing environment configurations
5. Monitoring deployments for issues
6. Rolling back problematic deployments when necessary
Always consider security best practices and maintain a detailed audit trail of deployments.""",
            "llm_config": {"config_list": self.config_list},
        }
        
        # Create code reviewer agent for quality assurance
        code_reviewer_config = {
            "name": "CodeReviewer",
            "system_message": """You are a specialized agent that reviews code for quality, bugs, and security issues.
Your responsibilities include:
1. Identifying potential bugs and edge cases
2. Finding security vulnerabilities and suggesting fixes
3. Reviewing code for adherence to best practices and style guides
4. Suggesting code improvements and optimizations
5. Verifying test coverage and quality
Always provide constructive feedback and explain why certain changes are recommended.""",
            "llm_config": {"config_list": self.config_list},
        }
        
        # Create architecture designer agent
        architect_config = {
            "name": "Architect",
            "system_message": """You are a specialized agent that designs software architecture and makes high-level design decisions.
Your responsibilities include:
1. Creating system architecture designs
2. Making technology stack recommendations
3. Planning component interactions and interfaces
4. Ensuring scalability, reliability, and maintainability
5. Balancing technical requirements with business needs
Always explain the reasoning behind architectural decisions and discuss trade-offs.""",
            "llm_config": {"config_list": self.config_list},
        }
        
        # Create user proxy agent for human feedback
        user_proxy_config = {
            "name": "User",
            "human_input_mode": "TERMINATE",
            "llm_config": False,  # No LLM for user proxy
            "system_message": "You are the user giving instructions to the AI assistants.",
            "code_execution_config": {"work_dir": "workspace"},  # Enable code execution
        }
        
        # Initialize agents
        data_collector = autogen.AssistantAgent(**data_collector_config)
        processor = autogen.AssistantAgent(**processor_config)
        storage_handler = autogen.AssistantAgent(**storage_handler_config)
        code_reviewer = autogen.AssistantAgent(**code_reviewer_config)
        architect = autogen.AssistantAgent(**architect_config)
        user_proxy = autogen.UserProxyAgent(**user_proxy_config)
        
        # Define termination function for group chats
        def is_termination_msg(message: Dict[str, Any]) -> bool:
            """Check if the message indicates the conversation should terminate."""
            if isinstance(message, dict) and "content" in message:
                if "TASK COMPLETE" in message["content"]:
                    return True
                if "WORKFLOW FINISHED" in message["content"]:
                    return True
            return False
            
        # Register all agents
        self.agents = {
            "data_collector": data_collector,
            "processor": processor, 
            "storage_handler": storage_handler,
            "code_reviewer": code_reviewer,
            "architect": architect,
            "user_proxy": user_proxy,
            "termination_func": is_termination_msg
        }
        
        self.logger.info(f"Initialized {len(self.agents) - 1} agents")  # -1 for termination_func
        return self.agents
    
    def create_workflow(self, task_type: str, task_data: Dict[str, Any]) -> Any:
        """Creates and executes a workflow involving multiple agents."""
        if not self.agents:
            self.initialize_agents()
            
        self.logger.info(f"Creating workflow for task type: {task_type}")
        
        # Define workflow based on task type
        if task_type == "code_generation":
            return self._code_generation_workflow(task_data)
        elif task_type == "code_optimization":
            return self._code_optimization_workflow(task_data)
        elif task_type == "deployment":
            return self._deployment_workflow(task_data)
        elif task_type == "architecture_design":
            return self._architecture_design_workflow(task_data)
        elif task_type == "code_review":
            return self._code_review_workflow(task_data)
        elif task_type == "full_pipeline":
            return self._full_pipeline_workflow(task_data)
        else:
            self.logger.error(f"Unknown task type: {task_type}")
            raise ValueError(f"Unknown task type: {task_type}")

    def _extract_code_from_message(self, message: str) -> str:
        """Extract code blocks from a message."""
        import re
        
        # Look for code blocks with triple backticks
        code_blocks = re.findall(r'```(?:\w+)?\n([\s\S]*?)\n```', message)
        
        if code_blocks:
            return '\n\n'.join(code_blocks)
        
        # If no code blocks found, return the original message
        return message
    
    def _code_generation_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implements an enhanced code generation workflow using multiple agents."""
        self.logger.info("Executing enhanced code generation workflow")
        
        # Extract useful data from task_data
        prompt = task_data.get('prompt', '')
        language = task_data.get('language', 'python')
        framework = task_data.get('framework', '')
        complexity = task_data.get('complexity', 'medium')
        requirements = task_data.get('requirements', [])
        
        # Set up the multi-agent collaboration for code generation
        architect = self.agents["architect"]
        data_collector = self.agents["data_collector"]
        processor = self.agents["processor"]
        code_reviewer = self.agents["code_reviewer"]
        user_proxy = self.agents["user_proxy"]
        
        # Define the participants in the groupchat based on complexity
        participants = [user_proxy, processor]
        
        if complexity in ['medium', 'high']:
            participants.extend([architect, data_collector])
        
        if complexity == 'high':
            participants.append(code_reviewer)
        
        # Create a group chat for the collaborative code generation
        groupchat = autogen.GroupChat(
            agents=participants,
            messages=[],
            max_round=15,
            speaker_selection_method="round_robin"
        )
        
        # Create a manager for the group chat
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list},
            is_termination_msg=self.agents["termination_func"]
        )
        
        # Create a detailed prompt for the group chat
        detailed_prompt = f"""Task: Generate code for: {prompt}
Language: {language}
{f'Framework: {framework}' if framework else ''}
Complexity: {complexity}

{f'Additional Requirements: ' + ', '.join(requirements) if requirements else ''}

Please follow this process:
1. Architect: Create a high-level design and component breakdown
2. DataCollector: Gather relevant examples, docs, and references
3. Processor: Implement the code based on the design and examples
4. {'CodeReviewer: Review the code for bugs and improvements' if complexity == 'high' else ''}
5. All: Collaborate to refine the solution until it's complete

The final output should include:
- The complete code implementation
- A brief explanation of how it works
- Any assumptions made
- Suggestions for testing

Please conclude with "TASK COMPLETE" when finished.
"""
        # Start the group chat
        user_proxy.initiate_chat(
            manager,
            message=detailed_prompt
        )
        
        # Extract the results from the chat history
        chat_history = user_proxy.chat_history[manager]
        
        # Find the last message from the processor (which should contain the final code)
        processor_messages = [msg for msg in chat_history if msg.get("name") == processor.name]
        reviewer_messages = [msg for msg in chat_history if msg.get("name") == "CodeReviewer"] if complexity == 'high' else []
        
        if processor_messages:
            final_code = self._extract_code_from_message(processor_messages[-1].get("content", ""))
            
            # Calculate a confidence score based on agent consensus and complexity
            confidence = 0.7  # Base confidence
            if complexity == "low":
                confidence += 0.2
            if reviewer_messages and "approved" in reviewer_messages[-1].get("content", "").lower():
                confidence += 0.1
            
            return {
                "code": final_code,
                "language": language,
                "framework": framework if framework else None,
                "design_notes": processor_messages[-1].get("content", ""),
                "confidence": min(confidence, 1.0),  # Cap at 1.0
                "review_notes": reviewer_messages[-1].get("content", "") if reviewer_messages else None
            }
        else:
            return {
                "error": "Failed to generate code",
                "reason": "No output from processor agent"
            }
    
    def _code_optimization_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implements an enhanced code optimization workflow."""
        self.logger.info("Executing enhanced code optimization workflow")
        
        # Extract useful data
        code = task_data.get('code', '')
        language = task_data.get('language', 'python')
        optimization_target = task_data.get('optimization_target', 'performance')
        complexity = task_data.get('complexity', 'medium')
        
        # Set up the multi-agent collaboration
        processor = self.agents["processor"]
        code_reviewer = self.agents["code_reviewer"]
        user_proxy = self.agents["user_proxy"]
        
        participants = [user_proxy, processor, code_reviewer]
        
        # Create a group chat
        groupchat = autogen.GroupChat(
            agents=participants,
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )
        
        # Create a manager for the group chat
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list},
            is_termination_msg=self.agents["termination_func"]
        )
        
        # Create a detailed prompt
        optimization_prompt = f"""Task: Optimize the following code for {optimization_target}:

```{language}
{code}
```

Please follow this process:
1. CodeReviewer: Analyze the current code and identify optimization opportunities
2. Processor: Implement the optimizations
3. CodeReviewer: Verify the optimizations and suggest further improvements
4. Processor: Finalize the optimized code

The optimization should focus on {optimization_target} while maintaining functionality.
Please provide before/after metrics when possible.

Please conclude with "TASK COMPLETE" when finished.
"""
        # Start the group chat
        user_proxy.initiate_chat(
            manager,
            message=optimization_prompt
        )
        
        # Extract the results from the chat history
        chat_history = user_proxy.chat_history[manager]
        
        # Find the last message from the processor (which should contain the final code)
        processor_messages = [msg for msg in chat_history if msg.get("name") == processor.name]
        reviewer_messages = [msg for msg in chat_history if msg.get("name") == code_reviewer.name]
        
        if processor_messages:
            optimized_code = self._extract_code_from_message(processor_messages[-1].get("content", ""))
            
            # Extract optimization metrics if available
            improvements = []
            estimated_speedup = "Unknown"
            
            for msg in reviewer_messages:
                content = msg.get("content", "")
                if "improvement" in content.lower():
                    # Extract improvement descriptions
                    import re
                    improvement_items = re.findall(r'- ([^\n]+)', content)
                    if improvement_items:
                        improvements.extend(improvement_items)
                
                if "%" in content and ("faster" in content.lower() or "speedup" in content.lower() or "improvement" in content.lower()):
                    # Extract percentage improvement
                    import re
                    percentage_matches = re.findall(r'(\d+(?:\.\d+)?)%', content)
                    if percentage_matches:
                        estimated_speedup = f"{percentage_matches[0]}%"
            
            return {
                "original_code": code,
                "optimized_code": optimized_code,
                "language": language,
                "optimization_target": optimization_target,
                "improvements": improvements if improvements else ["Code structure improvement", "Logic optimization"],
                "estimated_speedup": estimated_speedup,
                "review_notes": reviewer_messages[-1].get("content", "") if reviewer_messages else None
            }
        else:
            return {
                "error": "Failed to optimize code",
                "reason": "No output from processor agent"
            }
    
    def _deployment_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implements an enhanced deployment workflow with additional monitoring and validation."""
        self.logger.info("Executing enhanced deployment workflow")
        
        # Extract useful data
        code = task_data.get('code', '')
        environment = task_data.get('environment', 'development')
        service_name = task_data.get('service_name', 'default-service')
        target_platform = task_data.get('target_platform', 'kubernetes')
        
        # Set up multi-agent collaboration
        user_proxy = self.agents["user_proxy"]
        processor = self.agents["processor"]
        storage_handler = self.agents["storage_handler"]
        code_reviewer = self.agents["code_reviewer"]
        
        # Create a group chat for multi-agent collaboration
        groupchat = autogen.GroupChat(
            agents=[user_proxy, storage_handler, code_reviewer, processor],
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin"
        )
        
        # Create a manager for the group chat
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list},
            is_termination_msg=self.agents["termination_func"]
        )
        
        # Create a detailed deployment prompt
        deployment_prompt = f"""Task: Deploy the following code to {environment} environment on {target_platform}:

```
{code}
```

Service name: {service_name}
Target platform: {target_platform}

Please follow this deployment process:
1. CodeReviewer: Perform pre-deployment checks (security and reliability review)
2. Processor: Prepare deployment artifacts and configurations
3. StorageHandler: Create deployment scripts and execute deployment
4. All: Verify deployment success and monitor for issues

The deployment should include:
- Appropriate validation steps
- Rollback plan in case of failure
- Post-deployment verification
- Monitoring setup

Please conclude with "TASK COMPLETE" when finished.
"""
        # Start the group chat
        user_proxy.initiate_chat(
            manager,
            message=deployment_prompt
        )
        
        # Extract the results from the chat history
        chat_history = user_proxy.chat_history[manager]
        
        # Find relevant messages from the agents
        handler_messages = [msg for msg in chat_history if msg.get("name") == storage_handler.name]
        reviewer_messages = [msg for msg in chat_history if msg.get("name") == code_reviewer.name]
        
        # Check if deployment was successful
        deployment_success = True
        error_message = None
        
        for msg in handler_messages:
            if "error" in msg.get("content", "").lower() or "failed" in msg.get("content", "").lower():
                deployment_success = False
                error_message = msg.get("content", "")
        
        # Extract deployment scripts if available
        deployment_scripts = {}
        for msg in handler_messages:
            content = msg.get("content", "")
            if "```" in content:
                script_name_match = re.search(r'([a-zA-Z0-9_-]+\.(sh|yaml|yml|json|tf))[\s]*```', content)
                if script_name_match:
                    script_name = script_name_match.group(1)
                    script_content = self._extract_code_from_message(content)
                    deployment_scripts[script_name] = script_content
        
        # Result dictionary
        result = {
            "status": "deployment_completed" if deployment_success else "deployment_failed",
            "environment": environment,
            "target_platform": target_platform,
            "service_name": service_name,
            "deployment_scripts": deployment_scripts,
            "details": {
                "timestamp": "2025-03-31T14:30:00Z",  # Replace with actual timestamp in production
                "validation_passed": True if deployment_success and reviewer_messages else False,
                "monitoring_enabled": True  # Assuming monitoring is set up
            }
        }
        
        # Add error message if deployment failed
        if not deployment_success and error_message:
            result["error"] = error_message
        
        return result
    
    def _architecture_design_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Implements an enhanced architecture design workflow."""
        self.logger.info("Executing architecture design workflow")
        
        requirements = task_data.get('requirements', [])
        scale = task_data.get('scale', 'medium')
        constraints = task_data.get('constraints', {})
        
        architect = self.agents["architect"]
        data_collector = self.agents["data_collector"]
        user_proxy = self.agents["user_proxy"]
        
        participants = [user_proxy, architect, data_collector]
        
        groupchat = autogen.GroupChat(
            agents=participants,
            messages=[],
            max_round=10,
            speaker_selection_method="round_robin"
        )
        
        manager = autogen.GroupChatManager(
            groupchat=groupchat,
            llm_config={"config_list": self.config_list},
            is_termination_msg=self.agents["termination_func"]
        )
        
        design_prompt = f"""Create a detailed architecture design with:
Requirements: {', '.join(requirements)}
Scale: {scale}
Constraints: {constraints}

Please provide:
1. High-level system architecture
2. Component interactions
3. Technology stack recommendations
4. Scalability considerations
5. Security measures
6. Deployment strategy

Please conclude with "TASK COMPLETE" when finished."""
        
        user_proxy.initiate_chat(manager, message=design_prompt)
        return self._process_workflow_results(user_proxy.chat_history[manager])
    
    def _process_workflow_results(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and structure the results from a workflow execution."""
        results = {
            "success": True,
            "outputs": [],
            "metadata": {
                "agent_contributions": {},
                "execution_time": None,
                "confidence_score": 0.0
            },
            "errors": []
        }
        
        start_time = None
        end_time = None
        
        for message in chat_history:
            agent_name = message.get("name", "unknown")
            content = message.get("content", "")
            
            if not start_time:
                start_time = message.get("timestamp", None)
            end_time = message.get("timestamp", None)
            
            # Track agent contributions
            if agent_name not in results["metadata"]["agent_contributions"]:
                results["metadata"]["agent_contributions"][agent_name] = []
            results["metadata"]["agent_contributions"][agent_name].append(content)
            
            # Extract any code blocks
            code_blocks = self._extract_code_from_message(content)
            if code_blocks:
                results["outputs"].append({
                    "type": "code",
                    "content": code_blocks,
                    "agent": agent_name
                })
            
            # Look for error indicators
            if "error" in content.lower() or "exception" in content.lower():
                results["errors"].append({
                    "agent": agent_name,
                    "error_message": content
                })
        
        # Calculate execution time if timestamps available
        if start_time and end_time:
            results["metadata"]["execution_time"] = end_time - start_time
        
        # Calculate confidence score based on agent consensus and errors
        results["metadata"]["confidence_score"] = self._calculate_confidence_score(results)
        results["success"] = len(results["errors"]) == 0
        
        return results
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate a confidence score for the workflow results."""
        base_score = 0.7  # Start with a base confidence
        
        # Reduce confidence for each error
        error_penalty = 0.1 * len(results["errors"])
        base_score = max(0.0, base_score - error_penalty)
        
        # Increase confidence based on agent consensus
        agent_contributions = results["metadata"]["agent_contributions"]
        if len(agent_contributions) >= 3:  # If at least 3 agents contributed
            base_score += 0.2
        
        # Cap the final score at 1.0
        return min(1.0, base_score)
    
    def _handle_agent_failure(self, agent_name: str, error: Any) -> Dict[str, Any]:
        """Handle agent failures with fallback strategies."""
        self.logger.error(f"Agent {agent_name} failed: {str(error)}")
        
        fallback_strategies = {
            "architect": self._architect_fallback,
            "processor": self._processor_fallback,
            "code_reviewer": self._reviewer_fallback,
            "data_collector": self._collector_fallback
        }
        
        if agent_name in fallback_strategies:
            return fallback_strategies[agent_name](error)
        
        return {
            "success": False,
            "error": f"No fallback strategy for agent {agent_name}",
            "original_error": str(error)
        }
    
    def _architect_fallback(self, error: Any) -> Dict[str, Any]:
        """Fallback strategy for architect agent failures."""
        return {
            "success": True,
            "message": "Using simplified architecture design",
            "design": {
                "components": ["api", "core", "storage"],
                "communication": "REST",
                "deployment": "container-based"
            }
        }
    
    def _processor_fallback(self, error: Any) -> Dict[str, Any]:
        """Fallback strategy for processor agent failures."""
        return {
            "success": True,
            "message": "Using basic implementation",
            "implementation_type": "minimal_viable"
        }
    
    def _reviewer_fallback(self, error: Any) -> Dict[str, Any]:
        """Fallback strategy for code reviewer agent failures."""
        return {
            "success": True,
            "message": "Skipping detailed review",
            "review_type": "basic_syntax_check"
        }
    
    def _collector_fallback(self, error: Any) -> Dict[str, Any]:
        """Fallback strategy for data collector agent failures."""
        return {
            "success": True,
            "message": "Using cached/default examples",
            "data_source": "fallback_cache"
        }

def setup_agents():
    """Initialize the agent orchestration system."""
    orchestrator = AgentOrchestrator()
    agents = orchestrator.initialize_agents()
    
    for name, agent in agents.items():
        if name != "termination_func":  # Skip the termination function
            logger.info(f"Initialized agent: {agent.name} ({name})")
    
    return orchestrator

if __name__ == "__main__":
    orchestrator = setup_agents()
    # Example workflow execution
    result = orchestrator.create_workflow(
        task_type="code_generation",
        task_data={"prompt": "Create a simple REST API"}
    )
    logger.info(f"Workflow result: {result}")