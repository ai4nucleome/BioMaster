## api_reference.md

# Biomni API Reference

Comprehensive API documentation for the biomni framework.

## A1 Agent Class

The A1 class is the primary interface for interacting with biomni.

### Initialization

```python
from biomni.agent import A1

agent = A1(
    path: str,              # Path to data lake directory
    llm: str,               # LLM model identifier
    verbose: bool = True,   # Enable verbose logging
    mcp_config: str = None  # Path to MCP server configuration
)
```

**Parameters:**

- **`path`** (str, required) - Directory path for biomni data lake (~11GB). Data is automatically downloaded on first use if not present.

- **`llm`** (str, required) - LLM model identifier. Options include:
  - `'claude-sonnet-4-20250514'` - Recommended for balanced performance
  - `'claude-opus-4-20250514'` - Maximum capability
  - `'gpt-4'`, `'gpt-4-turbo'` - OpenAI models
  - `'gemini-2.0-flash-exp'` - Google Gemini
  - `'llama-3.3-70b-versatile'` - Via Groq
  - Custom model endpoints via provider configuration

- **`verbose`** (bool, optional, default=True) - Enable detailed logging of agent reasoning, tool use, and code execution.

- **`mcp_config`** (str, optional) - Path to MCP (Model Context Protocol) server configuration file for external tool integration.

**Example:**
```python
# Basic initialization
agent = A1(path='./biomni_data', llm='claude-sonnet-4-20250514')

# With MCP integration
agent = A1(
    path='./biomni_data',
    llm='claude-sonnet-4-20250514',
    mcp_config='./.biomni/mcp_config.json'
)
```

### Core Methods

#### `go(query: str) -> str`

Execute a biomedical research task autonomously.

```python
result = agent.go(query: str)
```

**Parameters:**
- **`query`** (str) - Natural language description of the biomedical task to execute

**Returns:**
- **`str`** - Final answer or analysis result from the agent

**Behavior:**
1. Decomposes query into executable sub-tasks
2. Retrieves relevant knowledge from integrated databases
3. Generates and executes Python code for analysis
4. Iterates on results until task completion
5. Returns final synthesized answer

**Example:**
```python
result = agent.go("""
Identify genes associated with Alzheimer's disease from GWAS data.
Perform pathway enrichment analysis on top hits.
""")
print(result)
```

#### `save_conversation_history(output_path: str, format: str = 'pdf')`

Save complete conversation history including task, reasoning, code, and results.

```python
agent.save_conversation_history(
    output_path: str,
    format: str = 'pdf'
)
```

**Parameters:**
- **`output_path`** (str) - File path for saved report
- **`format`** (str, optional, default='pdf') - Output format: `'pdf'`, `'html'`, or `'markdown'`

**Example:**
```python
agent.save_conversation_history('reports/alzheimers_gwas_analysis.pdf')
```

#### `reset()`

Reset agent state and clear conversation history.

```python
agent.reset()
```

Use when starting a new independent task to clear previous context.

**Example:**
```python
# Task 1
agent.go("Analyze dataset A")
agent.save_conversation_history("task1.pdf")

# Reset for fresh context
agent.reset()

# Task 2 - independent of Task 1
agent.go("Analyze dataset B")
```

### Configuration via default_config

Global configuration parameters accessible via `biomni.config.default_config`.

```python
from biomni.config import default_config

# LLM Configuration
default_config.llm = "claude-sonnet-4-20250514"
default_config.llm_temperature = 0.7

# Execution Parameters
default_config.timeout_seconds = 1200  # 20 minutes
default_config.max_iterations = 50     # Max reasoning loops
default_config.max_tokens = 4096       # Max tokens per LLM call

# Code Execution
default_config.enable_code_execution = True
default_config.sandbox_mode = False    # Enable for restricted execution

# Data and Caching
default_config.data_cache_dir = "./biomni_cache"
default_config.enable_caching = True
```

**Key Parameters:**

- **`timeout_seconds`** (int, default=1200) - Maximum time for task execution. Increase for complex analyses.

- **`max_iterations`** (int, default=50) - Maximum agent reasoning loops. Prevents infinite loops.

- **`enable_code_execution`** (bool, default=True) - Allow agent to execute generated code. Disable for code generation only.

- **`sandbox_mode`** (bool, default=False) - Enable sandboxed code execution (requires additional setup).

## BiomniEval1 Evaluation Framework

Framework for benchmarking agent performance on biomedical tasks.

### Initialization

```python
from biomni.eval import BiomniEval1

evaluator = BiomniEval1(
    dataset_path: str = None,  # Path to evaluation dataset
    metrics: list = None        # Evaluation metrics to compute
)
```

**Example:**
```python
evaluator = BiomniEval1()
```

### Methods

#### `evaluate(task_type: str, instance_id: str, answer: str) -> float`

Evaluate agent answer against ground truth.

```python
score = evaluator.evaluate(
    task_type: str,     # Task category
    instance_id: str,   # Specific task instance
    answer: str         # Agent-generated answer
)
```

**Parameters:**
- **`task_type`** (str) - Task category: `'crispr_design'`, `'scrna_analysis'`, `'gwas_interpretation'`, `'drug_admet'`, `'clinical_diagnosis'`
- **`instance_id`** (str) - Unique identifier for task instance from dataset
- **`answer`** (str) - Agent's answer to evaluate

**Returns:**
- **`float`** - Evaluation score (0.0 to 1.0)

**Example:**
```python
# Generate answer
result = agent.go("Design CRISPR screen for autophagy genes")

# Evaluate
score = evaluator.evaluate(
    task_type='crispr_design',
    instance_id='autophagy_001',
    answer=result
)
print(f"Score: {score:.2f}")
```

#### `load_dataset() -> dict`

Load the Biomni-Eval1 benchmark dataset.

```python
dataset = evaluator.load_dataset()
```

**Returns:**
- **`dict`** - Dictionary with task instances organized by task type

**Example:**
```python
dataset = evaluator.load_dataset()

for task_type, instances in dataset.items():
    print(f"{task_type}: {len(instances)} instances")
```

#### `run_benchmark(agent: A1, task_types: list = None) -> dict`

Run full benchmark evaluation on agent.

```python
results = evaluator.run_benchmark(
    agent: A1,
    task_types: list = None  # Specific task types or None for all
)
```

**Returns:**
- **`dict`** - Results with scores, timing, and detailed metrics per task

**Example:**
```python
results = evaluator.run_benchmark(
    agent=agent,
    task_types=['crispr_design', 'scrna_analysis']
)

print(f"Overall accuracy: {results['mean_score']:.2f}")
print(f"Average time: {results['mean_time']:.1f}s")
```

## Data Lake API

Access integrated biomedical databases programmatically.

### Gene Database Queries

```python
from biomni.data import GeneDB

gene_db = GeneDB(path='./biomni_data')

# Query gene information
gene_info = gene_db.get_gene('BRCA1')
# Returns: {'symbol': 'BRCA1', 'name': '...', 'function': '...', ...}

# Search genes by pathway
pathway_genes = gene_db.search_by_pathway('DNA repair')
# Returns: List of gene symbols in pathway

# Get gene interactions
interactions = gene_db.get_interactions('TP53')
# Returns: List of interacting genes with interaction types
```

### Protein Structure Access

```python
from biomni.data import ProteinDB

protein_db = ProteinDB(path='./biomni_data')

# Get AlphaFold structure
structure = protein_db.get_structure('P38398')  # BRCA1 UniProt ID
# Returns: Path to PDB file or structure object

# Search PDB database
pdb_entries = protein_db.search_pdb('kinase', resolution_max=2.5)
# Returns: List of PDB IDs matching criteria
```

### Clinical Data Access

```python
from biomni.data import ClinicalDB

clinical_db = ClinicalDB(path='./biomni_data')

# Query ClinVar variants
variant_info = clinical_db.get_variant('rs429358')  # APOE4 variant
# Returns: {'significance': '...', 'disease': '...', 'frequency': ...}

# Search OMIM for disease
disease_info = clinical_db.search_omim('Alzheimer')
# Returns: List of OMIM entries with gene associations
```

### Literature Search

```python
from biomni.data import LiteratureDB

lit_db = LiteratureDB(path='./biomni_data')

# Search PubMed abstracts
papers = lit_db.search('CRISPR screening cancer', max_results=10)
# Returns: List of paper dictionaries with titles, abstracts, PMIDs

# Get citations for paper
citations = lit_db.get_citations('PMID:12345678')
# Returns: List of citing papers
```

## MCP Server Integration

Extend biomni with external tools via Model Context Protocol.

### Configuration Format

Create `.biomni/mcp_config.json`:

```json
{
  "servers": {
    "fda-drugs": {
      "command": "python",
      "args": ["-m", "mcp_server_fda"],
      "env": {
        "FDA_API_KEY": "${FDA_API_KEY}"
      }
    },
    "web-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### Using MCP Tools in Tasks

```python
# Initialize with MCP config
agent = A1(
    path='./data',
    llm='claude-sonnet-4-20250514',
    mcp_config='./.biomni/mcp_config.json'
)

# Agent can now use MCP tools automatically
result = agent.go("""
Search for FDA-approved drugs targeting EGFR.
Get their approval dates and indications.
""")
# Agent uses fda-drugs MCP server automatically
```

## Error Handling

Common exceptions and handling strategies:

```python
from biomni.exceptions import (
    BiomniException,
    LLMError,
    CodeExecutionError,
    DataNotFoundError,
    TimeoutError
)

try:
    result = agent.go("Complex biomedical task")
except TimeoutError:
    # Task exceeded timeout_seconds
    print("Task timed out. Consider increasing timeout.")
    default_config.timeout_seconds = 3600
except CodeExecutionError as e:
    # Generated code failed to execute
    print(f"Code execution error: {e}")
    # Review generated code in conversation history
except DataNotFoundError:
    # Required data not in data lake
    print("Data not found. Ensure data lake is downloaded.")
except LLMError as e:
    # LLM API error
    print(f"LLM error: {e}")
    # Check API keys and rate limits
```

## Best Practices

### Efficient API Usage

1. **Reuse agent instances** for related tasks to maintain context
2. **Set appropriate timeouts** based on task complexity
3. **Use caching** to avoid redundant data downloads
4. **Monitor iterations** to detect reasoning loops early

### Production Deployment

```python
from biomni.agent import A1
from biomni.config import default_config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Production settings
default_config.timeout_seconds = 3600
default_config.max_iterations = 100
default_config.sandbox_mode = True  # Enable sandboxing

# Initialize with error handling
try:
    agent = A1(path='/data/biomni', llm='claude-sonnet-4-20250514')
    result = agent.go(task_query)
    agent.save_conversation_history(f'reports/{task_id}.pdf')
except Exception as e:
    logging.error(f"Task {task_id} failed: {e}")
    # Handle failure appropriately
```

### Memory Management

For large-scale analyses:

```python
# Process datasets in chunks
chunk_results = []
for chunk in dataset_chunks:
    agent.reset()  # Clear memory between chunks
    result = agent.go(f"Analyze chunk: {chunk}")
    chunk_results.append(result)

# Combine results
final_result = combine_results(chunk_results)
```

---

## llm_providers.md

# LLM Provider Configuration

Comprehensive guide for configuring different LLM providers with biomni.

## Overview

Biomni supports multiple LLM providers for flexible deployment across different infrastructure and cost requirements. The framework abstracts provider differences through a unified interface.

## Supported Providers

1. **Anthropic Claude** (Recommended)
2. **OpenAI**
3. **Azure OpenAI**
4. **Google Gemini**
5. **Groq**
6. **AWS Bedrock**
7. **Custom Endpoints**

## Anthropic Claude

**Recommended for:** Best balance of reasoning quality, speed, and biomedical knowledge.

### Setup

```bash
# Set API key
export ANTHROPIC_API_KEY="sk-ant-..."

# Or in .env file
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### Available Models

```python
from biomni.agent import A1

# Sonnet 4 - Balanced performance (recommended)
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

# Opus 4 - Maximum capability
agent = A1(path='./data', llm='claude-opus-4-20250514')

# Haiku 4 - Fast and economical
agent = A1(path='./data', llm='claude-haiku-4-20250514')
```

### Configuration Options

```python
from biomni.config import default_config

default_config.llm = "claude-sonnet-4-20250514"
default_config.llm_temperature = 0.7
default_config.max_tokens = 4096
default_config.anthropic_api_key = "sk-ant-..."  # Or use env var
```

**Model Characteristics:**

| Model | Best For | Speed | Cost | Reasoning Quality |
|-------|----------|-------|------|-------------------|
| Opus 4 | Complex multi-step analyses | Slower | High | Highest |
| Sonnet 4 | General biomedical tasks | Fast | Medium | High |
| Haiku 4 | Simple queries, bulk processing | Fastest | Low | Good |

## OpenAI

**Recommended for:** Established infrastructure, GPT-4 optimization.

### Setup

```bash
export OPENAI_API_KEY="sk-..."
```

### Available Models

```python
# GPT-4 Turbo
agent = A1(path='./data', llm='gpt-4-turbo')

# GPT-4
agent = A1(path='./data', llm='gpt-4')

# GPT-4o
agent = A1(path='./data', llm='gpt-4o')
```

### Configuration

```python
from biomni.config import default_config

default_config.llm = "gpt-4-turbo"
default_config.openai_api_key = "sk-..."
default_config.openai_organization = "org-..."  # Optional
default_config.llm_temperature = 0.7
```

**Considerations:**
- GPT-4 Turbo recommended for cost-effectiveness
- May require additional biomedical context for specialized tasks
- Rate limits vary by account tier

## Azure OpenAI

**Recommended for:** Enterprise deployments, data residency requirements.

### Setup

```bash
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export AZURE_OPENAI_API_VERSION="2024-02-01"
```

### Configuration

```python
from biomni.config import default_config

default_config.llm = "azure-gpt-4"
default_config.azure_openai_api_key = "..."
default_config.azure_openai_endpoint = "https://your-resource.openai.azure.com/"
default_config.azure_openai_deployment_name = "gpt-4"
default_config.azure_openai_api_version = "2024-02-01"
```

### Usage

```python
agent = A1(path='./data', llm='azure-gpt-4')
```

**Deployment Notes:**
- Requires Azure OpenAI Service provisioning
- Deployment names set during Azure resource creation
- API versions periodically updated by Microsoft

## Google Gemini

**Recommended for:** Google Cloud integration, multimodal tasks.

### Setup

```bash
export GOOGLE_API_KEY="..."
```

### Available Models

```python
# Gemini 2.0 Flash (recommended)
agent = A1(path='./data', llm='gemini-2.0-flash-exp')

# Gemini Pro
agent = A1(path='./data', llm='gemini-pro')
```

### Configuration

```python
from biomni.config import default_config

default_config.llm = "gemini-2.0-flash-exp"
default_config.google_api_key = "..."
default_config.llm_temperature = 0.7
```

**Features:**
- Native multimodal support (text, images, code)
- Fast inference
- Competitive pricing

## Groq

**Recommended for:** Ultra-fast inference, cost-sensitive applications.

### Setup

```bash
export GROQ_API_KEY="gsk_..."
```

### Available Models

```python
# Llama 3.3 70B
agent = A1(path='./data', llm='llama-3.3-70b-versatile')

# Mixtral 8x7B
agent = A1(path='./data', llm='mixtral-8x7b-32768')
```

### Configuration

```python
from biomni.config import default_config

default_config.llm = "llama-3.3-70b-versatile"
default_config.groq_api_key = "gsk_..."
```

**Characteristics:**
- Extremely fast inference via custom hardware
- Open-source model options
- Limited context windows for some models

## AWS Bedrock

**Recommended for:** AWS infrastructure, compliance requirements.

### Setup

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

### Available Models

```python
# Claude via Bedrock
agent = A1(path='./data', llm='bedrock-claude-sonnet-4')

# Llama via Bedrock
agent = A1(path='./data', llm='bedrock-llama-3-70b')
```

### Configuration

```python
from biomni.config import default_config

default_config.llm = "bedrock-claude-sonnet-4"
default_config.aws_access_key_id = "..."
default_config.aws_secret_access_key = "..."
default_config.aws_region = "us-east-1"
```

**Requirements:**
- AWS account with Bedrock access enabled
- Model access requested through AWS console
- IAM permissions configured for Bedrock APIs

## Custom Endpoints

**Recommended for:** Self-hosted models, custom infrastructure.

### Configuration

```python
from biomni.config import default_config

default_config.llm = "custom"
default_config.custom_llm_endpoint = "http://localhost:8000/v1/chat/completions"
default_config.custom_llm_api_key = "..."  # If required
default_config.custom_llm_model_name = "llama-3-70b"
```

### Usage

```python
agent = A1(path='./data', llm='custom')
```

**Endpoint Requirements:**
- Must implement OpenAI-compatible chat completions API
- Support for function/tool calling recommended
- JSON response format

**Example with vLLM:**

```bash
# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3-70b-chat \
    --port 8000

# Configure biomni
export CUSTOM_LLM_ENDPOINT="http://localhost:8000/v1/chat/completions"
```

## Model Selection Guidelines

### By Task Complexity

**Simple queries** (gene lookup, basic calculations):
- Claude Haiku 4
- Gemini 2.0 Flash
- Groq Llama 3.3 70B

**Moderate tasks** (data analysis, literature search):
- Claude Sonnet 4 (recommended)
- GPT-4 Turbo
- Gemini 2.0 Flash

**Complex analyses** (multi-step reasoning, novel insights):
- Claude Opus 4 (recommended)
- GPT-4
- Claude Sonnet 4

### By Cost Sensitivity

**Budget-conscious:**
1. Groq (fastest, cheapest)
2. Claude Haiku 4
3. Gemini 2.0 Flash

**Balanced:**
1. Claude Sonnet 4 (recommended)
2. GPT-4 Turbo
3. Gemini Pro

**Quality-first:**
1. Claude Opus 4
2. GPT-4
3. Claude Sonnet 4

### By Infrastructure

**Cloud-agnostic:**
- Anthropic Claude (direct API)
- OpenAI (direct API)

**AWS ecosystem:**
- AWS Bedrock (Claude, Llama)

**Azure ecosystem:**
- Azure OpenAI Service

**Google Cloud:**
- Google Gemini

**On-premises:**
- Custom endpoints with self-hosted models

## Performance Comparison

Based on Biomni-Eval1 benchmark:

| Provider | Model | Avg Score | Avg Time (s) | Cost/1K tasks |
|----------|-------|-----------|--------------|---------------|
| Anthropic | Opus 4 | 0.89 | 45 | $120 |
| Anthropic | Sonnet 4 | 0.85 | 28 | $45 |
| OpenAI | GPT-4 Turbo | 0.82 | 35 | $55 |
| Google | Gemini 2.0 Flash | 0.78 | 22 | $25 |
| Groq | Llama 3.3 70B | 0.73 | 12 | $8 |
| Anthropic | Haiku 4 | 0.75 | 15 | $15 |

*Note: Costs are approximate and vary by usage patterns.*

## Troubleshooting

### API Key Issues

```python
# Verify key is set
import os
print(os.getenv('ANTHROPIC_API_KEY'))

# Or check in Python
from biomni.config import default_config
print(default_config.anthropic_api_key)
```

### Rate Limiting

```python
from biomni.config import default_config

# Add retry logic
default_config.max_retries = 5
default_config.retry_delay = 10  # seconds

# Reduce concurrency
default_config.max_concurrent_requests = 1
```

### Timeout Errors

```python
# Increase timeout for slow providers
default_config.llm_timeout = 120  # seconds

# Or switch to faster model
default_config.llm = "claude-sonnet-4-20250514"  # Fast and capable
```

### Model Not Available

```bash
# For Bedrock: Enable model access in AWS console
aws bedrock list-foundation-models --region us-east-1

# For Azure: Check deployment name
az cognitiveservices account deployment list \
    --name your-resource-name \
    --resource-group your-rg
```

## Best Practices

### Cost Optimization

1. **Use appropriate models** - Don't use Opus 4 for simple queries
2. **Enable caching** - Reuse data lake access across tasks
3. **Batch processing** - Group similar tasks together
4. **Monitor usage** - Track API costs per task type

```python
from biomni.config import default_config

# Enable response caching
default_config.enable_caching = True
default_config.cache_ttl = 3600  # 1 hour
```

### Multi-Provider Strategy

```python
def get_agent_for_task(task_complexity):
    """Select provider based on task requirements"""
    if task_complexity == 'simple':
        return A1(path='./data', llm='claude-haiku-4-20250514')
    elif task_complexity == 'moderate':
        return A1(path='./data', llm='claude-sonnet-4-20250514')
    else:
        return A1(path='./data', llm='claude-opus-4-20250514')

# Use appropriate model
agent = get_agent_for_task('moderate')
result = agent.go(task_query)
```

### Fallback Configuration

```python
from biomni.exceptions import LLMError

def execute_with_fallback(task_query):
    """Try multiple providers if primary fails"""
    providers = [
        'claude-sonnet-4-20250514',
        'gpt-4-turbo',
        'gemini-2.0-flash-exp'
    ]

    for llm in providers:
        try:
            agent = A1(path='./data', llm=llm)
            return agent.go(task_query)
        except LLMError as e:
            print(f"{llm} failed: {e}")
            continue

    raise Exception("All providers failed")
```

## Provider-Specific Tips

### Anthropic Claude
- Best for complex biomedical reasoning
- Use Sonnet 4 for most tasks
- Reserve Opus 4 for novel research questions

### OpenAI
- Add system prompts with biomedical context for better results
- Use JSON mode for structured outputs
- Monitor token usage - context window limits

### Azure OpenAI
- Provision deployments in regions close to data
- Use managed identity for secure authentication
- Monitor quota consumption in Azure portal

### Google Gemini
- Leverage multimodal capabilities for image-based tasks
- Use streaming for long-running analyses
- Consider Gemini Pro for production workloads

### Groq
- Ideal for high-throughput screening tasks
- Limited reasoning depth vs. Claude/GPT-4
- Best for well-defined, structured problems

### AWS Bedrock
- Use IAM roles instead of access keys when possible
- Enable CloudWatch logging for debugging
- Monitor cross-region latency

---

## use_cases.md

# Biomni Use Cases and Examples

Comprehensive examples demonstrating biomni across biomedical research domains.

## Table of Contents

1. [CRISPR Screening and Gene Editing](#crispr-screening-and-gene-editing)
2. [Single-Cell RNA-seq Analysis](#single-cell-rna-seq-analysis)
3. [Drug Discovery and ADMET](#drug-discovery-and-admet)
4. [GWAS and Genetic Analysis](#gwas-and-genetic-analysis)
5. [Clinical Genomics and Diagnostics](#clinical-genomics-and-diagnostics)
6. [Protein Structure and Function](#protein-structure-and-function)
7. [Literature and Knowledge Synthesis](#literature-and-knowledge-synthesis)
8. [Multi-Omics Integration](#multi-omics-integration)

---

## CRISPR Screening and Gene Editing

### Example 1: Genome-Wide CRISPR Screen Design

**Task:** Design a CRISPR knockout screen to identify genes regulating autophagy.

```python
from biomni.agent import A1

agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Design a genome-wide CRISPR knockout screen to identify genes regulating
autophagy in HEK293 cells.

Requirements:
1. Generate comprehensive sgRNA library targeting all protein-coding genes
2. Design 4 sgRNAs per gene with optimal on-target and minimal off-target scores
3. Include positive controls (known autophagy regulators: ATG5, BECN1, ULK1)
4. Include negative controls (non-targeting sgRNAs)
5. Prioritize genes based on:
   - Existing autophagy pathway annotations
   - Protein-protein interactions with known autophagy factors
   - Expression levels in HEK293 cells
6. Output sgRNA sequences, scores, and gene prioritization rankings

Provide analysis as Python code and interpret results.
""")

agent.save_conversation_history("autophagy_screen_design.pdf")
```

**Expected Output:**
- sgRNA library with ~80,000 guides (4 per gene × ~20,000 genes)
- On-target and off-target scores for each sgRNA
- Prioritized gene list based on pathway enrichment
- Quality control metrics for library design

### Example 2: CRISPR Off-Target Prediction

```python
result = agent.go("""
Analyze potential off-target effects for this sgRNA sequence:
GCTGAAGATCCAGTTCGATG

Tasks:
1. Identify all genomic locations with ≤3 mismatches
2. Score each potential off-target site
3. Assess likelihood of cleavage at off-target sites
4. Recommend whether sgRNA is suitable for use
5. If unsuitable, suggest alternative sgRNAs for the same gene
""")
```

### Example 3: Screen Hit Analysis

```python
result = agent.go("""
Analyze CRISPR screen results from autophagy phenotype screen.

Input file: screen_results.csv
Columns: sgRNA_ID, gene, log2_fold_change, p_value, FDR

Tasks:
1. Identify significant hits (FDR < 0.05, |LFC| > 1.5)
2. Perform gene ontology enrichment on hit genes
3. Map hits to known autophagy pathways
4. Identify novel candidates not previously linked to autophagy
5. Predict functional relationships between hit genes
6. Generate visualization of hit genes in pathway context
""")
```

---

## Single-Cell RNA-seq Analysis

### Example 1: Cell Type Annotation

**Task:** Analyze single-cell RNA-seq data and annotate cell populations.

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Analyze single-cell RNA-seq dataset from human PBMC sample.

File: pbmc_data.h5ad (10X Genomics format)

Workflow:
1. Quality control:
   - Filter cells with <200 or >5000 detected genes
   - Remove cells with >20% mitochondrial content
   - Filter genes detected in <3 cells

2. Normalization and preprocessing:
   - Normalize to 10,000 reads per cell
   - Log-transform
   - Identify highly variable genes
   - Scale data

3. Dimensionality reduction:
   - PCA (50 components)
   - UMAP visualization

4. Clustering:
   - Leiden algorithm with resolution=0.8
   - Identify cluster markers (Wilcoxon rank-sum test)

5. Cell type annotation:
   - Annotate clusters using marker genes:
     * T cells (CD3D, CD3E)
     * B cells (CD79A, MS4A1)
     * NK cells (GNLY, NKG7)
     * Monocytes (CD14, LYZ)
     * Dendritic cells (FCER1A, CST3)

6. Generate UMAP plots with annotations and export results
""")

agent.save_conversation_history("pbmc_scrna_analysis.pdf")
```

### Example 2: Differential Expression Analysis

```python
result = agent.go("""
Perform differential expression analysis between conditions in scRNA-seq data.

Data: pbmc_treated_vs_control.h5ad
Conditions: treated (drug X) vs control

Tasks:
1. Identify differentially expressed genes for each cell type
2. Use statistical tests appropriate for scRNA-seq (MAST or Wilcoxon)
3. Apply multiple testing correction (Benjamini-Hochberg)
4. Threshold: |log2FC| > 0.5, adjusted p < 0.05
5. Perform pathway enrichment on DE genes per cell type
6. Identify cell-type-specific drug responses
7. Generate volcano plots and heatmaps
""")
```

### Example 3: Trajectory Analysis

```python
result = agent.go("""
Perform pseudotime trajectory analysis on differentiation dataset.

Data: hematopoiesis_scrna.h5ad
Starting population: Hematopoietic stem cells (HSCs)

Analysis:
1. Subset to hematopoietic lineages
2. Compute diffusion map or PAGA for trajectory inference
3. Order cells along pseudotime
4. Identify genes with dynamic expression along trajectory
5. Cluster genes by expression patterns
6. Map trajectories to known differentiation pathways
7. Visualize key transcription factors driving differentiation
""")
```

---

## Drug Discovery and ADMET

### Example 1: ADMET Property Prediction

**Task:** Predict ADMET properties for drug candidates.

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Predict ADMET properties for these drug candidates:

Compounds (SMILES format):
1. CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5
2. CN1CCN(CC1)C2=C(C=C3C(=C2)N=CN=C3NC4=CC=C(C=C4)F)OC
3. CC(C)(C)NC(=O)N(CC1=CC=CC=C1)C2CCN(CC2)C(=O)C3=CC4=C(C=C3)OCO4

For each compound, predict:

**Absorption:**
- Caco-2 permeability (cm/s)
- Human intestinal absorption (HIA %)
- Oral bioavailability

**Distribution:**
- Plasma protein binding (%)
- Blood-brain barrier penetration (BBB+/-)
- Volume of distribution (L/kg)

**Metabolism:**
- CYP450 substrate/inhibitor predictions (2D6, 3A4, 2C9, 2C19)
- Metabolic stability (T1/2)

**Excretion:**
- Clearance (mL/min/kg)
- Half-life (hours)

**Toxicity:**
- hERG IC50 (cardiotoxicity risk)
- Hepatotoxicity prediction
- Ames mutagenicity
- LD50 estimates

Provide predictions with confidence scores and flag any red flags.
""")

agent.save_conversation_history("admet_predictions.pdf")
```

### Example 2: Target Identification

```python
result = agent.go("""
Identify potential protein targets for Alzheimer's disease drug development.

Tasks:
1. Query GWAS data for Alzheimer's-associated genes
2. Identify genes with druggable domains (kinases, GPCRs, ion channels, etc.)
3. Check for brain expression patterns
4. Assess disease relevance via literature mining
5. Evaluate existing chemical probe availability
6. Rank targets by:
   - Genetic evidence strength
   - Druggability
   - Lack of existing therapies
7. Suggest target validation experiments
""")
```

### Example 3: Virtual Screening

```python
result = agent.go("""
Perform virtual screening for EGFR kinase inhibitors.

Database: ZINC15 lead-like subset (~6M compounds)
Target: EGFR kinase domain (PDB: 1M17)

Workflow:
1. Prepare protein structure (remove waters, add hydrogens)
2. Define binding pocket (based on erlotinib binding site)
3. Generate pharmacophore model from known EGFR inhibitors
4. Filter ZINC database by:
   - Molecular weight: 200-500 Da
   - LogP: 0-5
   - Lipinski's rule of five
   - Pharmacophore match
5. Dock top 10,000 compounds
6. Score by docking energy and predicted binding affinity
7. Select top 100 for further analysis
8. Predict ADMET properties for top hits
9. Recommend top 10 compounds for experimental validation
""")
```

---

## GWAS and Genetic Analysis

### Example 1: GWAS Summary Statistics Analysis

**Task:** Interpret GWAS results and identify causal genes.

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Analyze GWAS summary statistics for Type 2 Diabetes.

Input file: t2d_gwas_summary.txt
Columns: CHR, BP, SNP, P, OR, BETA, SE, A1, A2

Analysis steps:
1. Identify genome-wide significant variants (P < 5e-8)
2. Perform LD clumping to identify independent signals
3. Map variants to genes using:
   - Nearest gene
   - eQTL databases (GTEx)
   - Hi-C chromatin interactions
4. Prioritize causal genes using multiple evidence:
   - Fine-mapping scores
   - Coding variant consequences
   - Gene expression in relevant tissues (pancreas, liver, adipose)
   - Pathway enrichment
5. Identify druggable targets among causal genes
6. Compare with known T2D genes and highlight novel associations
7. Generate Manhattan plot, QQ plot, and gene prioritization table
""")

agent.save_conversation_history("t2d_gwas_analysis.pdf")
```

### Example 2: Polygenic Risk Score

```python
result = agent.go("""
Develop and validate polygenic risk score (PRS) for coronary artery disease (CAD).

Training GWAS: CAD_discovery_summary_stats.txt (N=180,000)
Validation cohort: CAD_validation_genotypes.vcf (N=50,000)

Tasks:
1. Select variants for PRS using p-value thresholding (P < 1e-5)
2. Perform LD clumping (r² < 0.1, 500kb window)
3. Calculate PRS weights from GWAS betas
4. Compute PRS for validation cohort individuals
5. Evaluate PRS performance:
   - AUC for CAD case/control discrimination
   - Odds ratios across PRS deciles
   - Compare to traditional risk factors (age, sex, BMI, smoking)
6. Assess PRS calibration and create risk stratification plot
7. Identify high-risk individuals (top 5% PRS)
""")
```

### Example 3: Variant Pathogenicity Prediction

```python
result = agent.go("""
Predict pathogenicity of rare coding variants in candidate disease genes.

Variants (VCF format):
- chr17:41234451:A>G (BRCA1 p.Arg1347Gly)
- chr2:179428448:C>T (TTN p.Trp13579*)
- chr7:117188679:G>A (CFTR p.Gly542Ser)

For each variant, assess:
1. In silico predictions (SIFT, PolyPhen2, CADD, REVEL)
2. Population frequency (gnomAD)
3. Evolutionary conservation (PhyloP, PhastCons)
4. Protein structure impact (using AlphaFold structures)
5. Functional domain location
6. ClinVar annotations (if available)
7. Literature evidence
8. ACMG/AMP classification criteria

Provide pathogenicity classification (benign, likely benign, VUS, likely pathogenic, pathogenic) with supporting evidence.
""")
```

---

## Clinical Genomics and Diagnostics

### Example 1: Rare Disease Diagnosis

**Task:** Diagnose rare genetic disease from whole exome sequencing.

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Analyze whole exome sequencing (WES) data for rare disease diagnosis.

Patient phenotypes (HPO terms):
- HP:0001250 (Seizures)
- HP:0001249 (Intellectual disability)
- HP:0001263 (Global developmental delay)
- HP:0001252 (Hypotonia)

VCF file: patient_trio.vcf (proband + parents)

Analysis workflow:
1. Variant filtering:
   - Quality filters (QUAL > 30, DP > 10, GQ > 20)
   - Frequency filters (gnomAD AF < 0.01)
   - Functional impact (missense, nonsense, frameshift, splice site)

2. Inheritance pattern analysis:
   - De novo variants
   - Autosomal recessive (compound het, homozygous)
   - X-linked

3. Phenotype-driven prioritization:
   - Match candidate genes to HPO terms
   - Use HPO-gene associations
   - Check gene expression in relevant tissues (brain)

4. Variant pathogenicity assessment:
   - In silico predictions
   - ACMG classification
   - Literature evidence

5. Generate diagnostic report with:
   - Top candidate variants
   - Supporting evidence
   - Functional validation suggestions
   - Genetic counseling recommendations
""")

agent.save_conversation_history("rare_disease_diagnosis.pdf")
```

### Example 2: Cancer Genomics Analysis

```python
result = agent.go("""
Analyze tumor-normal paired sequencing for cancer genomics.

Files:
- tumor_sample.vcf (somatic variants)
- tumor_rnaseq.bam (gene expression)
- tumor_cnv.seg (copy number variants)

Analysis:
1. Identify driver mutations:
   - Known cancer genes (COSMIC, OncoKB)
   - Recurrent hotspot mutations
   - Truncating mutations in tumor suppressors

2. Analyze mutational signatures:
   - Decompose signatures (COSMIC signatures)
   - Identify mutagenic processes

3. Copy number analysis:
   - Identify amplifications and deletions
   - Focal vs. arm-level events
   - Assess oncogene amplifications and TSG deletions

4. Gene expression analysis:
   - Identify outlier gene expression
   - Fusion transcript detection
   - Pathway dysregulation

5. Therapeutic implications:
   - Match alterations to FDA-approved therapies
   - Identify clinical trial opportunities
   - Predict response to targeted therapies

6. Generate precision oncology report
""")
```

### Example 3: Pharmacogenomics

```python
result = agent.go("""
Generate pharmacogenomics report for patient genotype data.

VCF file: patient_pgx.vcf

Analyze variants affecting drug metabolism:

**CYP450 genes:**
- CYP2D6 (affects ~25% of drugs)
- CYP2C19 (clopidogrel, PPIs, antidepressants)
- CYP2C9 (warfarin, NSAIDs)
- CYP3A5 (tacrolimus, immunosuppressants)

**Drug transporter genes:**
- SLCO1B1 (statin myopathy risk)
- ABCB1 (P-glycoprotein)

**Drug targets:**
- VKORC1 (warfarin dosing)
- DPYD (fluoropyrimidine toxicity)
- TPMT (thiopurine toxicity)

For each gene:
1. Determine diplotype (*1/*1, *1/*2, etc.)
2. Assign metabolizer phenotype (PM, IM, NM, RM, UM)
3. Provide dosing recommendations using CPIC/PharmGKB guidelines
4. Flag high-risk drug-gene interactions
5. Suggest alternative medications if needed

Generate patient-friendly report with actionable recommendations.
""")
```

---

## Protein Structure and Function

### Example 1: AlphaFold Structure Analysis

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Analyze AlphaFold structure prediction for novel protein.

Protein: Hypothetical protein ABC123 (UniProt: Q9XYZ1)

Tasks:
1. Retrieve AlphaFold structure from database
2. Assess prediction quality:
   - pLDDT scores per residue
   - Identify high-confidence regions (pLDDT > 90)
   - Flag low-confidence regions (pLDDT < 50)

3. Structural analysis:
   - Identify domains using structural alignment
   - Predict fold family
   - Identify secondary structure elements

4. Functional prediction:
   - Search for structural homologs in PDB
   - Identify conserved functional sites
   - Predict binding pockets
   - Suggest possible ligands/substrates

5. Variant impact analysis:
   - Map disease-associated variants to structure
   - Predict structural consequences
   - Identify variants affecting binding sites

6. Generate PyMOL visualization scripts highlighting key features
""")

agent.save_conversation_history("alphafold_analysis.pdf")
```

### Example 2: Protein-Protein Interaction Prediction

```python
result = agent.go("""
Predict and analyze protein-protein interactions for autophagy pathway.

Query proteins: ATG5, ATG12, ATG16L1

Analysis:
1. Retrieve known interactions from:
   - STRING database
   - BioGRID
   - IntAct
   - Literature mining

2. Predict novel interactions using:
   - Structural modeling (AlphaFold-Multimer)
   - Coexpression analysis
   - Phylogenetic profiling

3. Analyze interaction interfaces:
   - Identify binding residues
   - Assess interface properties (area, hydrophobicity)
   - Predict binding affinity

4. Functional analysis:
   - Map interactions to autophagy pathway steps
   - Identify regulatory interactions
   - Predict complex stoichiometry

5. Therapeutic implications:
   - Identify druggable interfaces
   - Suggest peptide inhibitors
   - Design disruption strategies

Generate network visualization and interaction details.
""")
```

---

## Literature and Knowledge Synthesis

### Example 1: Systematic Literature Review

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Perform systematic literature review on CRISPR base editing applications.

Search query: "CRISPR base editing" OR "base editor" OR "CBE" OR "ABE"
Date range: 2016-2025

Tasks:
1. Search PubMed and retrieve relevant abstracts
2. Filter for original research articles
3. Extract key information:
   - Base editor type (CBE, ABE, dual)
   - Target organism/cell type
   - Application (disease model, therapy, crop improvement)
   - Editing efficiency
   - Off-target assessment

4. Categorize applications:
   - Therapeutic applications (by disease)
   - Agricultural applications
   - Basic research

5. Analyze trends:
   - Publications over time
   - Most studied diseases
   - Evolution of base editor technology

6. Synthesize findings:
   - Clinical trial status
   - Remaining challenges
   - Future directions

Generate comprehensive review document with citation statistics.
""")

agent.save_conversation_history("crispr_base_editing_review.pdf")
```

### Example 2: Gene Function Synthesis

```python
result = agent.go("""
Synthesize knowledge about gene function from multiple sources.

Target gene: PARK7 (DJ-1)

Integrate information from:
1. **Genetic databases:**
   - NCBI Gene
   - UniProt
   - OMIM

2. **Expression data:**
   - GTEx tissue expression
   - Human Protein Atlas
   - Single-cell expression atlases

3. **Functional data:**
   - GO annotations
   - KEGG pathways
   - Reactome
   - Protein interactions (STRING)

4. **Disease associations:**
   - ClinVar variants
   - GWAS catalog
   - Disease databases (DisGeNET)

5. **Literature:**
   - PubMed abstracts
   - Key mechanistic studies
   - Review articles

Synthesize into comprehensive gene report:
- Molecular function
- Biological processes
- Cellular localization
- Tissue distribution
- Disease associations
- Known drug targets/inhibitors
- Unresolved questions

Generate structured summary suitable for research planning.
""")
```

---

## Multi-Omics Integration

### Example 1: Multi-Omics Disease Analysis

```python
agent = A1(path='./data', llm='claude-sonnet-4-20250514')

result = agent.go("""
Integrate multi-omics data to understand disease mechanism.

Disease: Alzheimer's disease
Data types:
- Genomics: GWAS summary statistics (gwas_ad.txt)
- Transcriptomics: Brain RNA-seq (controls vs AD, rnaseq_data.csv)
- Proteomics: CSF proteomics (proteomics_csf.csv)
- Metabolomics: Plasma metabolomics (metabolomics_plasma.csv)
- Epigenomics: Brain methylation array (methylation_data.csv)

Integration workflow:
1. Analyze each omics layer independently:
   - Identify significantly altered features
   - Perform pathway enrichment

2. Cross-omics correlation:
   - Correlate gene expression with protein levels
   - Link genetic variants to expression (eQTL)
   - Associate methylation with gene expression
   - Connect proteins to metabolites

3. Network analysis:
   - Build multi-omics network
   - Identify key hub genes/proteins
   - Detect disease modules

4. Causal inference:
   - Prioritize drivers vs. consequences
   - Identify therapeutic targets
   - Predict drug mechanisms

5. Generate integrative model of AD pathogenesis

Provide visualization and therapeutic target recommendations.
""")

agent.save_conversation_history("ad_multiomics_analysis.pdf")
```

### Example 2: Systems Biology Modeling

```python
result = agent.go("""
Build systems biology model of metabolic pathway.

Pathway: Glycolysis
Data sources:
- Enzyme kinetics (BRENDA database)
- Metabolite concentrations (literature)
- Gene expression (tissue-specific, GTEx)
- Flux measurements (C13 labeling studies)

Modeling tasks:
1. Construct pathway model:
   - Define reactions and stoichiometry
   - Parameterize enzyme kinetics (Km, Vmax, Ki)
   - Set initial metabolite concentrations

2. Simulate pathway dynamics:
   - Steady-state analysis
   - Time-course simulations
   - Sensitivity analysis

3. Constraint-based modeling:
   - Flux balance analysis (FBA)
   - Identify bottleneck reactions
   - Predict metabolic engineering strategies

4. Integrate with gene expression:
   - Tissue-specific model predictions
   - Disease vs. normal comparisons

5. Therapeutic predictions:
   - Enzyme inhibition effects
   - Metabolic rescue strategies
   - Drug target identification

Generate model in SBML format and simulation results.
""")
```

---

## Best Practices for Task Formulation

### 1. Be Specific and Detailed

**Poor:**
```python
agent.go("Analyze this RNA-seq data")
```

**Good:**
```python
agent.go("""
Analyze bulk RNA-seq data from cancer vs. normal samples.

Files: cancer_rnaseq.csv (TPM values, 50 cancer, 50 normal)

Tasks:
1. Differential expression (DESeq2, padj < 0.05, |log2FC| > 1)
2. Pathway enrichment (KEGG, Reactome)
3. Generate volcano plot and top DE gene heatmap
""")
```

### 2. Include File Paths and Formats

Always specify:
- Exact file paths
- File formats (VCF, BAM, CSV, H5AD, etc.)
- Data structure (columns, sample IDs)

### 3. Set Clear Success Criteria

Define thresholds and cutoffs:
- Statistical significance (P < 0.05, FDR < 0.1)
- Fold change thresholds
- Quality filters
- Expected outputs

### 4. Request Visualizations

Explicitly ask for plots:
- Volcano plots, MA plots
- Heatmaps, PCA plots
- Network diagrams
- Manhattan plots

### 5. Specify Biological Context

Include:
- Organism (human, mouse, etc.)
- Tissue/cell type
- Disease/condition
- Treatment details

### 6. Request Interpretations

Ask agent to:
- Interpret biological significance
- Suggest follow-up experiments
- Identify limitations
- Provide literature context

---

## Common Patterns

### Data Quality Control

```python
"""
Before analysis, perform quality control:
1. Check for missing values
2. Assess data distributions
3. Identify outliers
4. Generate QC report
Only proceed with analysis if data passes QC.
"""
```

### Iterative Refinement

```python
"""
Perform analysis in stages:
1. Initial exploratory analysis
2. Based on results, refine parameters
3. Focus on interesting findings
4. Generate final report

Show intermediate results for each stage.
"""
```

### Reproducibility

```python
"""
Ensure reproducibility:
1. Set random seeds where applicable
2. Log all parameters used
3. Save intermediate files
4. Export environment info (package versions)
5. Generate methods section for paper
"""
```

These examples demonstrate the breadth of biomedical tasks biomni can handle. Adapt the patterns to your specific research questions, and always include sufficient detail for the agent to execute autonomously.
