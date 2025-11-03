"""
HybridRAG: Combines Vector and Graph-based RAG for optimal retrieval
"""

import os
import logging
import numpy as np
from typing import List, Dict, Optional

from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

from .GraphRAG import GraphRAG


class HybridRAG:
    """
    Hybrid RAG system that combines:
    1. Vector-based retrieval (fast, semantic similarity)
    2. Graph-based retrieval (context-aware, relationship discovery)
    
    Uses weighted scoring and re-ranking for optimal results.
    """
    
    def __init__(
        self,
        collection_name: str,
        embedding_function: Embeddings,
        persist_directory: str = "./hybrid_db",
        vector_weight: float = 0.6,
        graph_weight: float = 0.4,
        similarity_threshold: float = 0.75,
        max_neighbors: int = 2,
        enable_reranking: bool = True
    ):
        """
        Initialize HybridRAG
        
        Args:
            collection_name: Name of the knowledge collection
            embedding_function: Embedding model for vectorization
            persist_directory: Directory to save hybrid data
            vector_weight: Weight for vector similarity scores (0-1)
            graph_weight: Weight for graph context scores (0-1)
            similarity_threshold: Threshold for graph edge creation
            max_neighbors: Max neighbors for graph expansion
            enable_reranking: Whether to re-rank results
        """
        self.collection_name = collection_name
        self.embeddings = embedding_function
        self.persist_directory = persist_directory
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight
        self.enable_reranking = enable_reranking
        
        # Create persist directory
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize Vector RAG (Chroma)
        self.vector_store = Chroma(
            collection_name=f"{collection_name}_vector",
            embedding_function=embedding_function,
            persist_directory=os.path.join(persist_directory, "vector")
        )
        
        # Initialize Graph RAG
        self.graph_store = GraphRAG(
            collection_name=f"{collection_name}_graph",
            embedding_function=embedding_function,
            persist_directory=os.path.join(persist_directory, "graph"),
            similarity_threshold=similarity_threshold,
            max_neighbors=max_neighbors
        )
        
        # Document ID mapping: {doc_id: content}
        self.doc_id_map = {}
        
        logging.info(f"HybridRAG initialized: {collection_name}")
        logging.info(f"Weights - Vector: {vector_weight}, Graph: {graph_weight}")
        logging.info(f"Reranking: {'enabled' if enable_reranking else 'disabled'}")
    
    def get(self, ids: List[str]) -> Dict:
        """
        Get documents by IDs (compatible with Chroma interface)
        
        Args:
            ids: List of document IDs
            
        Returns:
            Dictionary with 'documents' key
        """
        # Try vector store first (faster)
        result = self.vector_store.get(ids=ids)
        if result['documents']:
            return result
        
        # Fallback to graph store
        return self.graph_store.get(ids=ids)
    
    def add_texts(
        self,
        texts: List[str],
        metadatas: List[Dict],
        ids: List[str]
    ):
        """
        Add texts to both vector and graph stores
        
        Args:
            texts: List of text contents
            metadatas: List of metadata dictionaries
            ids: List of document IDs
        """
        if not texts:
            return
        
        # Add to vector store
        self.vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Add to graph store
        self.graph_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        # Update document ID mapping
        for doc_id, text in zip(ids, texts):
            self.doc_id_map[doc_id] = text
        
        logging.info(f"Added {len(texts)} documents to HybridRAG")
    
    def _compute_vector_scores(
        self,
        query: str,
        candidate_docs: List
    ) -> Dict[str, float]:
        """
        Compute vector similarity scores for candidate documents
        
        Args:
            query: Query string
            candidate_docs: List of candidate document objects
            
        Returns:
            Dictionary mapping doc_id to vector score
        """
        # Generate query embedding
        query_embedding = np.array(self.embeddings.embed_query(query))
        
        scores = {}
        for doc in candidate_docs:
            # Get document embedding
            doc_text = doc.page_content
            doc_embedding = np.array(self.embeddings.embed_documents([doc_text])[0])
            
            # Compute cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            # Use metadata.id or generate one
            doc_id = doc.metadata.get('id', hash(doc_text))
            scores[str(doc_id)] = float(similarity)
        
        return scores
    
    def _compute_graph_scores(
        self,
        candidate_docs: List
    ) -> Dict[str, float]:
        """
        Compute graph-based scores considering relationships
        
        Args:
            candidate_docs: List of candidate document objects
            
        Returns:
            Dictionary mapping doc_id to graph score
        """
        scores = {}
        
        # Get graph statistics
        graph_stats = self.graph_store.get_graph_stats()
        avg_degree = graph_stats.get('avg_degree', 1.0)
        
        for doc in candidate_docs:
            doc_id = str(doc.metadata.get('id', hash(doc.page_content)))
            
            # Base score: 0.5
            score = 0.5
            
            # Bonus for having many connections (hub nodes are important)
            try:
                node_id = doc_id
                if node_id in self.graph_store.graph:
                    degree = self.graph_store.graph.degree(node_id)
                    # Normalize by average degree
                    degree_score = min(1.0, degree / (avg_degree + 1))
                    score += 0.3 * degree_score
            except:
                pass
            
            # Bonus for same source as other high-scoring docs
            source = doc.metadata.get('source', '')
            if source:
                source_bonus = 0.2
                score += source_bonus
            
            scores[doc_id] = score
        
        return scores
    
    def _hybrid_score(
        self,
        doc_id: str,
        vector_scores: Dict[str, float],
        graph_scores: Dict[str, float]
    ) -> float:
        """
        Compute hybrid score combining vector and graph signals
        
        Args:
            doc_id: Document ID
            vector_scores: Vector similarity scores
            graph_scores: Graph relationship scores
            
        Returns:
            Combined hybrid score
        """
        v_score = vector_scores.get(doc_id, 0.0)
        g_score = graph_scores.get(doc_id, 0.5)
        
        # Weighted combination
        hybrid = self.vector_weight * v_score + self.graph_weight * g_score
        
        return hybrid
    
    def _rerank_documents(
        self,
        docs: List,
        scores: Dict[str, float]
    ) -> List:
        """
        Re-rank documents by hybrid scores
        
        Args:
            docs: List of document objects
            scores: Hybrid scores for each document
            
        Returns:
            Re-ranked list of documents
        """
        # Create (doc, score) pairs
        doc_score_pairs = []
        for doc in docs:
            doc_id = str(doc.metadata.get('id', hash(doc.page_content)))
            score = scores.get(doc_id, 0.0)
            doc_score_pairs.append((doc, score))
        
        # Sort by score (descending)
        doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Return sorted documents
        return [doc for doc, score in doc_score_pairs]
    
    def similarity_search(self, query: str, k: int = 4) -> List:
        """
        Perform hybrid similarity search
        
        Args:
            query: Query text
            k: Number of documents to return
            
        Returns:
            List of Document objects
        """
        # Step 1: Get candidates from both stores
        # Vector store: Get more candidates for better coverage
        vector_k = k * 2
        vector_docs = self.vector_store.similarity_search(query, k=vector_k)
        
        # Graph store: Get candidates with context expansion
        graph_k = k
        graph_docs = self.graph_store.similarity_search(query, k=graph_k)
        
        # Step 2: Merge candidates (remove duplicates)
        seen_contents = set()
        all_docs = []
        
        for doc in vector_docs + graph_docs:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                all_docs.append(doc)
        
        if not all_docs:
            logging.warning("No documents found in hybrid search")
            return []
        
        # Step 3: Compute scores
        vector_scores = self._compute_vector_scores(query, all_docs)
        graph_scores = self._compute_graph_scores(all_docs)
        
        # Step 4: Combine scores
        hybrid_scores = {}
        for doc in all_docs:
            doc_id = str(doc.metadata.get('id', hash(doc.page_content)))
            hybrid_scores[doc_id] = self._hybrid_score(
                doc_id, vector_scores, graph_scores
            )
        
        # Step 5: Re-rank if enabled
        if self.enable_reranking:
            all_docs = self._rerank_documents(all_docs, hybrid_scores)
        
        # Step 6: Return top k
        result_docs = all_docs[:k]
        
        logging.info(
            f"HybridRAG search: query='{query[:50]}...', "
            f"vector_candidates={len(vector_docs)}, "
            f"graph_candidates={len(graph_docs)}, "
            f"merged={len(all_docs)}, "
            f"returned={len(result_docs)}"
        )
        
        return result_docs
    
    def get_stats(self) -> Dict:
        """Get statistics about both stores"""
        vector_count = self.vector_store._collection.count()
        graph_stats = self.graph_store.get_graph_stats()
        
        return {
            'vector_store': {
                'num_documents': vector_count
            },
            'graph_store': graph_stats,
            'weights': {
                'vector': self.vector_weight,
                'graph': self.graph_weight
            },
            'reranking_enabled': self.enable_reranking
        }

