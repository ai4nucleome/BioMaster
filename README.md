# BioMaster: Automating Complex Bioinformatics Workflows

**BioMaster** is a multi-agent framework designed to streamline and automate complex bioinformatics workflows. By leveraging large language models (LLMs) and dynamic knowledge retrieval, BioMaster addresses key limitations in automation, improving accuracy, efficiency, and scalability across a wide range of bioinformatics tasks, such as RNA-seq, ChIP-seq, and Hi-C data processing.

---

## Features

- **Automated Bioinformatics Workflows**: BioMaster automates complex bioinformatics tasks, such as data preprocessing, alignment, variant calling, and analysis, with a focus on RNA-seq, ChIP-seq, and Hi-C data.
  
- **Role-based Agents**: Specialized agents within BioMaster perform task decomposition, validation, and execution, improving the management of complex workflows.
  
- **Retrieval-Augmented Generation (RAG)**: BioMaster dynamically retrieves relevant knowledge from external sources to enhance adaptability to new tools and niche analyses.
  
- **Enhanced Error Handling**: BioMaster provides advanced error detection and correction mechanisms to ensure consistency and reliability across multi-step workflows.
  
- **Efficient Memory Management**: Optimized memory strategies allow BioMaster to handle long-running workflows without compromising performance or accuracy.

- **Extensible**: BioMaster is designed to be easily extendable, with support for custom bioinformatics tools and workflows.

---

## Installation

You can install BioMaster using the following steps:

1. Clone the repository:

git clone https://github.com/yourusername/BioMaster.git
cd BioMaster

2. Install the required dependencies:
```sh
conda create -n agent python=3.12

conda activate agent

pip install -r requirements.txt
```

3. download data and move to `data/`:

```sh
通过网盘分享的文件：Biomaster
链接: https://pan.baidu.com/s/1t9I63lucrjdWjSK09NVxwQ?pwd=ai4s 提取码: ai4s 
```
---

## Usage

BioMaster allows you to run and automate bioinformatics tasks using the `Biomaster` class. Here's a basic usage example:

```python
from agents.Biomaster import Biomaster
from langchain_core.messages import HumanMessage
import json
# Example of using the agent
if __name__ == "__main__":

    config = {"configurable": {"thread_id": "abc124"}}
    api_key = 'sk-BMBEq7cFiq8LClul845cB42f9aCf429dB04a0bF6Ad542e2b'
    base_url = 'https://one-api.bltcy.top/v1'
    manager = Biomaster(api_key, base_url,excutor=True, tools_dir="tools",id='002')
    
    datalist=["./data/1000GP_pruned.bed: SNP file in bed format",
                "./data/1000GP_pruned.bim: snp info associate with the bed format",
                "./data/1000GP_pruned.fam: data information, the first col is population, the second is sample ID",]
    goal='please help me do ROH.'
    
    manager.execute_PLAN(goal,datalist)
    print("**********************************************************")

    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)




```

In this example, `Biomaster` is initialized with API keys and a set of data. The `execute_TASK` method processes the task with the provided data list and returns the plan results.


```sh
conda activate agent
python run.py
```
---

## File Structure

- `agents/`: Contains agent classes for task management and execution.
- `tools/`: Directory for storing tool configurations used in the workflows.
- `output/`: Output directory where results and logs are saved.
- `doc/`: Stores documentation files for the workflows.
- `data/`: Usually used to store files.

---


# License
This project is licensed under the following terms:

- **Code**: Licensed under the MIT License. See LICENSE for details.
- **Data and Documentation**: Licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).

---

## Acknowledgments

- This project uses the [langchain](https://github.com/hwchase17/langchain) library for integration with OpenAI and other tools.
- Thanks to all contributors and the open-source community for making BioMaster possible!
