import os
import subprocess
import json
import re
import logging
from datetime import datetime
import uuid  # Used for generating unique IDs
import requests
import numpy as np
from typing import List

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain_chroma import Chroma  # Using Chroma from langchain_chroma package
from langchain_community.tools import ShellTool
from langchain_community.llms import Ollama  # Import Ollama support

from .prompts import PLAN_PROMPT, PLAN_EXAMPLES, TASK_PROMPT, TASK_EXAMPLES, DEBUG_EXAMPLES, DEBUG_PROMPT
from .ToolAgent import Json_Format_Agent
from .CheckAgent import CheckAgent  # Add this import at the top
from .ollama import OllamaEmbeddings
# Lazy import for GraphRAG and HybridRAG to avoid NetworkX compatibility issues
# They will be imported only when actually needed


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Biomaster:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        Model: str = "o3-mini",
        embedding_model: str = "text-embedding-ada-002",
        tool_model: str = "gpt-4o-mini",
        excutor: bool = False,
        Repeat: int = 5,
        output_dir: str = './output',
        id: str = '001',
        embedding_base_url: str=None,
        embedding_api_key: str=None,
        chroma_db_dir: str = './chroma_db',  # Chroma persistence directory
        token_log_path: str = './token.txt',  # Add token log path parameter
        use_ollama: bool = False,  # Whether to use ollama
        ollama_base_url: str = "http://localhost:11434",  # Ollama API address
        rag_type: str = 'vector',  # RAG type: 'vector', 'graph', or 'hybrid'
        graph_db_dir: str = './graph_db',  # GraphRAG persistence directory
        graph_similarity_threshold: float = 0.75,  # Similarity threshold for GraphRAG
        graph_max_neighbors: int = 2,  # Max neighbors for GraphRAG
        hybrid_db_dir: str = './hybrid_db',  # HybridRAG persistence directory
        hybrid_vector_weight: float = 0.6,  # Vector weight for HybridRAG
        hybrid_graph_weight: float = 0.4,  # Graph weight for HybridRAG
        hybrid_enable_reranking: bool = True,  # Enable reranking for HybridRAG
        plan_k: int = 1,  # Number of documents to retrieve for PLAN phase
        task_k: int = 2,  # Number of documents to retrieve for TASK phase
        plan_search_type: str = 'similarity',  # Search strategy for PLAN phase
        task_search_type: str = 'similarity',  # Search strategy for TASK phase
        score_threshold: float = 0.7,  # Minimum similarity score threshold
        mmr_diversity_score: float = 0.3,  # MMR diversity score (0-1)
        diverse_multiplier: int = 3,  # Multiplier for diverse search
        rerank_multiplier: int = 2  # Multiplier for rerank search
    ):
        # Set USER_AGENT environment variable to eliminate warnings
        os.environ['USER_AGENT'] = 'Biomaster/1.0'
        
        self.api_key = api_key
        self.base_url = base_url
        self.model = Model
        self.doc_dir = "doc"
        self.excutor = excutor
        self.repeat = Repeat
        self.output_dir = output_dir
        self.stop_flag = False  # Flag
        self.token_log_path = token_log_path
        self.tool_model = tool_model
        
        # RAG settings
        self.rag_type = rag_type.lower()
        self.chroma_db_dir = chroma_db_dir
        self.graph_db_dir = graph_db_dir
        self.graph_similarity_threshold = graph_similarity_threshold
        self.graph_max_neighbors = graph_max_neighbors
        self.hybrid_db_dir = hybrid_db_dir
        self.hybrid_vector_weight = hybrid_vector_weight
        self.hybrid_graph_weight = hybrid_graph_weight
        self.hybrid_enable_reranking = hybrid_enable_reranking
        
        # Retrieval parameters
        self.plan_k = plan_k
        self.task_k = task_k
        self.plan_search_type = plan_search_type.lower()
        self.task_search_type = task_search_type.lower()
        self.score_threshold = score_threshold
        self.mmr_diversity_score = mmr_diversity_score
        self.diverse_multiplier = diverse_multiplier
        self.rerank_multiplier = rerank_multiplier
        
        # Ollama settings
        self.use_ollama = use_ollama
        self.ollama_base_url = ollama_base_url
        
        # Automatically map model names to ollama models
        if self.use_ollama:
            self.ollama_model = self.model
            self.ollama_embedding_model = embedding_model
        else:
            self.ollama_model = None
            self.ollama_embedding_model = None
        
        if embedding_base_url== None or embedding_api_key== None:
            self.embedding_base_url = self.base_url
            self.embedding_api_key = self.api_key
        else:
            self.embedding_base_url = embedding_base_url
            self.embedding_api_key = embedding_api_key
        os.environ['OPENAI_API_KEY'] = self.api_key
        
        if id == '000':
            self.id = self._generate_new_id()
        else:
            self.id = id
            self._load_existing_files()

        self.tool_names = self.load_tool_links()
        print(self.tool_names)

        self.PLAN_prompt = PLAN_PROMPT.format(tool_names=self.tool_names)
        self.TASK_prompt = TASK_PROMPT.format(tool_names=self.tool_names)
        self.DEBUG_prompt = DEBUG_PROMPT.format(tool_names=self.tool_names)

        self.PLAN_examples = PLAN_EXAMPLES
        self.TASK_examples = TASK_EXAMPLES
        self.DEBUG_examples = DEBUG_EXAMPLES

        # Initialize agents
        if self.use_ollama:
            self.DEBUG_agent = self._create_ollama_agent(self.DEBUG_prompt, self.DEBUG_examples)
            self.TASK_agent = self._create_ollama_agent(self.TASK_prompt, self.TASK_examples)
            self.PLAN_agent = self._create_ollama_agent(self.PLAN_prompt, self.PLAN_examples)
            # Use custom Ollama embeddings model
            self.embeddings = OllamaEmbeddings(
                base_url=self.ollama_base_url,
                model=self.ollama_embedding_model
            )
        else:
            self.DEBUG_agent = self._create_agent(self.DEBUG_prompt, self.DEBUG_examples)
            self.TASK_agent = self._create_agent(self.TASK_prompt, self.TASK_examples)
            self.PLAN_agent = self._create_agent(self.PLAN_prompt, self.PLAN_examples)
            # Create embeddings instance and pass API key directly
            self.embeddings = OpenAIEmbeddings(
                model=embedding_model, 
                base_url=self.embedding_base_url,
                api_key=self.embedding_api_key
            )

        # Store collection name
        self.collection1_name = "popgen_collection1"
        self.collection2_name = "popgen_collection2"

        # Initialize vector storage based on RAG type
        if self.rag_type == 'graph':
            logging.info("Initializing GraphRAG knowledge base...")
            try:
                from .GraphRAG import GraphRAG
                self.vectorstore = GraphRAG(
                    collection_name=self.collection1_name,
                    embedding_function=self.embeddings,
                    persist_directory=os.path.join(self.graph_db_dir, "collection1"),
                    similarity_threshold=self.graph_similarity_threshold,
                    max_neighbors=self.graph_max_neighbors
                )
                self.vectorstore_tool = GraphRAG(
                    collection_name=self.collection2_name,
                    embedding_function=self.embeddings,
                    persist_directory=os.path.join(self.graph_db_dir, "collection2"),
                    similarity_threshold=self.graph_similarity_threshold,
                    max_neighbors=self.graph_max_neighbors
                )
                logging.info("GraphRAG initialized successfully")
            except ImportError as e:
                logging.error(f"Failed to import GraphRAG: {e}")
                logging.error("Please install networkx: pip install 'networkx>=3.0,<4.0'")
                logging.info("Falling back to Vector RAG (Chroma)")
                self.rag_type = 'vector'
            except Exception as e:
                logging.error(f"Failed to initialize GraphRAG: {e}")
                logging.info("Falling back to Vector RAG (Chroma)")
                self.rag_type = 'vector'
        
        if self.rag_type == 'hybrid':
            logging.info("Initializing HybridRAG knowledge base...")
            try:
                from .HybridRAG import HybridRAG
                self.vectorstore = HybridRAG(
                    collection_name=self.collection1_name,
                    embedding_function=self.embeddings,
                    persist_directory=os.path.join(self.hybrid_db_dir, "collection1"),
                    vector_weight=self.hybrid_vector_weight,
                    graph_weight=self.hybrid_graph_weight,
                    similarity_threshold=self.graph_similarity_threshold,
                    max_neighbors=self.graph_max_neighbors,
                    enable_reranking=self.hybrid_enable_reranking
                )
                self.vectorstore_tool = HybridRAG(
                    collection_name=self.collection2_name,
                    embedding_function=self.embeddings,
                    persist_directory=os.path.join(self.hybrid_db_dir, "collection2"),
                    vector_weight=self.hybrid_vector_weight,
                    graph_weight=self.hybrid_graph_weight,
                    similarity_threshold=self.graph_similarity_threshold,
                    max_neighbors=self.graph_max_neighbors,
                    enable_reranking=self.hybrid_enable_reranking
                )
                logging.info("HybridRAG initialized successfully")
            except ImportError as e:
                logging.error(f"Failed to import HybridRAG: {e}")
                logging.error("Please install networkx: pip install 'networkx>=3.0,<4.0'")
                logging.info("Falling back to Vector RAG (Chroma)")
                self.rag_type = 'vector'
            except Exception as e:
                logging.error(f"Failed to initialize HybridRAG: {e}")
                logging.info("Falling back to Vector RAG (Chroma)")
                self.rag_type = 'vector'
        
        if self.rag_type == 'vector':  # Default to vector (Chroma)
            logging.info("Initializing Vector (Chroma) knowledge base...")
            self.vectorstore = Chroma(
                collection_name=self.collection1_name,
                embedding_function=self.embeddings,
                persist_directory=os.path.join(self.chroma_db_dir, "collection1")
            )
            self.vectorstore_tool = Chroma(
                collection_name=self.collection2_name,
                embedding_function=self.embeddings,
                persist_directory=os.path.join(self.chroma_db_dir, "collection2")
            )
            logging.info("Vector RAG (Chroma) initialized successfully")

        # Load knowledge data (only add new data)
        self.Load_PLAN_RAG()
        self.Load_Tool_RAG()
        
        # Log statistics based on RAG type
        if self.rag_type == 'graph':
            plan_stats = self.vectorstore.get_graph_stats()
            tool_stats = self.vectorstore_tool.get_graph_stats()
            logging.info(f"PLAN GraphRAG stats: {plan_stats}")
            logging.info(f"TOOL GraphRAG stats: {tool_stats}")
        elif self.rag_type == 'hybrid':
            plan_stats = self.vectorstore.get_stats()
            tool_stats = self.vectorstore_tool.get_stats()
            logging.info(f"PLAN HybridRAG stats: {plan_stats}")
            logging.info(f"TOOL HybridRAG stats: {tool_stats}")

        # Initialize the CheckAgent
        if self.use_ollama:
            # If using ollama, CheckAgent also uses ollama
            self.check_agent = CheckAgent(api_key="", base_url="", model="", use_ollama=True, 
                                        ollama_base_url=self.ollama_base_url, ollama_model=self.ollama_model)
        else:
            self.check_agent = CheckAgent(api_key=api_key, base_url=base_url, model=self.tool_model)
        
    def _create_ollama_agent(self, prompt_template, examples):
        """Create agent based on ollama"""
        # Initialize Ollama LLM
        ollama_llm = Ollama(base_url=self.ollama_base_url, model=self.ollama_model)
        
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}")
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

        parser = StrOutputParser()

        final_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            few_shot_prompt,
            ("human", "{input}")
        ])

        # Create original agent
        agent = final_prompt | ollama_llm | parser
        
        return agent

    def test_ollama_connection(self):
        """
        Test connection to ollama
        
        Returns:
        - Boolean, indicating whether connection is successful
        """
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags")
            if response.status_code == 200:
                available_models = [model["name"] for model in response.json().get("models", [])]
                if self.ollama_model in available_models:
                    logging.info(f"Successfully connected to ollama server, found required model: {self.ollama_model}")
                    return True
                else:
                    available_models_str = ", ".join(available_models)
                    logging.warning(f"Successfully connected to ollama server, but required model: {self.ollama_model} not found. Available models: {available_models_str}")
                    return False
            else:
                logging.error(f"Failed to connect to ollama server: {response.status_code} - {response.text}")
                return False    
        except Exception as e:
            logging.error(f"Failed to connect to ollama server: {str(e)}")
            return False    
    
    def normalize_keys(self,input_dict):
        """ Recursively convert all dictionary keys to lowercase."""
        if isinstance(input_dict, dict):
            return {k.lower(): self.normalize_keys(v) for k, v in input_dict.items()}
        elif isinstance(input_dict, list):
            return [self.normalize_keys(item) for item in input_dict]
        else:
            return input_dict
    def load_tool_links(self):
        """Read Task_Knowledge.json and return the list of source in metadata"""
        json_file_path = os.path.join(self.doc_dir, "Task_Knowledge.json")
        print(json_file_path)
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            
            sources = []
            for item in data:
                if "metadata" in item and "source" in item["metadata"]:
                    sources.append(item["metadata"]["source"])
            
            return sources
        return []
    
    def _generate_new_id(self):
        existing_ids = []
        for file_name in os.listdir(self.output_dir):
            match = re.match(r'^(\d{3})_', file_name)
            if match:
                existing_ids.append(int(match.group(1)))

        new_id = min(set(range(1, max(existing_ids, default=0) + 2)) - set(existing_ids))
        return f'{new_id:03d}'

    def _load_existing_files(self):
        # Load PLAN and step files for specified ID
        plan_file = os.path.join(self.output_dir, f'{self.id}_PLAN.json')
        if os.path.exists(plan_file):
            self.plan_data = self.load_progress(self.output_dir, f'{self.id}_PLAN.json')
        else:
            print(f"No PLAN file found for ID: {self.id}")

        # Here you can add more logic to load other required files

    def check_stop(self):
        if self.stop_flag:
            print(f"Task {self.id} is being stopped.")
            raise Exception(f"Task {self.id} was stopped by user request.")

    def stop(self):
        self.stop_flag = True

    def add_documents_if_not_exists(self, documents, collection, collection_name):
        """
        Add documents to vector database if document ID does not exist.
        :param documents: List, containing dictionaries, dictionaries need 'page_content' and 'metadata' keys
        :param collection: Chroma vector database collection
        :param collection_name: String, collection name
        """
        new_texts = []
        new_metadatas = []
        new_ids = []
        for doc in documents:
            doc_id = doc['metadata'].get("id")
            if not doc_id:
                # If no ID, generate a unique ID
                doc_id = str(uuid.uuid4())
                doc['metadata']['id'] = doc_id

            # Use get method to check if document exists
            existing_docs = collection.get(ids=[doc_id])
            if not existing_docs['documents']:
                new_texts.append(doc['page_content'])
                new_metadatas.append(doc['metadata'])
                new_ids.append(doc_id)

        if new_texts:
            # Process documents in batches of up to 32 (maximum bulk processing size for most embedded models)
            batch_size = 32
            for i in range(0, len(new_texts), batch_size):
                batch_texts = new_texts[i:i+batch_size]
                batch_metadatas = new_metadatas[i:i+batch_size]
                batch_ids = new_ids[i:i+batch_size]
                
                collection.add_texts(texts=batch_texts, metadatas=batch_metadatas, ids=batch_ids)
                logging.info(f"Added batch of {len(batch_texts)} documents to {collection_name} (batch {i//batch_size + 1})")
            
            logging.info(f"Added total of {len(new_texts)} new documents to {collection_name}")

    def Load_PLAN_RAG(self):
        """
        Load knowledge entries from JSON file and store them in Chroma vector database.
        Each JSON entry is stored and retrieved as an independent unit.
        """
        json_file_path = os.path.join(self.doc_dir, "Plan_Knowledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON file format error: Should contain a list of knowledge entries")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore, self.collection1_name)
        logging.info("Loaded PLAN_RAG data.")
        # Chroma will automatically persist, no need to explicitly call persist()

    def Load_Tool_RAG(self):
        """
        Load knowledge entries from JSON file and store them in Chroma vector database.
        Each JSON entry is stored and retrieved as an independent unit.
        """
        json_file_path = os.path.join(self.doc_dir, "Task_Knowledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON file format error: Should contain a list of knowledge entries")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore_tool, self.collection2_name)
        logging.info("Loaded Tool_RAG data.")
        # Chroma will automatically persist, no need to explicitly call persist()

    def log_token_usage(self, model_name, input_tokens, output_tokens):
        """
        Record model token usage to log file
        
        :param model_name: Used model name
        :param input_tokens: Input token count
        :param output_tokens: Output token count
        """
        log_entry = f"Model: {model_name}, Input tokens: {input_tokens}, Output tokens: {output_tokens}\n"
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(os.path.abspath(self.token_log_path)), exist_ok=True)
        
        # Append log to file
        with open(self.token_log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
        
        # Output to console as well
        logging.info(f"Token usage: {log_entry.strip()}")

    def _perform_search(self, vectorstore, query: str, k: int, search_type: str):
        """
        Perform document retrieval using specified search strategy.
        
        Args:
            vectorstore: The vector store to search
            query: Search query string
            k: Number of documents to retrieve
            search_type: Type of search ('similarity', 'mmr', 'similarity_score_threshold', 'diverse', 'rerank')
        
        Returns:
            List of retrieved documents
        """
        search_type = search_type.lower()
        
        try:
            if search_type == 'similarity':
                # Standard cosine similarity search (default)
                docs = vectorstore.similarity_search(query, k=k)
                logging.info(f"Search type: similarity, retrieved {len(docs)} documents")
                
            elif search_type == 'mmr':
                # Maximum Marginal Relevance - balances relevance and diversity
                docs = vectorstore.max_marginal_relevance_search(
                    query, 
                    k=k,
                    fetch_k=k*3,  # Fetch more candidates for better diversity
                    lambda_mult=1.0 - self.mmr_diversity_score  # Convert diversity to MMR's lambda
                )
                logging.info(f"Search type: MMR (diversity={self.mmr_diversity_score}), retrieved {len(docs)} documents")
                
            elif search_type == 'similarity_score_threshold':
                # Filter results by minimum similarity score
                docs_with_scores = vectorstore.similarity_search_with_score(query, k=k*2)
                docs = [doc for doc, score in docs_with_scores if score >= self.score_threshold][:k]
                if len(docs) == 0:
                    logging.warning(f"No documents meet score threshold {self.score_threshold}, falling back to top {k}")
                    docs = vectorstore.similarity_search(query, k=k)
                logging.info(f"Search type: score_threshold ({self.score_threshold}), retrieved {len(docs)} documents")
                
            elif search_type == 'diverse':
                # Fetch more results and select diverse subset
                fetch_count = k * self.diverse_multiplier
                all_docs = vectorstore.similarity_search(query, k=fetch_count)
                
                # Simple diversity selection: pick documents that are dissimilar to each other
                if len(all_docs) <= k:
                    docs = all_docs
                else:
                    docs = [all_docs[0]]  # Start with most relevant
                    for doc in all_docs[1:]:
                        # Check if this doc is sufficiently different from selected docs
                        if len(docs) >= k:
                            break
                        # Simple diversity check: content length and unique keywords
                        is_diverse = True
                        for selected_doc in docs:
                            # If too similar in content, skip
                            if len(set(doc.page_content.split()) & set(selected_doc.page_content.split())) > len(doc.page_content.split()) * 0.7:
                                is_diverse = False
                                break
                        if is_diverse:
                            docs.append(doc)
                    
                    # Fill remaining slots if needed
                    while len(docs) < k and len(all_docs) > len(docs):
                        for doc in all_docs:
                            if doc not in docs:
                                docs.append(doc)
                                break
                                
                logging.info(f"Search type: diverse (multiplier={self.diverse_multiplier}), retrieved {len(docs)} from {len(all_docs)} candidates")
                
            elif search_type == 'rerank':
                # Retrieve more documents and rerank by relevance
                fetch_count = k * self.rerank_multiplier
                docs_with_scores = vectorstore.similarity_search_with_score(query, k=fetch_count)
                
                # Sort by score (lower is better in most vector DBs, but check your setup)
                # For Chroma with L2 distance, lower scores are better
                # For cosine similarity, higher scores are better
                # Let's assume we're getting relevance scores where higher is better after normalization
                docs_with_scores_sorted = sorted(docs_with_scores, key=lambda x: x[1], reverse=False)  # Lower L2 distance is better
                docs = [doc for doc, score in docs_with_scores_sorted[:k]]
                
                logging.info(f"Search type: rerank (multiplier={self.rerank_multiplier}), retrieved {len(docs)} from {len(docs_with_scores)} candidates")
                
            else:
                # Fallback to similarity search
                logging.warning(f"Unknown search type '{search_type}', falling back to similarity search")
                docs = vectorstore.similarity_search(query, k=k)
                
        except Exception as e:
            logging.error(f"Error in search type '{search_type}': {e}, falling back to similarity search")
            docs = vectorstore.similarity_search(query, k=k)
            
        return docs

    def _create_agent(self, prompt_template, examples):
        model = ChatOpenAI(model=self.model, base_url=self.base_url)

        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}")
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples
        )

        parser = StrOutputParser()

        final_prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_template),
            few_shot_prompt,
            ("human", "{input}")
        ])

        agent = final_prompt | model | parser
        return agent

    def shell_writing(self, commands, step):
        shell_script_path = os.path.join(self.output_dir, f"{self.id}_Step_{step}.sh")

        code_prefix = [
            'which python',
            'conda config --set show_channel_urls false',
            'conda config --add channels conda-forge',
            'conda config --add channels bioconda',
            'mkdir -p ./output/'+str(self.id)
        ]

        with open(shell_script_path, "w", encoding="utf-8") as file:
            # Write prefix commands first
            file.write("#!/bin/bash\n")
            for command in code_prefix:
                file.write(command + "\n")

            # Write actual shell commands
            for command in commands:
                file.write(f"{command}\n")
        return shell_script_path

    def _truncate_text(self, text, max_length):
        return text if len(text) <= max_length else text[:max_length] + '...'

    def save_progress(self, step_data, output_dir, file_name):
        file_name = f"{self.id}_{file_name}"
        file_path = os.path.join(output_dir, file_name)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Write data
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(step_data, file, indent=4)

    def load_progress(self, output_dir, file_name):
        file_name = f"{self.id}_{file_name}"
        file_path = os.path.join(output_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                step_data = json.load(file)
            return step_data
        return None

    def _get_output_files(self):
        output_files = []
        output_dir_path = os.path.join(self.output_dir, str(self.id))

        # Iterate through all files in output directory
        for root, dirs, files in os.walk(output_dir_path):
            for file in files:
                if file.endswith(('.json', '.sh', '.txt')):  # You can filter files based on their type
                    output_files.append(os.path.join(root, file))

        return output_files

    def execute_PLAN(self, goal, datalist):
        """
        Generate new PLAN, overwrite previous PLAN.json, and save old plan and step outputs to history.
        """
        plan_file_path = os.path.join(self.output_dir, "PLAN.json")
        existing_plan = self.load_progress(self.output_dir, "PLAN.json")
        print(existing_plan)
        print()
        if existing_plan:
            logging.info("existing PLAN found.")
        else:
            logging.info("No existing PLAN found. Proceeding to generate a new PLAN.")
        # Generate new PLAN
        logging.info("Generating a new PLAN.")

        related_docs = self._perform_search(self.vectorstore, goal, k=self.plan_k, search_type=self.plan_search_type)
        related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])
        logging.info(f"Related documents content: {related_docs_content}")
        # Build reference content: Use related document content as reference
        combined_reference = related_docs_content

        PLAN_input = {
            "input": json.dumps({
                "id": self.id,
                "goal": goal,
                "datalist": datalist,
                "related_docs": combined_reference
            })
        }
        PLAN_results = self.PLAN_agent.invoke(PLAN_input)
        print(PLAN_results)
        
        PLAN_results = Json_Format_Agent(
            PLAN_results, 
            self.api_key, 
            self.base_url,
            tool_model=self.tool_model,
            use_ollama=self.use_ollama,
            ollama_base_url=self.ollama_base_url,
            ollama_model=self.ollama_model
        )
        
        try:
            parsed_plan = json.loads(PLAN_results.strip().strip('"'))
            PLAN_results_dict = self.normalize_keys(parsed_plan)
        except json.JSONDecodeError:
            # 处理JSON解析错误
            print(f"Error parsing PLAN JSON: {PLAN_results}")
            return None
        
        # 保存PLAN并返回
        self.save_progress(PLAN_results_dict, self.output_dir, "PLAN.json")
        logging.info("Saved new PLAN.json.")
        
        logging.info("_____________________________________________________")
        logging.info(json.dumps(PLAN_results_dict, indent=4, ensure_ascii=False))
        logging.info("_____________________________________________________")
        
        return PLAN_results_dict

    def get_all_files_in_output_folder(self):
        """
        Get all file paths in output/{id} folder
        """
        output_folder = os.path.join(self.output_dir, self.id)
        if not os.path.exists(output_folder):
            print(f"Folder {output_folder} does not exist.")
            return []

        # Iterate through all files
        all_files = []
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        return all_files

    def execute_TASK(self, datalist):
        PLAN_results_dict = self.load_progress(self.output_dir, f"PLAN.json")
        PLAN_results_dict = self.normalize_keys(PLAN_results_dict)
        TASK_agent = self.TASK_agent
        step_datalist = datalist
        if self.excutor:
            DEBUG_agent = self.DEBUG_agent
        ids = self.id
        # Get all generated file paths and add them to step['input filename']
        
        all_output_files = self.get_all_files_in_output_folder()
        print(f"All files in output/{ids}: {all_output_files}")
        
        # 使用plan_data而不是PLAN_results_dict['plan']
        for i in range(1, len(PLAN_results_dict['plan']) + 1):
            print("Step:", i)
            self.check_stop()
            if self.stop_flag:
                break
            
            step = PLAN_results_dict['plan'][i - 1]
            if self.excutor:
                DEBUG_output_dict = self.load_progress(self.output_dir, f"DEBUG_Output_{i}.json")

                if DEBUG_output_dict and DEBUG_output_dict.get("stats", True):
                    print(f"Step {i} already completed. Continuing.")
                    step_datalist = DEBUG_output_dict['output_filename'] + step_datalist
                    continue

            related_docs = self._perform_search(self.vectorstore_tool, step['description'], k=self.task_k, search_type=self.task_search_type)

            # Concatenate full content as string, ensure not truncated
            related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])
            print(related_docs)
            # Add traversed file paths to step['input filename']
            additional_files = self.get_all_files_in_output_folder()
            step['input_filename'].extend(additional_files)

            self.check_stop()
            if self.stop_flag:
                break

            # print(step['input_filename'])

            generated_files = self._get_output_files()
            step['input_filename'].extend(generated_files)
            step['input_filename'] = list(set(step['input_filename']))  # Remove duplicates
            print(step['input_filename'])

            # Repeat Test count
            retry_count = 0
            # JSON error
            Json_Error = False

            while retry_count < self.repeat:
                # If DEBUG_output_dict exists and stats is false, execute script directly
                if DEBUG_output_dict and DEBUG_output_dict.get("stats") is False and retry_count==0:
                    TASK_results = DEBUG_output_dict.get("shell", "")  
                    PRE_DEBUG_output=[]      
                elif retry_count == 0 or Json_Error:
                    self.check_stop()
                    if self.stop_flag:
                        break
                    # extract data from datalist
                    # Assume step['input_filename'] already exists and is a list
                    new_input_filenames = [item.split(':')[0] for item in step_datalist]
                    # Update step['input_filename'], ensure no duplicate file paths
                    step['input_filename'] = list(set(step['input_filename'] + new_input_filenames))
                    # print(step['input_filename'])

                    TASK_input = {
                        "input": json.dumps({
                            "task": step,
                            "id": ids,
                            "related_docs": related_docs_content,  # Use related_docs_content
                        })
                    }
                    TASK_results = TASK_agent.invoke(TASK_input)
                    TASK_results = Json_Format_Agent(TASK_results,  self.api_key, self.base_url,tool_model=self.tool_model)


                    PRE_DEBUG_output = []
                    try:
                        TASK_results = json.loads(TASK_results)
                        TASK_results = TASK_results.get("shell", "")
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse TASK_results: {e}")
                        TASK_results = ""

                    # If not executed, skip subsequent steps directly
                    if not self.excutor:
                        shell_script_path = self.shell_writing(TASK_results, i)
                        break

                else:
                    TASK_results = DEBUG_output_dict.get("shell", "")

                # Write as sh script
                shell_script_path = self.shell_writing(TASK_results, i)
                # Execute script

                self.check_stop()
                if self.stop_flag:
                    break
                result = subprocess.run(["bash", shell_script_path], capture_output=True)#, text=True

                stdout_str = result.stdout.decode("utf-8", errors="replace")
                stderr_str = result.stderr.decode("utf-8", errors="replace")
                self.check_stop()
                if self.stop_flag:
                    break
                max_output_length = 5000  # Set maximum output character count

                result_stdout = stdout_str[:max_output_length] if len(stdout_str) > max_output_length else stdout_str
                result_stderr = stderr_str[:max_output_length] if len(stderr_str) > max_output_length else stderr_str


                DEBUG_input = {
                    "input": json.dumps({
                        "task": step,
                        "pre debug": PRE_DEBUG_output,
                        "result": result_stderr if result.returncode != 0 else result_stdout,
                        "related_docs": related_docs_content,
                        "id": ids,
                        "shell": TASK_results,
                    })
                }

                self.save_progress(DEBUG_input, self.output_dir, f"DEBUG_Input_{i}.json")
                DEBUG_output = DEBUG_agent.invoke(DEBUG_input)
                # Save previous input
                PRE_DEBUG_output.append(DEBUG_output)

                # Format
                DEBUG_output = Json_Format_Agent(DEBUG_output, self.api_key, self.base_url,tool_model=self.tool_model)

                try:
                    print("***************************************************************")
                    print(DEBUG_output)
                    print("***************************************************************")
                    DEBUG_output_dict = json.loads(DEBUG_output)
                    self.save_progress(DEBUG_output_dict, self.output_dir, f"DEBUG_Output_{i}.json")

                    print(DEBUG_output_dict.get("stats", False))
                    # Only perform checks if stats is True
                    if DEBUG_output_dict.get("stats", False):
                        # Add file verification using CheckAgent
                        debug_output_path = os.path.join(self.output_dir, f"{self.id}_DEBUG_Output_{i}.json")
                        check_results = self.check_agent.check_output_files(debug_output_path)
                        
                        # Reload the DEBUG output file as CheckAgent may have updated it
                        with open(debug_output_path, 'r', encoding='utf-8') as f:
                            DEBUG_output_dict = json.load(f)
                        
                        # If file verification passed
                        if check_results.get("stats", True):
                            # If we have new output filenames, update them
                            if check_results.get("output_filename"):
                                # Update the output_filename in DEBUG_output_dict
                                DEBUG_output_dict["output_filename"] = check_results.get("output_filename")
                                self.save_progress(DEBUG_output_dict, self.output_dir, f"DEBUG_Output_{i}.json")
                            
                            # Success - move to next step
                            previous_output_filenames = step['output_filename']
                            break
                        else:
                            # File verification failed, give DebugAgent another chance
                            DEBUG_input = {
                                "input": json.dumps({
                                    "task": step,
                                    "pre debug": [json.dumps(DEBUG_output_dict)],
                                    "result": f"File verification failed: {check_results.get('analysis', '')}"+result_stderr,
                                    "related_docs": related_docs_content,
                                    "id": ids,
                                    "shell": TASK_results,
                                })
                            }
                            
                            # Run DebugAgent again and parse result
                            DEBUG_output = DEBUG_agent.invoke(DEBUG_input)
                            DEBUG_output = Json_Format_Agent(DEBUG_output, self.api_key, self.base_url,tool_model=self.tool_model)
                            
                            try:
                                new_DEBUG_output_dict = json.loads(DEBUG_output)
                                # Update the DEBUG output file
                                DEBUG_output_dict = new_DEBUG_output_dict
                                self.save_progress(DEBUG_output_dict, self.output_dir, f"DEBUG_Output_{i}.json")
                            except json.JSONDecodeError:
                                logging.error(f"Error parsing DEBUG agent retry output for step {i}")
                            
                            # Check if DebugAgent fixed the issue
                            if DEBUG_output_dict.get("stats", False):
                                previous_output_filenames = step['output_filename']
                                break  # Success
                            else:
                                print(f"Step {i} failed: {DEBUG_output_dict.get('analyze', '')}")
                                print(f"File check analysis: {check_results.get('analysis', '')}")
                                print(f"Attempt {retry_count + 1}")
                                retry_count += 1
                    else:
                        print(f"Step {i} failed. Attempt {retry_count + 1}")
                        retry_count += 1
                except json.JSONDecodeError:
                    print(f"JSON Decode Error, retrying... Attempt {retry_count + 1}")
                    DEBUG_output_dict = {}
                    retry_count += 1
                    Json_Error = True

            if retry_count >= self.repeat:
                print(f"Step {i} failed after {self.repeat} retries. Moving to next step.")
                break
        
        return PLAN_results_dict

    def _filter_thinking_process(self, text):
        """
        Filter out <think></think> tags and their contents
        If not in ollama mode, return text directly
        
        Parameters:
        - text: Text to filter
        
        Returns:
        - Filtered text
        """
        if not self.use_ollama:
            return text
        
        import re
        # Use regex to remove <think>...</think> parts
        filtered_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return filtered_text
