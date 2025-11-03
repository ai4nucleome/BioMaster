from agents.Biomaster import Biomaster
from langchain_core.messages import HumanMessage
import yaml
import json
import os
import sys

# Load configuration from YAML file
def load_config(config_path='config.yaml'):
    """Load YAML configuration file"""
    with open(config_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

# Main function
if __name__ == "__main__":
    # Parse command line arguments to get config file path
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    
    # If config file doesn't exist, report error and exit
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' does not exist")
        sys.exit(1)
    
    # Load configuration
    config = load_config(config_path)
    
    # Get API settings from configuration
    api_key = config['api']['main']['key']
    base_url = config['api']['main']['base_url']
    embedding_api_key = config['api']['embedding']['key']
    embedding_base_url = config['api']['embedding']['base_url']
    
    # Ollama settings
    use_ollama = config.get('biomaster', {}).get('use_ollama', False)
    ollama_config = config.get('api', {}).get('ollama', {})
    ollama_enabled = ollama_config.get('enabled', False)
    # Use ollama if specified in both biomaster and ollama sections
    use_ollama = use_ollama and ollama_enabled
    ollama_base_url = ollama_config.get('base_url', 'http://localhost:11434')
    
    # Get model settings from configuration
    Model = config['models']['main']
    tool_model = config['models'].get('tool', Model)  # Use main model if tool model not specified
    embedding_model = config['models']['embedding']
    
    # Get Biomaster settings from configuration
    excutor = config['biomaster']['executor']
    ids = config['biomaster']['id']
    generate_plan = config['biomaster'].get('generate_plan', True)  # Default to True
    
    # Get RAG settings from configuration
    rag_config = config.get('rag', {})
    rag_type = rag_config.get('type', 'vector')
    
    # Retrieval settings
    retrieval_config = rag_config.get('retrieval', {})
    plan_k = retrieval_config.get('plan_k', 1)
    task_k = retrieval_config.get('task_k', 2)
    plan_search_type = retrieval_config.get('plan_search_type', 'similarity')
    task_search_type = retrieval_config.get('task_search_type', 'similarity')
    score_threshold = retrieval_config.get('score_threshold', 0.7)
    mmr_diversity_score = retrieval_config.get('mmr_diversity_score', 0.3)
    diverse_multiplier = retrieval_config.get('diverse_multiplier', 3)
    rerank_multiplier = retrieval_config.get('rerank_multiplier', 2)
    
    # Vector RAG settings
    vector_config = rag_config.get('vector', {})
    chroma_db_dir = vector_config.get('chroma_db_dir', './chroma_db')
    
    # Graph RAG settings
    graph_config = rag_config.get('graph', {})
    graph_db_dir = graph_config.get('persist_directory', './graph_db')
    graph_similarity_threshold = graph_config.get('similarity_threshold', 0.75)
    graph_max_neighbors = graph_config.get('max_neighbors', 2)
    
    # Hybrid RAG settings
    hybrid_config = rag_config.get('hybrid', {})
    hybrid_db_dir = hybrid_config.get('persist_directory', './hybrid_db')
    hybrid_vector_weight = hybrid_config.get('vector_weight', 0.6)
    hybrid_graph_weight = hybrid_config.get('graph_weight', 0.4)
    hybrid_enable_reranking = hybrid_config.get('enable_reranking', True)
    
    # Get data and goal from configuration
    datalist = config['data']['files']
    goal = config['data']['goal']

    print(f"Using ollama: {use_ollama}")
    print(f"Ollama base URL: {ollama_base_url}")
    print(f"Model: {Model}")
    print(f"Embedding model: {embedding_model}")
    print(f"RAG type: {rag_type}")

    # Initialize Biomaster instance
    manager = Biomaster(
        api_key, 
        base_url,
        excutor=excutor,
        id=ids,
        Model=Model,
        embedding_model=embedding_model,
        tool_model=tool_model,
        embedding_base_url=embedding_base_url,
        embedding_api_key=embedding_api_key,
        use_ollama=use_ollama,
        ollama_base_url=ollama_base_url,
        rag_type=rag_type,
        chroma_db_dir=chroma_db_dir,
        graph_db_dir=graph_db_dir,
        graph_similarity_threshold=graph_similarity_threshold,
        graph_max_neighbors=graph_max_neighbors,
        hybrid_db_dir=hybrid_db_dir,
        hybrid_vector_weight=hybrid_vector_weight,
        hybrid_graph_weight=hybrid_graph_weight,
        hybrid_enable_reranking=hybrid_enable_reranking,
        plan_k=plan_k,
        task_k=task_k,
        plan_search_type=plan_search_type,
        task_search_type=task_search_type,
        score_threshold=score_threshold,
        mmr_diversity_score=mmr_diversity_score,
        diverse_multiplier=diverse_multiplier,
        rerank_multiplier=rerank_multiplier
    )
    
    # If using ollama, test connection
    if use_ollama:
        print("Testing Ollama connection...")
        if not manager.test_ollama_connection():
            print("Warning: Unable to connect to ollama service or model not found. Continuing in API mode.")
            manager.use_ollama = False
        else:
            print(f"Successfully connected to Ollama service, using model: {manager.ollama_model} and embedding model: {manager.ollama_embedding_model}")

    # Execute PLAN based on configuration
    if generate_plan:
        manager.execute_PLAN(goal, datalist)
        print("**********************************************************")

    # Execute TASK
    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)
