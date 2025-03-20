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
    
    datalist=["./data/1000GP_pruned.bed: SNP file in bed format",
                "./data/1000GP_pruned.bim: snp info associate with the bed format",
                "./data/1000GP_pruned.fam: data information, the first col is population, the second is sample ID",]
    goal='please help me do ld decay by plink.'

    manager.execute_PLAN(goal,datalist)
    print("**********************************************************")

    PLAN_results_dict = manager.execute_TASK(datalist)
    print(PLAN_results_dict)


