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
pip install -r requirements.txt
```
3. Set up the environment for BioMaster:

Make sure you have `conda` installed and set up. BioMaster requires some bioinformatics tools to be installed, including BWA, Samtools, and others.
```sh
conda install -y bwa samtools trimmomatic
```

---

## Usage

BioMaster allows you to run and automate bioinformatics tasks using the `Biomaster` class. Here's a basic usage example:

```python
from agents.Biomaster import Biomaster

# Configuration for the agent
api_key = 'your-openai-api-key'
base_url = 'your-openai-base-url'

# Initialize Biomaster with your configuration
manager = Biomaster(api_key, base_url, excutor=True, tools_dir="tools", id='002')

# Input data and goal
datalist = [
    './data/4DNFI15H1RVG.fastq.gz: pair 1 The first file.',
    './data/4DNFIZHUKESO.fastq.gz: pair 1 The second file.',
    './data/4DNFIEQ58J6G.fastq.gz: pair 2 The first file.',
    './data/4DNFIKVDGNJN.fastq.gz: pair 2 The second file.',
    './data/hg38.bwaindex.tgz: GRCh38 (human) reference genome',
    './data/hg38.chrom.sizes: GRCh38 chromsize file'
]

goal = 'Please use this data for a complete Hi-C data preprocessing process'

# Run the task
plan_results = manager.execute_TASK(datalist)
print(plan_results)
```
In this example, `Biomaster` is initialized with API keys and a set of data. The `execute_TASK` method processes the task with the provided data list and returns the plan results.

---

## File Structure

- `agents/`: Contains agent classes for task management and execution.
- `tools/`: Directory for storing tool configurations used in the workflows.
- `output/`: Output directory where results and logs are saved.
- `prompts/`: Contains predefined prompts used for task generation and debugging.
- `doc/`: Stores documentation files for the workflows.

---

## Contributing

Feel free to fork the repository and create pull requests for any enhancements or bug fixes. Contributions are welcome!

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- This project uses the [langchain](https://github.com/hwchase17/langchain) library for integration with OpenAI and other tools.
- Thanks to all contributors and the open-source community for making BioMaster possible!
