from agents.Biomaster import Biomaster
from langchain_core.messages import HumanMessage
import json
# Example of using the agent
if __name__ == "__main__":
    # Configuration for the agent
    config = {"configurable": {"thread_id": "abc124"}}
    api_key = 'sk----'
    base_url = '----'

    manager = Biomaster(api_key, base_url,excutor=True, tools_dir="tools",id='002')
    

    datalist=[ './data/4DNFI15H1RVG.fastq.gz: pair 1 The first file. Raw paired-end sequencing data from an in situ Hi-C experiment on GM12878, utilizing MboI for chromatin fragmentation. ', 
                './data/4DNFIZHUKESO.fastq.gz: pair 1 The second file. Raw paired-end sequencing data from an in situ Hi-C experiment on GM12878 with MboI digestion. '
                './data/4DNFIEQ58J6G.fastq.gz: pair 2 The first file.Raw paired-end sequencing data from an in situ Hi-C experiment on GM12878, utilizing MboI for chromatin fragmentation.  ',
                './data/4DNFIKVDGNJN.fastq.gz: pair 2 The second file.Raw paired-end sequencing data from an in situ Hi-C experiment on GM12878 with MboI digestion.',
                './data/hg38.bwaindex.tgz: GRCh38 (human)  reference genome ',
                './data/hg38.chrom.sizes:the GRCh38 the chromsize file'
                ]
    goal='Please use this data for a complete hic data preprocessing process'
    
    # manager.execute_PLAN(goal,datalist)
    print("**********************************************************")

    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)


