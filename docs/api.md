# FusionAiAutoCoder API Documentation

## Overview

FusionAiAutoCoder provides a RESTful API for AI-assisted code generation and optimization. The API supports both synchronous and asynchronous operations, with background task processing for resource-intensive operations.

## Base URL

```
http://localhost:8080
```

For production deployments, use your configured domain and HTTPS.

## Authentication

Authentication is currently handled via API keys passed in the `Authorization` header:

```
Authorization: Bearer your-api-key
```

## Endpoints

### Health Check

```
GET /health
```

Returns the health status and version information of the API.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 3600.5
}
```

### Create Task

```
POST /api/task
```

Creates a new task for processing in the background.

**Request Body:**

```json
{
  "task_type": "code_generation",
  "task_data": {
    "prompt": "Create a sorting function",
    "language": "python",
    "complexity": "low",
    "use_gpu": false
  }
}
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "result": null
}
```

### Get Task Status

```
GET /api/task/{task_id}
```

Retrieves the status and result of a previously submitted task.

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "code": "def sort_array(arr):\n    return sorted(arr)",
    "language": "python",
    "confidence": 0.95,
    "metadata": {
      "execution_time": 1.5,
      "gpu_used": false,
      "version_info": {
        "system": "Linux",
        "python": "3.9.5",
        "fusion_ai": "1.0.0"
      }
    }
  }
}
```

### Generate Code

```
POST /api/generate
```

Generates code based on a natural language prompt.

**Request Body:**

```json
{
  "prompt": "Create a function to validate email addresses",
  "language": "python",
  "complexity": "low",
  "use_gpu": false,
  "framework": null
}
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "result": null
}
```

### Optimize Code

```
POST /api/optimize
```

Optimizes existing code for performance, memory usage, or readability.

**Request Body:**

```json
{
  "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
  "optimization_target": "performance",
  "language": "python"
}
```

**Response:**

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "result": null
}
```

### Batch Processing

```
POST /api/batch
```

Processes multiple tasks in a single batch request.

**Request Body:**

```json
{
  "tasks": [
    {
      "task_type": "code_generation",
      "task_data": {
        "prompt": "Create a sorting function",
        "language": "python"
      }
    },
    {
      "task_type": "code_optimization",
      "task_data": {
        "code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
        "optimization_target": "performance"
      }
    }
  ]
}
```

**Response:**

```json
[
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "result": {
      "code": "def sort_array(arr):\n    return sorted(arr)",
      "language": "python",
      "confidence": 0.95
    }
  },
  {
    "task_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "completed",
    "result": {
      "optimized_code": "def factorial(n):\n    result = 1\n    for i in range(1, n+1):\n        result *= i\n    return result",
      "language": "python",
      "improvements": ["Algorithm optimization", "Memory usage reduction"],
      "estimated_speedup": "75%"
    }
  }
]
```

## Error Handling

The API returns standard HTTP status codes:

- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Resource not found
- `500` - Server error

Error responses include a `detail` field with more information:

```json
{
  "detail": "Task not found"
}
```

## Rate Limiting

API requests are limited to 100 requests per minute per API key. Exceeding this limit will result in a `429 Too Many Requests` response.

## Azure AI Foundry Integration

The API automatically uses Azure AI Foundry services when appropriate, based on task complexity and resource availability. This behavior can be controlled via the `use_gpu` parameter in request bodies.