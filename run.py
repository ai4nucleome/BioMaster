from agents.Biomaster import Biomaster
from langchain_core.messages import HumanMessage
import json
# Example of using the agent
if __name__ == "__main__":

    config = {"configurable": {"thread_id": "abc124"}}
    api_key = 'sk-----'
    base_url = 'https://sg.uiuiapi.com/v1'
    # you can choose other base url
    manager = Biomaster(api_key, base_url,excutor=True,id='007')
    
    # datalist=["./data/1000GP_pruned.bed: SNP file in bed format",
    #             "./data/1000GP_pruned.bim: snp info associate with the bed format",
    #             "./data/1000GP_pruned.fam: data information, the first col is population, the second is sample ID",]
    # goal='please help me do ROH.'
    datalist=[ './data/SRR1374921.fastq.gz: single-end mouse rna-seq reads, replicate 1 in LoGlu group',
            './data/SRR1374922.fastq.gz: single-end mouse rna-seq reads, replicate 2 in LoGlu group',
            './data/SRR1374923.fastq.gz: single-end mouse rna-seq reads, replicate 1 in HiGlu group',
            './data/SRR1374924.fastq.gz: single-end mouse rna-seq reads, replicate 2 in HiGlu group',
            './data/TruSeq3-SE1.fa: trimming adapter',
            './data/mm391.fa: mouse mm39 genome fasta',
            './data/mm391.ncbiRefSeq.gtf: mouse mm39 genome annotation',]
    goal='find the differentially expressed genes'
    # manager.execute_PLAN(goal,datalist)
    print("**********************************************************")

    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)


