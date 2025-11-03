"""
Test script to compare Vector RAG and GraphRAG performance
"""

import sys
sys.path.append('..')

from agents.Biomaster import Biomaster
import time

def test_rag_system(rag_type='vector'):
    """
    Test a RAG system with sample queries
    
    Args:
        rag_type: 'vector' or 'graph'
    """
    print(f"\n{'='*60}")
    print(f"Testing {rag_type.upper()} RAG System")
    print(f"{'='*60}\n")
    
    # Initialize BioMaster with specified RAG type
    manager = Biomaster(
        api_key='your-api-key',
        base_url='https://api.siliconflow.cn/v1/',
        Model='deepseek-ai/DeepSeek-V3',
        embedding_model='BAAI/bge-m3',
        tool_model='deepseek-ai/DeepSeek-V3',
        excutor=False,
        id='test_rag',
        rag_type=rag_type,
        graph_similarity_threshold=0.75,
        graph_max_neighbors=2
    )
    
    # Test queries
    test_queries = [
        "ChIP-seq peak calling workflow",
        "RNA-seq differential expression analysis",
        "Single-cell clustering analysis",
        "Hi-C data preprocessing"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        # Measure retrieval time
        start_time = time.time()
        
        # PLAN RAG search
        plan_docs = manager.vectorstore.similarity_search(query, k=3)
        
        # TASK RAG search
        task_docs = manager.vectorstore_tool.similarity_search(query, k=3)
        
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Retrieval time: {elapsed_time:.4f}s")
        print(f"\n📋 PLAN RAG Results ({len(plan_docs)} documents):")
        for i, doc in enumerate(plan_docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:100] + "..."
            print(f"  {i}. [{source}] {content_preview}")
        
        print(f"\n🔧 TASK RAG Results ({len(task_docs)} documents):")
        for i, doc in enumerate(task_docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            content_preview = doc.page_content[:100] + "..."
            print(f"  {i}. [{source}] {content_preview}")
        
        print()
    
    # Display graph statistics if using GraphRAG
    if rag_type == 'graph':
        print("\n" + "="*60)
        print("GraphRAG Statistics")
        print("="*60)
        plan_stats = manager.vectorstore.get_graph_stats()
        task_stats = manager.vectorstore_tool.get_graph_stats()
        
        print("\n📊 PLAN Knowledge Graph:")
        for key, value in plan_stats.items():
            print(f"  {key}: {value}")
        
        print("\n📊 TASK Knowledge Graph:")
        for key, value in task_stats.items():
            print(f"  {key}: {value}")
        print()


def compare_rag_systems():
    """
    Run comparative tests between Vector RAG and GraphRAG
    """
    print("\n" + "="*60)
    print("BioMaster RAG System Comparison Test")
    print("="*60)
    
    # Test Vector RAG
    print("\n🔵 Phase 1: Testing Vector RAG (Chroma)")
    print("-" * 60)
    test_rag_system(rag_type='vector')
    
    # Test GraphRAG
    print("\n🟢 Phase 2: Testing GraphRAG")
    print("-" * 60)
    test_rag_system(rag_type='graph')
    
    print("\n" + "="*60)
    print("Comparison Summary")
    print("="*60)
    print("""
    Vector RAG:
    ✅ Faster retrieval
    ✅ Lower memory usage
    ✅ Simple and reliable
    ⚠️  No context expansion
    
    GraphRAG:
    ✅ Context-aware retrieval
    ✅ Discovers related knowledge
    ✅ Better for complex workflows
    ⚠️  Slightly slower
    ⚠️  Higher memory usage
    
    Recommendation:
    - Use Vector RAG for general-purpose queries
    - Use GraphRAG for complex, multi-step workflows
    """)


if __name__ == "__main__":
    # Check if API key is provided
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type in ['vector', 'graph']:
            test_rag_system(rag_type=test_type)
        elif test_type == 'compare':
            compare_rag_systems()
        else:
            print("Usage: python test_graphrag.py [vector|graph|compare]")
    else:
        # Run comparison by default
        compare_rag_systems()

