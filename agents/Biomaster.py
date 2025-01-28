import os
import subprocess
import json
import re
import logging
from datetime import datetime
import uuid  

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain_chroma import Chroma  
from langchain_community.tools import ShellTool

from .prompts import PLAN_PROMPT, PLAN_EXAMPLES, TASK_PROMPT, TASK_EXAMPLES, DEBUG_EXAMPLES, DEBUG_PROMPT
from .utils import normalize_keys, load_tool_links
from .ToolAgent import Json_Format_Agent
from .CheckAgent import Check_Agent
from mem0 import Memory  


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Biomaster:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        Model: str = "chatgpt-4o-latest",
        excutor: bool = False,
        Repeat: int = 5,
        tools_dir: str = "tools",
        output_dir: str = './output',
        id: str = '001',
        chroma_db_dir: str = './chroma_db'  
    ):
        os.environ['USER_AGENT'] = 'Biomaster/1.0'
        os.environ['OPENAI_API_KEY'] = api_key
        self.api_key = api_key
        self.base_url = base_url
        self.model = Model
        self.tools_dir = tools_dir
        self.doc_dir = "doc"
        self.excutor = excutor
        self.repeat = Repeat
        self.output_dir = output_dir
        self.stop_flag = False  

        if id == '000':
            self.id = self._generate_new_id()
        else:
            self.id = id
            self._load_existing_files()

        tools_info, self.tool_names = self._load_tools_from_files()

        self.PLAN_prompt = PLAN_PROMPT.format(tool_names=self.tool_names)
        self.TASK_prompt = TASK_PROMPT.format(tool_names=self.tool_names)
        self.DEBUG_prompt = DEBUG_PROMPT.format(tool_names=self.tool_names)

        self.PLAN_examples = PLAN_EXAMPLES
        self.TASK_examples = TASK_EXAMPLES
        self.DEBUG_examples = DEBUG_EXAMPLES

        self.DEBUG_agent = self._create_agent(self.DEBUG_prompt, self.DEBUG_examples)
        self.TASK_agent = self._create_agent(self.TASK_prompt, self.TASK_examples)
        self.PLAN_agent = self._create_agent(self.PLAN_prompt, self.PLAN_examples)

        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", base_url=self.base_url)

        self.collection1_name = "popgen_collection1"
        self.collection2_name = "popgen_collection2"

        self.vectorstore = Chroma(
            collection_name=self.collection1_name,
            embedding_function=self.embeddings,
            persist_directory=os.path.join(chroma_db_dir, "collection1")  
        )
        self.vectorstore_tool = Chroma(
            collection_name=self.collection2_name,
            embedding_function=self.embeddings,
            persist_directory=os.path.join(chroma_db_dir, "collection2") 
        )


        self.Load_PLAN_RAG()
        self.Load_Tool_RAG()

    def _generate_new_id(self):
        existing_ids = []
        for file_name in os.listdir(self.output_dir):
            match = re.match(r'^(\d{3})_', file_name)
            if match:
                existing_ids.append(int(match.group(1)))

        new_id = min(set(range(1, max(existing_ids, default=0) + 2)) - set(existing_ids))
        return f'{new_id:03d}'

    def _load_existing_files(self):
        plan_file = os.path.join(self.output_dir, f'{self.id}_PLAN.json')
        if os.path.exists(plan_file):
            self.plan_data = self.load_progress(self.output_dir, f'{self.id}_PLAN.json')
        else:
            print(f"No PLAN file found for ID: {self.id}")


    def check_stop(self):
        if self.stop_flag:
            print(f"Task {self.id} is being stopped.")
            raise Exception(f"Task {self.id} was stopped by user request.")

    def stop(self):
        self.stop_flag = True

    def _load_tools_from_files(self):
        tool_files = [f for f in os.listdir(self.tools_dir) if f.endswith(".config")]
        tool_strings = []
        tool_names = []

        for file in tool_files:
            tool_name = file.split(".")[0]
            tool_names.append(tool_name)

            with open(os.path.join(self.tools_dir, file), "r", encoding='utf-8') as f:
                tool_description = f.read().strip()
                tool_strings.append(f"    {tool_name}: {tool_description}")

        return "\n".join(tool_strings), ", ".join(tool_names)

    def add_documents_if_not_exists(self, documents, collection, collection_name):
        """
        Add a document to the vector database if the document ID does not exist.
        :param documents: list， 'page_content' , 'metadata' 
        :param collection: Chroma set
        :param collection_name: str
        """
        new_texts = []
        new_metadatas = []
        new_ids = []
        for doc in documents:
            doc_id = doc['metadata'].get("id")
            if not doc_id:

                doc_id = str(uuid.uuid4())
                doc['metadata']['id'] = doc_id

            existing_docs = collection.get(ids=[doc_id])
            if not existing_docs['documents']:
                new_texts.append(doc['page_content'])
                new_metadatas.append(doc['metadata'])
                new_ids.append(doc_id)

        if new_texts:
            collection.add_texts(texts=new_texts, metadatas=new_metadatas, ids=new_ids)
            logging.info(f"Added {len(new_texts)} new documents to {collection_name}")

    def Load_PLAN_RAG(self):
        """
        Load the knowledge items from the JSON file and store them in the Chroma vector database.
Each JSON entry is stored and retrieved as a separate unit.
        """
        json_file_path = os.path.join(self.doc_dir, "Plan_Knowledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found：{json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON file format error: Should contain a list of knowledge items")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore, self.collection1_name)
        logging.info("Loaded PLAN_RAG data.")
        # Chroma persist automatically, no need to explicitly call persist()

    def Load_Tool_RAG(self):
        """
        Load the knowledge items from the JSON file and store them in the Chroma vector database.
Each JSON entry is stored and retrieved as a separate unit.
        """
        json_file_path = os.path.join(self.doc_dir, "Task_Konwledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found：{json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON file format error: Should contain a list of knowledge items")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore_tool, self.collection2_name)
        logging.info("Loaded Tool_RAG data.")
        # Chroma automatically persists without explicitly calling persist()

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
            # 'conda config --set show_channel_urls false',
            # 'conda config --add channels conda-forge',
            # 'conda config --add channels bioconda',
        ]

        with open(shell_script_path, "w", encoding="utf-8") as file:
            file.write("#!/bin/bash\n")
            for command in code_prefix:
                file.write(command + "\n")

            for command in commands:
                file.write(f"{command}\n")
        return shell_script_path

    def _truncate_text(self, text, max_length):
        return text if len(text) <= max_length else text[:max_length] + '...'

    def save_progress(self, step_data, output_dir, file_name):
        file_name = f"{self.id}_{file_name}"
        file_path = os.path.join(output_dir, file_name)

        os.makedirs(output_dir, exist_ok=True)

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

        for root, dirs, files in os.walk(output_dir_path):
            for file in files:
                if file.endswith(('.json', '.sh', '.txt')):
                    output_files.append(os.path.join(root, file))

        return output_files

    def _archive_existing_plan(self):

        plan_file = os.path.join(self.output_dir, "PLAN.json")
        if os.path.exists(plan_file):

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            archived_plan_path = os.path.join(self.doc_dir, f"PLAN_{self.id}_{timestamp}.json")
            with open(plan_file, "r", encoding="utf-8") as src, open(archived_plan_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            logging.info(f"Archived existing PLAN.json to {archived_plan_path}")

            history_plan_file = os.path.join(self.doc_dir, "excute_agent_plan_history.json")  
            if not os.path.exists(history_plan_file):
                with open(history_plan_file, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=4, ensure_ascii=False)

            with open(history_plan_file, "r", encoding="utf-8") as f:
                history_plans = json.load(f)

            with open(plan_file, "r", encoding="utf-8") as f:
                current_plan = json.load(f)

            history_entry = {
                "id": self.id,
                "timestamp": timestamp,
                "plan": current_plan
            }
            history_plans.append(history_entry)

            with open(history_plan_file, "w", encoding="utf-8") as f:
                json.dump(history_plans, f, indent=4, ensure_ascii=False)

            logging.info(f"Added existing PLAN.json to history with ID {self.id}")

    def _archive_existing_steps(self):

        history_task_file = os.path.join(self.doc_dir, "excute_agent_task_history.json") 
        if not os.path.exists(history_task_file):
            with open(history_task_file, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

        steps = []
        for file in os.listdir(self.output_dir):
            debug_match = re.match(rf"^{self.id}_DEBUG_Output_(\d+)\.json$", file)
            shell_match = re.match(rf"^{self.id}_Step_(\d+)\.sh$", file)
            if debug_match:
                step_num = int(debug_match.group(1))
                with open(os.path.join(self.output_dir, file), "r", encoding="utf-8") as f:
                    debug_data = json.load(f)
                steps.append({
                    "step_number": step_num,
                    "type": "debug_output",
                    "content": debug_data
                })
            elif shell_match:
                step_num = int(shell_match.group(1))
                with open(os.path.join(self.output_dir, file), "r", encoding="utf-8") as f:
                    shell_commands = f.read()
                steps.append({
                    "step_number": step_num,
                    "type": "shell_script",
                    "content": shell_commands
                })

        with open(history_task_file, "r", encoding="utf-8") as f:
            history_tasks = json.load(f)

        current_plan = self.load_progress(self.output_dir, "PLAN.json")

        history_entry = {
            "id": self.id,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "steps": steps,
            "plan": current_plan
        }

        history_tasks.append(history_entry)

        with open(history_task_file, "w", encoding="utf-8") as f:
            json.dump(history_tasks, f, indent=4, ensure_ascii=False)

        logging.info(f"Archived existing steps to task history with ID {self.id}")

    def execute_PLAN(self, goal, datalist):

        plan_file_path = os.path.join(self.output_dir, "PLAN.json")
        existing_plan = self.load_progress(self.output_dir, "PLAN.json")

        if existing_plan:
            self._archive_existing_plan()
            self._archive_existing_steps()
        else:
            logging.info("No existing PLAN found. Proceeding to generate a new PLAN.")

        logging.info("Generating a new PLAN.")
        related_docs = self.vectorstore.similarity_search(goal, k=1)
        related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])
        logging.info(f"Related documents content: {related_docs_content}")

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
        try:
            PLAN_results_dict = normalize_keys(json.loads(PLAN_results.strip().strip('"')))
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse PLAN_results: {e}")
            return {}


        self.save_progress(PLAN_results_dict, self.output_dir, "PLAN.json")
        logging.info("Saved new PLAN.json.")

        logging.info("_____________________________________________________")
        logging.info(json.dumps(PLAN_results_dict, indent=4, ensure_ascii=False))
        logging.info("_____________________________________________________")

        return PLAN_results_dict

    def get_all_files_in_output_folder(self):

        output_folder = os.path.join(self.output_dir, self.id)
        if not os.path.exists(output_folder):
            print(f"Folder {output_folder} does not exist.")
            return []

        all_files = []
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
        return all_files

    def execute_TASK(self, datalist):
        PLAN_results_dict = self.load_progress(self.output_dir, f"PLAN.json")
        PLAN_results_dict = normalize_keys(PLAN_results_dict)
        TASK_agent = self.TASK_agent
        step_datalist = datalist
        if self.excutor:
            DEBUG_agent = self.DEBUG_agent
        ids = self.id

        all_output_files = self.get_all_files_in_output_folder()
        print(f"All files in output/{ids}: {all_output_files}")
        # print(generated_files)
        for i in range(1, len(PLAN_results_dict['plan']) + 1):
            print("Step:", i)
            self.check_stop()
            step = PLAN_results_dict['plan'][i - 1]

            if self.excutor:
                DEBUG_output_dict = self.load_progress(self.output_dir, f"DEBUG_Output_{i}.json")

                if DEBUG_output_dict and DEBUG_output_dict.get("stats", True):
                    print(f"Step {i} already completed. Continuing.")
                    step_datalist = DEBUG_output_dict['output_filename'] + step_datalist
                    continue
            tool_name = step['tools']
            tool_links = load_tool_links(tool_name, self.tools_dir)

            related_docs = self.vectorstore_tool.similarity_search(step['description'], k=1)

            related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])

            additional_files = self.get_all_files_in_output_folder()
            step['input_filename'].extend(additional_files)



            generated_files = self._get_output_files()
            step['input_filename'].extend(generated_files)
            step['input_filename'] = list(set(step['input_filename']))  
            print(step['input_filename'])

            # Repeat Test count
            retry_count = 0
            # JSON error
            Json_Error = False

            while retry_count < self.repeat:
                if retry_count == 0 or Json_Error:

                    new_input_filenames = [item.split(':')[0] for item in step_datalist]


                    step['input_filename'] = list(set(step['input_filename'] + new_input_filenames))
                    print(step['input_filename'])

                    TASK_input = {
                        "input": json.dumps({
                            "task": step,
                            "id": ids,
                            "related_docs": related_docs_content,  
                        })
                    }
                    TASK_results = TASK_agent.invoke(TASK_input)
                    TASK_results = Json_Format_Agent(TASK_results, self.api_key, self.base_url)
                    PRE_DEBUG_output = []
                    try:
                        TASK_results = json.loads(TASK_results)
                        TASK_results = TASK_results.get("shell", "")
                    except json.JSONDecodeError as e:
                        logging.error(f"Failed to parse TASK_results: {e}")
                        TASK_results = ""


                    if not self.excutor:
                        shell_script_path = self.shell_writing(TASK_results, i)
                        break

                else:
                    TASK_results = DEBUG_output_dict.get("shell", "")


                shell_script_path = self.shell_writing(TASK_results, i)

                result = subprocess.run(["bash", shell_script_path], capture_output=True, text=True)

                max_output_length = 5000  

                result_stdout = result.stdout[:max_output_length] if len(result.stdout) > max_output_length else result.stdout
                result_stderr = result.stderr[:max_output_length] if len(result.stderr) > max_output_length else result.stderr

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

                PRE_DEBUG_output.append(DEBUG_output)


                DEBUG_output = Json_Format_Agent(DEBUG_output, self.api_key, self.base_url)

                try:
                    print("***************************************************************")
                    print(DEBUG_output)
                    print("***************************************************************")
                    DEBUG_output_dict = json.loads(DEBUG_output)
                    self.save_progress(DEBUG_output_dict, self.output_dir, f"DEBUG_Output_{i}.json")
                    if DEBUG_output_dict.get("stats", True):
                        Check_Agent(step,DEBUG_output, self.api_key, self.base_url)

                        previous_output_filenames = step['output_filename']
                        break  # Success
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
