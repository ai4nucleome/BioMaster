"""
GraphRAG: Graph-based Retrieval-Augmented Generation
Implements knowledge graph for context-aware document retrieval
"""

import os
import logging
import pickle
from typing import List, Dict, Optional, Tuple
import numpy as np

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logging.warning("NetworkX not available. GraphRAG functionality will be limited.")

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document


class GraphRAG:
    """
    Graph-based RAG system that:
    1. Builds a knowledge graph from documents
    2. Uses graph traversal for context-aware retrieval
    3. Discovers related documents through relationships
    """
    
    def __init__(
        self,
        collection_name: str,
        embedding_function: Embeddings,
        persist_directory: str = "./graph_db",
        similarity_threshold: float = 0.75,
        max_neighbors: int = 2
    ):
        """
        Initialize GraphRAG
        
        Args:
            collection_name: Name of the knowledge collection
            embedding_function: Embedding model for vectorization
            persist_directory: Directory to save graph data
            similarity_threshold: Minimum similarity to create edges (0-1)
            max_neighbors: Maximum neighbors to retrieve per node
        """
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX is required for GraphRAG. Please install: pip install 'networkx>=3.0,<4.0'")
        
        self.collection_name = collection_name
        self.embeddings = embedding_function
        self.persist_directory = persist_directory
        self.similarity_threshold = similarity_threshold
        self.max_neighbors = max_neighbors
        
        # Create persist directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize vector store (Chroma) for semantic search
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=os.path.join(persist_directory, "chroma")
        )
        
        # Initialize knowledge graph
        self.graph = nx.Graph()
        self.graph_path = os.path.join(persist_directory, f"{collection_name}_graph.pkl")
        
        # Document metadata: {doc_id: {content, metadata, embedding}}
        self.doc_metadata = {}
        self.metadata_path = os.path.join(persist_directory, f"{collection_name}_metadata.pkl")
        
        # Load existing graph if available
        self._load_graph()
        
        logging.info(f"GraphRAG initialized: {collection_name}")
        logging.info(f"Similarity threshold: {similarity_threshold}, Max neighbors: {max_neighbors}")
    
    def _load_graph(self):
        """Load existing graph and metadata from disk"""
        try:
            if os.path.exists(self.graph_path):
                with open(self.graph_path, 'rb') as f:
                    loaded_graph = pickle.load(f)
                
                # Ensure graph is undirected
                if loaded_graph.is_directed():
                    logging.info("Converting directed graph to undirected graph")
                    self.graph = loaded_graph.to_undirected()
                else:
                    self.graph = loaded_graph
                
                logging.info(f"Loaded graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
            
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, 'rb') as f:
                    self.doc_metadata = pickle.load(f)
                logging.info(f"Loaded metadata for {len(self.doc_metadata)} documents")
        except Exception as e:
            logging.warning(f"Failed to load graph: {e}. Starting with empty graph.")
            self.graph = nx.Graph()
            self.doc_metadata = {}
    
    def _save_graph(self):
        """Save graph and metadata to disk"""
        try:
            with open(self.graph_path, 'wb') as f:
                pickle.dump(self.graph, f)
            
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.doc_metadata, f)
            
            logging.debug(f"Saved graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
        except Exception as e:
            logging.error(f"Failed to save graph: {e}")
    
    def _compute_similarity(self, emb1: List[float], emb2: List[float]) -> float:
        """Compute cosine similarity between two embeddings"""
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(emb1, emb2) / (norm1 * norm2)
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs
    ) -> List[str]:
        """
        Add texts to the graph and vector store
        
        Args:
            texts: List of text strings to add
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        # Add to vector store first
        doc_ids = self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids, **kwargs)
        
        # Generate embeddings for graph
        embeddings = self.embeddings.embed_documents(texts)
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Add nodes to graph
        for doc_id, text, metadata, embedding in zip(doc_ids, texts, metadatas, embeddings):
            # Store metadata
            self.doc_metadata[doc_id] = {
                'content': text,
                'metadata': metadata,
                'embedding': embedding
            }
            
            # Add node to graph
            self.graph.add_node(doc_id, **metadata)
        
        # Build edges based on similarity
        self._build_edges(doc_ids, embeddings)
        
        # Save graph
        self._save_graph()
        
        logging.info(f"Added {len(doc_ids)} documents to GraphRAG")
        return doc_ids
    
    def _build_edges(self, new_doc_ids: List[str], new_embeddings: List[List[float]]):
        """Build edges between documents based on similarity"""
        # Compare new documents with existing ones
        all_doc_ids = list(self.doc_metadata.keys())
        
        for i, (new_id, new_emb) in enumerate(zip(new_doc_ids, new_embeddings)):
            for existing_id in all_doc_ids:
                if existing_id == new_id:
                    continue
                
                existing_emb = self.doc_metadata[existing_id]['embedding']
                similarity = self._compute_similarity(new_emb, existing_emb)
                
                # Create edge if similarity exceeds threshold
                if similarity >= self.similarity_threshold:
                    self.graph.add_edge(new_id, existing_id, weight=similarity)
    
    def get(self, ids: List[str]) -> Dict:
        """
        Get documents by IDs (compatible with Chroma interface)
        
        Args:
            ids: List of document IDs
            
        Returns:
            Dictionary with 'documents' key
        """
        return self.vector_store.get(ids=ids)
    
    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        """
        Search for similar documents using graph-based retrieval
        
        Args:
            query: Query string
            k: Number of documents to return
            
        Returns:
            List of Document objects
        """
        # First, get initial candidates using vector search
        initial_docs = self.vector_store.similarity_search(query, k=k)
        
        if not initial_docs:
            return []
        
        # Extract document IDs
        initial_ids = []
        for doc in initial_docs:
            # Try to get document ID from metadata or use hash
            doc_id = doc.metadata.get('id', hash(doc.page_content))
            initial_ids.append(str(doc_id))
        
        # Expand using graph neighbors
        expanded_ids = set(initial_ids)
        for doc_id in initial_ids:
            if doc_id in self.graph:
                # Get neighbors sorted by edge weight
                neighbors = list(self.graph.neighbors(doc_id))
                neighbors_with_weights = [
                    (n, self.graph[doc_id][n].get('weight', 0))
                    for n in neighbors
                ]
                neighbors_with_weights.sort(key=lambda x: x[1], reverse=True)
                
                # Add top neighbors
                for neighbor_id, weight in neighbors_with_weights[:self.max_neighbors]:
                    expanded_ids.add(neighbor_id)
        
        # Retrieve expanded documents
        expanded_docs = []
        for doc_id in list(expanded_ids)[:k * 2]:  # Get more than k to re-rank
            if doc_id in self.doc_metadata:
                metadata = self.doc_metadata[doc_id]
                doc = Document(
                    page_content=metadata['content'],
                    metadata=metadata['metadata']
                )
                expanded_docs.append(doc)
        
        # If we have the original docs, combine with expanded
        if expanded_docs:
            # Merge and deduplicate
            seen_content = set()
            final_docs = []
            
            # Prioritize initial docs
            for doc in initial_docs:
                if doc.page_content not in seen_content:
                    seen_content.add(doc.page_content)
                    final_docs.append(doc)
            
            # Add expanded docs
            for doc in expanded_docs:
                if doc.page_content not in seen_content and len(final_docs) < k:
                    seen_content.add(doc.page_content)
                    final_docs.append(doc)
            
            return final_docs[:k]
        
        return initial_docs
    
    def max_marginal_relevance_search(
        self, query: str, k: int = 4, fetch_k: int = 20, lambda_mult: float = 0.5, **kwargs
    ) -> List[Document]:
        """MMR search with graph expansion"""
        # Use vector store's MMR, then expand with graph
        initial_docs = self.vector_store.max_marginal_relevance_search(
            query, k=k, fetch_k=fetch_k, lambda_mult=lambda_mult, **kwargs
        )
        
        # For now, return as-is (could be enhanced with graph expansion)
        return initial_docs
    
    def similarity_search_with_score(self, query: str, k: int = 4, **kwargs) -> List[Tuple[Document, float]]:
        """Search with similarity scores"""
        return self.vector_store.similarity_search_with_score(query, k=k, **kwargs)
    
    def delete_collection(self):
        """Delete the collection and graph"""
        try:
            self.vector_store.delete_collection()
            
            # Clear graph
            self.graph.clear()
            self.doc_metadata.clear()
            
            # Remove files
            if os.path.exists(self.graph_path):
                os.remove(self.graph_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)
            
            logging.info(f"Deleted GraphRAG collection: {self.collection_name}")
        except Exception as e:
            logging.error(f"Failed to delete collection: {e}")
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the knowledge graph"""
        # Check connectivity based on graph type
        is_connected = False
        if len(self.graph.nodes) > 0:
            try:
                if self.graph.is_directed():
                    is_connected = nx.is_weakly_connected(self.graph)
                else:
                    is_connected = nx.is_connected(self.graph)
            except:
                is_connected = False
        
        return {
            'num_nodes': len(self.graph.nodes),
            'num_edges': len(self.graph.edges),
            'num_documents': len(self.doc_metadata),
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(len(self.graph.nodes), 1),
            'is_connected': is_connected,
            'graph_type': 'directed' if self.graph.is_directed() else 'undirected'
        }

