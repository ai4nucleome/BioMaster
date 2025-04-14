from agents.Biomaster import Biomaster
from langchain_core.messages import HumanMessage
import json
# Example of using the agent
if __name__ == "__main__":

    config = {"configurable": {"thread_id": "abc124"}}
    api_key = ''
    base_url = ''
    # you can choose other base url
    manager = Biomaster(api_key, base_url,excutor=True,id='010')
    

    datalist=[ './data/rnaseq_1.fastq.gz: RNA-Seq read 1 data (left read)',
            './data/rnaseq_2.fastq.gz: RNA-Seq read 2 data (right read)',
            './data/minigenome.fa: small genome sequence consisting of ~750 genes.',]
    goal='please do WGS/WES data analysis Somatic SNV+indel calling.'
    manager.execute_PLAN(goal,datalist)
    print("**********************************************************")

    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)


