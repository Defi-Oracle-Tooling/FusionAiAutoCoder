"""
Azure AI Foundry integration module for FusionAiAutoCoder.
Provides interfaces to connect with Azure AI services.
"""
import os
import logging
import json
import time
import hashlib
import pickle
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger("azure_integration")

# Authentication token cache file path
TOKEN_CACHE_PATH = os.environ.get("AZURE_FOUNDRY_TOKEN_CACHE", "cache/azure_token.cache")

class RequestCache:
    """Simple cache for Azure AI Foundry requests to reduce latency and costs."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600, persist_path: Optional[str] = None):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items to store in cache
            ttl: Time to live for cache entries in seconds (default: 1 hour)
            persist_path: Path to save cache to disk for persistence (default: None)
        """
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_order = []  # For LRU eviction
        self.persist_path = persist_path
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "expirations": 0,
            "insertions": 0
        }
        
        # Load cache from disk if path is provided
        if persist_path:
            self._load_from_disk()
        
        logger.info(f"Initialized request cache with max_size={max_size}, ttl={ttl}s")
    
    def _generate_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """Generate a unique cache key from the endpoint and payload."""
        payload_str = json.dumps(payload, sort_keys=True)
        key_material = f"{endpoint}:{payload_str}"
        return hashlib.md5(key_material.encode()).hexdigest()
    
    def get(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Try to get a response from the cache.
        
        Returns None if cache miss or entry expired.
        """
        key = self._generate_key(endpoint, payload)
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
            
        entry = self.cache[key]
        current_time = time.time()
        
        # Check if entry is still valid
        if current_time > entry["expires_at"]:
            # Remove expired entry
            del self.cache[key]
            self.access_order.remove(key)
            self.stats["expirations"] += 1
            self.stats["misses"] += 1
            return None
            
        # Update access order for LRU
        self.access_order.remove(key)
        self.access_order.append(key)
        
        self.stats["hits"] += 1
        logger.debug(f"Cache hit for {endpoint}")
        return entry["response"]
    
    def set(self, endpoint: str, payload: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Store a response in the cache."""
        key = self._generate_key(endpoint, payload)
        expires_at = time.time() + self.ttl
        
        # If cache is full, evict least recently used item
        if len(self.cache) >= self.max_size and key not in self.cache:
            lru_key = self.access_order.pop(0)
            del self.cache[lru_key]
            self.stats["evictions"] += 1
            logger.debug(f"Cache full, evicted least recently used entry")
        
        # Store new entry
        self.cache[key] = {
            "response": response,
            "expires_at": expires_at
        }
        
        self.stats["insertions"] += 1
        
        # Update access order
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        logger.debug(f"Cached response for {endpoint}")
        
        # Save cache to disk if path is provided
        if self.persist_path:
            self._save_to_disk()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = self.stats.copy()
        stats["size"] = len(self.cache)
        stats["max_size"] = self.max_size
        
        # Calculate hit rate
        total_requests = stats["hits"] + stats["misses"]
        stats["hit_rate"] = stats["hits"] / total_requests if total_requests > 0 else 0
        
        return stats
    
    def _save_to_disk(self) -> bool:
        """Save cache to disk for persistence between restarts."""
        if not self.persist_path:
            return False
            
        try:
            # Ensure directory exists
            cache_dir = os.path.dirname(self.persist_path)
            os.makedirs(cache_dir, exist_ok=True)
            
            # Create a serializable version of the cache
            serializable_cache = {
                "cache": self.cache,
                "access_order": self.access_order,
                "stats": self.stats,
                "timestamp": time.time()
            }
            
            # Save to disk
            with open(self.persist_path, 'wb') as f:
                pickle.dump(serializable_cache, f)
                
            logger.debug(f"Saved cache to {self.persist_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save cache to disk: {str(e)}")
            return False
    
    def _load_from_disk(self) -> bool:
        """Load cache from disk."""
        if not self.persist_path or not os.path.exists(self.persist_path):
            return False
            
        try:
            # Load from disk
            with open(self.persist_path, 'rb') as f:
                loaded_cache = pickle.load(f)
                
            # Restore cache data
            self.cache = loaded_cache["cache"]
            self.access_order = loaded_cache["access_order"]
            self.stats = loaded_cache["stats"]
            
            # Cleanup expired entries
            current_time = time.time()
            expired_keys = []
            
            for key, entry in self.cache.items():
                if current_time > entry["expires_at"]:
                    expired_keys.append(key)
            
            # Remove expired entries
            for key in expired_keys:
                del self.cache[key]
                self.access_order.remove(key)
                self.stats["expirations"] += 1
            
            logger.info(f"Loaded cache from {self.persist_path} with {len(self.cache)} valid entries")
            logger.debug(f"Removed {len(expired_keys)} expired entries during load")
            return True
        except Exception as e:
            logger.error(f"Failed to load cache from disk: {str(e)}")
            # Start with a fresh cache on error
            self.cache = {}
            self.access_order = []
            return False

class AzureAIFoundry:
    """Handles integration with Azure AI Foundry services."""
    
    def __init__(self):
        # Get configuration from environment
        self.tenant_id = os.environ.get("AZURE_TENANT_ID")
        self.client_id = os.environ.get("AZURE_CLIENT_ID")
        self.client_secret = os.environ.get("AZURE_CLIENT_SECRET")
        self.foundry_endpoint = os.environ.get("AZURE_FOUNDRY_ENDPOINT", "https://api.foundry.azure.com")
        
        # Determine if we should use mock or real implementation
        self.use_mock = os.environ.get("USE_MOCK_FOUNDRY", "true").lower() == "true"
        
        # Check if credentials are available
        self.is_configured = all([self.tenant_id, self.client_id, self.client_secret])
        if not self.is_configured and not self.use_mock:
            logger.warning("Azure AI Foundry integration not fully configured")
            logger.info("Falling back to mock implementation")
            self.use_mock = True
        
        # Initialize auth token
        self.auth_token = None
        self.token_expires_at = 0
        
        # Initialize request cache
        use_cache = os.environ.get("AZURE_FOUNDRY_USE_CACHE", "true").lower() == "true"
        self.cache_enabled = use_cache
        if use_cache:
            cache_size = int(os.environ.get("AZURE_FOUNDRY_CACHE_SIZE", "1000"))
            cache_ttl = int(os.environ.get("AZURE_FOUNDRY_CACHE_TTL", "3600"))
            self.request_cache = RequestCache(max_size=cache_size, ttl=cache_ttl)
            logger.info(f"Request caching enabled with size={cache_size}, ttl={cache_ttl}s")
        else:
            logger.info("Request caching disabled")
        
        if self.use_mock:
            logger.info("Using mock implementation for Azure AI Foundry")
        else:
            logger.info(f"Using real Azure AI Foundry implementation with endpoint: {self.foundry_endpoint}")
    
    async def authenticate(self) -> bool:
        """Authenticate with Azure services and get a token."""
        if self.use_mock:
            self.auth_token = "mock_token_for_development"
            self.token_expires_at = time.time() + 3600  # Token valid for 1 hour
            return True
            
        if not self.is_configured:
            logger.warning("Cannot authenticate: Azure credentials not configured")
            return False
            
        # Check if we have a valid token
        current_time = time.time()
        if self.auth_token and current_time < self.token_expires_at:
            return True
            
        try:
            # Real implementation using azure-identity
            from azure.identity import ClientSecretCredential
            
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # Get a token from Azure AD
            token_response = credential.get_token("https://cognitiveservices.azure.com/.default")
            self.auth_token = token_response.token
            self.token_expires_at = time.time() + token_response.expires_on
            
            logger.info("Successfully authenticated with Azure AD")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return False
    
    async def process_code_generation(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Use Azure AI Foundry for code generation."""
        # Check cache if enabled
        endpoint = f"{self.foundry_endpoint}/v1/code/generate"
        payload = {
            "prompt": prompt,
            "language": options.get("language", "python"),
            "temperature": options.get("temperature", 0.7),
            "max_tokens": options.get("max_tokens", 1000),
            "options": options
        }
        
        # Try to get from cache
        if self.cache_enabled and not self.use_mock:
            cached_response = self.request_cache.get(endpoint, payload)
            if cached_response:
                logger.info("Retrieved code generation result from cache")
                return cached_response
        
        if not await self.authenticate():
            logger.warning("Using mock response due to authentication failure")
            return self._mock_code_generation(prompt, options)
        
        if self.use_mock:
            return self._mock_code_generation(prompt, options)
            
        try:
            logger.info("Calling Azure AI Foundry for code generation")
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            # Make the API call
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Cache the successful response
                if self.cache_enabled:
                    self.request_cache.set(endpoint, payload, result)
                    
                return result
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return {"error": f"API call failed: {response.status_code}", "fallback": self._mock_code_generation(prompt, options)}
                
        except Exception as e:
            logger.error(f"Error calling Azure AI Foundry: {str(e)}")
            return {"error": str(e), "fallback": self._mock_code_generation(prompt, options)}
    
    async def process_code_optimization(self, code: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Use Azure AI Foundry for code optimization."""
        # Check cache if enabled
        endpoint = f"{self.foundry_endpoint}/v1/code/optimize"
        payload = {
            "code": code,
            "language": options.get("language", "python"),
            "optimization_target": options.get("optimization_target", "performance"),
            "options": options
        }
        
        # Try to get from cache
        if self.cache_enabled and not self.use_mock:
            cached_response = self.request_cache.get(endpoint, payload)
            if cached_response:
                logger.info("Retrieved code optimization result from cache")
                return cached_response
        
        if not await self.authenticate():
            logger.warning("Using mock response due to authentication failure")
            return self._mock_code_optimization(code, options)
        
        if self.use_mock:
            return self._mock_code_optimization(code, options)
            
        try:
            logger.info("Calling Azure AI Foundry for code optimization")
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            # Make the API call
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Cache the successful response
                if self.cache_enabled:
                    self.request_cache.set(endpoint, payload, result)
                    
                return result
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return {"error": f"API call failed: {response.status_code}", "fallback": self._mock_code_optimization(code, options)}
                
        except Exception as e:
            logger.error(f"Error calling Azure AI Foundry: {str(e)}")
            return {"error": str(e), "fallback": self._mock_code_optimization(code, options)}
    
    def get_cache_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about the request cache performance.
        
        Returns:
            Dict containing cache statistics and performance metrics
        """
        if not self.cache_enabled:
            return {
                "enabled": False,
                "message": "Caching is disabled for Azure AI Foundry"
            }
            
        stats = self.request_cache.get_stats()
        
        # Add some derived metrics
        total_requests = stats["hits"] + stats["misses"]
        if total_requests > 0:
            stats["efficiency"] = {
                "hit_rate_percentage": round(stats["hit_rate"] * 100, 2),
                "cache_utilization": round(stats["size"] / stats["max_size"] * 100, 2) if stats["max_size"] > 0 else 0,
                "eviction_rate": round(stats["evictions"] / stats["insertions"] * 100, 2) if stats["insertions"] > 0 else 0
            }
            
            # Calculate estimated cost savings (assuming each API call costs $0.002)
            cost_per_call = 0.002  # Placeholder value
            stats["estimated_savings"] = {
                "api_calls_saved": stats["hits"],
                "cost_saved": round(stats["hits"] * cost_per_call, 2)
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "cache_config": {
                "max_size": self.request_cache.max_size,
                "ttl_seconds": self.request_cache.ttl,
                "persistence_enabled": self.request_cache.persist_path is not None
            }
        }
    
    def _mock_code_generation(self, prompt: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock response for code generation."""
        language = options.get("language", "python")
        
        if language == "python":
            code = f"""
def main():
    \"\"\"
    Auto-generated function for: {prompt}
    \"\"\"
    # TODO: Implement {prompt}
    print("Implementing: {prompt}")
    
if __name__ == "__main__":
    main()
"""
        elif language == "javascript":
            code = f"""
function main() {{
    // Auto-generated function for: {prompt}
    console.log("Implementing: {prompt}");
}}

main();
"""
        else:
            code = f"// Auto-generated code for: {prompt}\n// Language: {language}"
            
        return {
            "code": code,
            "language": language,
            "confidence": 0.9,
            "source": "mock_azure_ai_foundry"
        }
    
    def _mock_code_optimization(self, code: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Create a mock response for code optimization."""
        target = options.get("optimization_target", "performance")
        language = options.get("language", "python")
        
        # Add mock optimization comments
        if language == "python":
            optimized_code = f"""# Optimized for {target}
# Improvements: Algorithm efficiency, memory usage
{code}

# Additional optimizations applied:
# - Used more efficient data structures
# - Reduced time complexity
"""
        else:
            optimized_code = f"""// Optimized for {target}
// Improvements: Algorithm efficiency, memory usage
{code}

// Additional optimizations applied:
// - Used more efficient data structures
// - Reduced time complexity
"""
            
        return {
            "optimized_code": optimized_code,
            "language": language,
            "improvements": [f"Optimized for {target}", "Algorithm efficiency", "Memory usage"],
            "estimated_speedup": "35%",
            "source": "mock_azure_ai_foundry"
        }

# Singleton instance
_instance = None

def get_azure_foundry_client():
    """Get or create the Azure AI Foundry client instance."""
    global _instance
    if _instance is None:
        _instance = AzureAIFoundry()
    return _instance