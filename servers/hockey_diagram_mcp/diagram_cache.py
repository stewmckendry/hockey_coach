"""
Hockey Diagram Cache Manager
Handles semantic caching of diagram specifications using ChromaDB.
Stores parsed specs and metadata for quick retrieval and reuse.
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import uuid4

import chromadb
from chromadb.api import ClientAPI
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

logger = logging.getLogger(__name__)

class DiagramCacheManager:
    """Manages caching of hockey diagram specifications in ChromaDB."""
    
    COLLECTION_NAME = "hockey_diagram_specs"
    
    def __init__(self, chroma_host: str = "localhost", chroma_port: int = 8000):
        """Initialize the cache manager with ChromaDB connection."""
        self.host = chroma_host
        self.port = chroma_port
        self._client = None
        self._collection = None
        self._embed_function = None
        
    def _get_client(self) -> ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                # Try HTTP client first
                self._client = chromadb.HttpClient(host=self.host, port=self.port)
                self._client.heartbeat()
                logger.info(f"Connected to ChromaDB at {self.host}:{self.port}")
            except Exception as e:
                logger.warning(f"HTTP client failed: {e}, using PersistentClient")
                # Fall back to persistent client
                self._client = chromadb.PersistentClient(
                    path="./chroma_diagram_cache"
                )
                logger.info("Using local PersistentClient for diagram cache")
        return self._client
    
    def _get_collection(self):
        """Get or create the diagram specs collection."""
        if self._collection is None:
            client = self._get_client()
            
            # Initialize embedding function
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self._embed_function = OpenAIEmbeddingFunction(api_key=api_key)
            else:
                logger.warning("No OPENAI_API_KEY found, using default embedding")
                self._embed_function = None
            
            # Get or create collection
            self._collection = client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                embedding_function=self._embed_function,
                metadata={"description": "Hockey diagram specifications cache"}
            )
            logger.info(f"Collection '{self.COLLECTION_NAME}' ready")
            
        return self._collection
    
    def save_diagram(
        self,
        prompt: str,
        spec: Dict[str, Any],
        parser_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save a diagram specification to the cache.
        
        Args:
            prompt: Original user prompt
            spec: Parsed diagram specification
            parser_type: Type of parser used (two_stage, enhanced, basic)
            metadata: Additional metadata (tags, author, etc.)
            
        Returns:
            Unique ID of the cached diagram
        """
        collection = self._get_collection()
        
        # Generate unique ID
        diagram_id = f"diagram_{uuid4().hex[:12]}"
        
        # Prepare metadata
        cache_metadata = {
            "prompt": prompt,
            "parser_type": parser_type,
            "created_at": datetime.utcnow().isoformat(),
            "spec_hash": hashlib.md5(json.dumps(spec, sort_keys=True).encode()).hexdigest(),
            "usage_count": 0,
            "last_used": datetime.utcnow().isoformat(),
            "validated": False
        }
        
        # Add custom metadata if provided, converting lists to JSON strings
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (list, dict)):
                    # Convert lists and dicts to JSON strings for ChromaDB
                    cache_metadata[key] = json.dumps(value)
                elif value is not None:
                    cache_metadata[key] = value
        
        # Store in ChromaDB
        collection.add(
            ids=[diagram_id],
            documents=[prompt],  # Use prompt as searchable document
            metadatas=[{
                **cache_metadata,
                "spec": json.dumps(spec)  # Store spec as JSON string in metadata
            }]
        )
        
        logger.info(f"Saved diagram {diagram_id} to cache")
        return diagram_id
    
    def search_diagrams(
        self,
        query: str,
        limit: int = 10,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for similar cached diagrams using semantic similarity.
        
        Args:
            query: Search query (typically a prompt)
            limit: Maximum number of results
            min_similarity: Minimum similarity score (0-1)
            
        Returns:
            List of matching diagram records
        """
        collection = self._get_collection()
        
        try:
            # Perform semantic search
            results = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            diagrams = []
            if results and results['ids'] and results['ids'][0]:
                for idx, diagram_id in enumerate(results['ids'][0]):
                    # Calculate similarity score (1 - distance)
                    distance = results['distances'][0][idx] if results['distances'] else 0
                    similarity = 1 - (distance / 2)  # Normalize to 0-1 range
                    
                    if similarity >= min_similarity:
                        metadata = results['metadatas'][0][idx]
                        
                        # Parse spec from JSON string
                        spec = json.loads(metadata.get('spec', '{}'))
                        
                        # Parse tags if it's a JSON string
                        tags = metadata.get('tags', '[]')
                        if isinstance(tags, str):
                            try:
                                tags = json.loads(tags)
                            except:
                                tags = []
                        
                        diagrams.append({
                            'id': diagram_id,
                            'prompt': metadata.get('prompt', ''),
                            'spec': spec,
                            'parser_type': metadata.get('parser_type', ''),
                            'created_at': metadata.get('created_at', ''),
                            'usage_count': metadata.get('usage_count', 0),
                            'validated': metadata.get('validated', False),
                            'similarity': similarity,
                            'tags': tags,
                            'author': metadata.get('author', 'anonymous')
                        })
            
            logger.info(f"Found {len(diagrams)} cached diagrams for query")
            return diagrams
            
        except Exception as e:
            logger.error(f"Error searching diagrams: {e}")
            return []
    
    def list_all_diagrams(
        self,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        ascending: bool = False
    ) -> Dict[str, Any]:
        """
        List all diagrams in the cache with pagination support.
        
        Args:
            limit: Maximum number of diagrams to return (default 50, max 100)
            offset: Number of diagrams to skip for pagination
            sort_by: Field to sort by ('created_at', 'usage_count', 'prompt')
            ascending: Sort order (False = descending/newest first)
            
        Returns:
            Dictionary with diagrams list and pagination info
        """
        collection = self._get_collection()
        
        try:
            # Get all diagrams
            all_results = collection.get()
            
            if not all_results or not all_results['ids']:
                return {
                    'success': True,
                    'diagrams': [],
                    'total': 0,
                    'limit': limit,
                    'offset': offset,
                    'has_more': False
                }
            
            # Build diagram list
            diagrams = []
            for idx, diagram_id in enumerate(all_results['ids']):
                metadata = all_results['metadatas'][idx]
                
                # Parse spec from JSON string
                spec = json.loads(metadata.get('spec', '{}'))
                
                # Parse tags if it's a JSON string
                tags = metadata.get('tags', '[]')
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except:
                        tags = []
                
                diagrams.append({
                    'id': diagram_id,
                    'prompt': metadata.get('prompt', ''),
                    'spec': spec,
                    'parser_type': metadata.get('parser_type', ''),
                    'created_at': metadata.get('created_at', ''),
                    'usage_count': metadata.get('usage_count', 0),
                    'validated': metadata.get('validated', False),
                    'tags': tags,
                    'author': metadata.get('author', 'anonymous')
                })
            
            # Sort diagrams
            if sort_by == 'usage_count':
                diagrams.sort(key=lambda x: x['usage_count'], reverse=not ascending)
            elif sort_by == 'prompt':
                diagrams.sort(key=lambda x: x['prompt'].lower(), reverse=not ascending)
            else:  # Default to created_at
                diagrams.sort(key=lambda x: x['created_at'], reverse=not ascending)
            
            # Apply pagination
            total = len(diagrams)
            limit = min(limit, 100)  # Cap at 100
            paginated_diagrams = diagrams[offset:offset + limit]
            
            return {
                'success': True,
                'diagrams': paginated_diagrams,
                'total': total,
                'limit': limit,
                'offset': offset,
                'has_more': (offset + limit) < total
            }
            
        except Exception as e:
            logger.error(f"Error listing diagrams: {e}")
            return {
                'success': False,
                'error': str(e),
                'diagrams': [],
                'total': 0
            }
    
    def get_diagram(self, diagram_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific cached diagram by ID.
        
        Args:
            diagram_id: Unique diagram identifier
            
        Returns:
            Diagram record or None if not found
        """
        collection = self._get_collection()
        
        try:
            result = collection.get(ids=[diagram_id])
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                
                # Parse spec from JSON string
                spec = json.loads(metadata.get('spec', '{}'))
                
                # Parse tags if it's a JSON string
                tags = metadata.get('tags', '[]')
                if isinstance(tags, str):
                    try:
                        tags = json.loads(tags)
                    except:
                        tags = []
                
                # Update usage stats
                self._update_usage_stats(diagram_id)
                
                return {
                    'id': diagram_id,
                    'prompt': metadata.get('prompt', ''),
                    'spec': spec,
                    'parser_type': metadata.get('parser_type', ''),
                    'created_at': metadata.get('created_at', ''),
                    'usage_count': metadata.get('usage_count', 0) + 1,
                    'validated': metadata.get('validated', False),
                    'tags': tags,
                    'author': metadata.get('author', 'anonymous')
                }
            
            logger.warning(f"Diagram {diagram_id} not found")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving diagram {diagram_id}: {e}")
            return None
    
    def update_diagram(
        self,
        diagram_id: str,
        spec: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update a cached diagram's spec or metadata.
        
        Args:
            diagram_id: Unique diagram identifier
            spec: Updated diagram specification (optional)
            metadata: Updated metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        collection = self._get_collection()
        
        try:
            # Get existing record
            result = collection.get(ids=[diagram_id])
            
            if not result or not result['ids']:
                logger.warning(f"Diagram {diagram_id} not found for update")
                return False
            
            existing_metadata = result['metadatas'][0]
            
            # Update spec if provided
            if spec:
                existing_metadata['spec'] = json.dumps(spec)
                existing_metadata['spec_hash'] = hashlib.md5(
                    json.dumps(spec, sort_keys=True).encode()
                ).hexdigest()
                existing_metadata['updated_at'] = datetime.utcnow().isoformat()
            
            # Update metadata if provided
            if metadata:
                existing_metadata.update(metadata)
            
            # Update in collection
            collection.update(
                ids=[diagram_id],
                metadatas=[existing_metadata]
            )
            
            logger.info(f"Updated diagram {diagram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating diagram {diagram_id}: {e}")
            return False
    
    def delete_diagram(self, diagram_id: str) -> bool:
        """
        Delete a cached diagram.
        
        Args:
            diagram_id: Unique diagram identifier
            
        Returns:
            True if successful, False otherwise
        """
        collection = self._get_collection()
        
        try:
            collection.delete(ids=[diagram_id])
            logger.info(f"Deleted diagram {diagram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting diagram {diagram_id}: {e}")
            return False
    
    def _update_usage_stats(self, diagram_id: str):
        """Update usage statistics for a diagram."""
        try:
            collection = self._get_collection()
            result = collection.get(ids=[diagram_id])
            
            if result and result['ids']:
                metadata = result['metadatas'][0]
                metadata['usage_count'] = metadata.get('usage_count', 0) + 1
                metadata['last_used'] = datetime.utcnow().isoformat()
                
                collection.update(
                    ids=[diagram_id],
                    metadatas=[metadata]
                )
        except Exception as e:
            logger.warning(f"Failed to update usage stats for {diagram_id}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        collection = self._get_collection()
        
        try:
            # Get all diagrams
            all_results = collection.get()
            total_count = len(all_results['ids']) if all_results['ids'] else 0
            
            if total_count == 0:
                return {
                    'total_diagrams': 0,
                    'validated_count': 0,
                    'parser_types': {},
                    'most_used': [],
                    'recently_used': []
                }
            
            # Process statistics
            validated_count = 0
            parser_types = {}
            usage_data = []
            
            for metadata in all_results['metadatas']:
                if metadata.get('validated'):
                    validated_count += 1
                
                parser_type = metadata.get('parser_type', 'unknown')
                parser_types[parser_type] = parser_types.get(parser_type, 0) + 1
                
                usage_data.append({
                    'id': metadata.get('id'),
                    'prompt': metadata.get('prompt', '')[:50],
                    'usage_count': metadata.get('usage_count', 0),
                    'last_used': metadata.get('last_used', '')
                })
            
            # Sort by usage
            most_used = sorted(usage_data, key=lambda x: x['usage_count'], reverse=True)[:5]
            recently_used = sorted(usage_data, key=lambda x: x['last_used'], reverse=True)[:5]
            
            return {
                'total_diagrams': total_count,
                'validated_count': validated_count,
                'parser_types': parser_types,
                'most_used': most_used,
                'recently_used': recently_used
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_diagrams': 0,
                'error': str(e)
            }