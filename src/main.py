# Added hybrid workflow integration for Azure AI Foundry
from azure.identity import DefaultAzureCredential
from azure.ai.foundry import FoundryClient

# Initialize Foundry client
credential = DefaultAzureCredential()
foundry_client = FoundryClient(credential=credential)

def hybrid_workflow(task_type, task_data):
    if task_type == "language_understanding":
        return foundry_client.language_understanding.process(task_data)
    elif task_type == "image_processing":
        return foundry_client.image_processing.analyze(task_data)
    else:
        raise ValueError("Unsupported task type")