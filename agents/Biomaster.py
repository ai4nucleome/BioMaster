import os
import subprocess
import json
import re
import logging
from datetime import datetime
import uuid  # 用于生成唯一ID

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, TextLoader, PyPDFLoader
from langchain_chroma import Chroma  # 使用 langchain_chroma 包中的 Chroma
from langchain_community.tools import ShellTool

from .prompts import PLAN_PROMPT, PLAN_EXAMPLES, TASK_PROMPT, TASK_EXAMPLES, DEBUG_EXAMPLES, DEBUG_PROMPT
from .ToolAgent import Json_Format_Agent
from .CheckAgent import CheckAgent  # Add this import at the top

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Biomaster:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        Model: str = "o3-mini-2025-01-31",
        excutor: bool = False,
        Repeat: int = 5,
        output_dir: str = './output',
        id: str = '001',
        chroma_db_dir: str = './chroma_db'  # Chroma持久化目录
    ):
        # 设置 USER_AGENT 环境变量以消除警告
        os.environ['USER_AGENT'] = 'Biomaster/1.0'
        os.environ['OPENAI_API_KEY'] = api_key
        self.api_key = api_key
        self.base_url = base_url
        self.model = Model
        self.doc_dir = "doc"
        self.excutor = excutor
        self.repeat = Repeat
        self.output_dir = output_dir
        self.stop_flag = False  # 标志位

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

        self.DEBUG_agent = self._create_agent(self.DEBUG_prompt, self.DEBUG_examples)
        self.TASK_agent = self._create_agent(self.TASK_prompt, self.TASK_examples)
        self.PLAN_agent = self._create_agent(self.PLAN_prompt, self.PLAN_examples)

        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002", base_url=self.base_url)

        # 存储集合名称
        self.collection1_name = "popgen_collection1"
        self.collection2_name = "popgen_collection2"

        # 初始化Chroma向量存储，指定持久化目录
        self.vectorstore = Chroma(
            collection_name=self.collection1_name,
            embedding_function=self.embeddings,
            persist_directory=os.path.join(chroma_db_dir, "collection1")  # 分开存储不同集合
        )
        self.vectorstore_tool = Chroma(
            collection_name=self.collection2_name,
            embedding_function=self.embeddings,
            persist_directory=os.path.join(chroma_db_dir, "collection2")  # 分开存储不同集合
        )

        # 加载知识数据（仅添加新数据）
        self.Load_PLAN_RAG()
        self.Load_Tool_RAG()

        # Initialize the CheckAgent
        self.check_agent = CheckAgent(api_key=api_key, base_url=base_url, model=Model)
    def normalize_keys(self,input_dict):
        """ Recursively convert all dictionary keys to lowercase."""
        if isinstance(input_dict, dict):
            return {k.lower(): self.normalize_keys(v) for k, v in input_dict.items()}
        elif isinstance(input_dict, list):
            return [self.normalize_keys(item) for item in input_dict]
        else:
            return input_dict
    def load_tool_links(self):
        """读取Task_Knowledge.json并返回metadata下source的列表"""
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
        # 加载指定ID的PLAN和step文件
        plan_file = os.path.join(self.output_dir, f'{self.id}_PLAN.json')
        if os.path.exists(plan_file):
            self.plan_data = self.load_progress(self.output_dir, f'{self.id}_PLAN.json')
        else:
            print(f"No PLAN file found for ID: {self.id}")

        # 这里可以添加更多逻辑来加载其他需要的文件

    def check_stop(self):
        if self.stop_flag:
            print(f"Task {self.id} is being stopped.")
            raise Exception(f"Task {self.id} was stopped by user request.")

    def stop(self):
        self.stop_flag = True

    def add_documents_if_not_exists(self, documents, collection, collection_name):
        """
        添加文档到向量数据库，如果文档ID不存在。
        :param documents: 列表，包含字典，字典中需有 'page_content' 和 'metadata' 键
        :param collection: Chroma 向量数据库集合
        :param collection_name: 字符串，集合名
        """
        new_texts = []
        new_metadatas = []
        new_ids = []
        for doc in documents:
            doc_id = doc['metadata'].get("id")
            if not doc_id:
                # 如果没有ID，生成一个唯一ID
                doc_id = str(uuid.uuid4())
                doc['metadata']['id'] = doc_id

            # 使用 get 方法检查文档是否存在
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
        从 JSON 文件中加载知识条目，并存储到 Chroma 向量数据库。
        每个 JSON 条目作为一个独立单元进行存储和检索。
        """
        json_file_path = os.path.join(self.doc_dir, "Plan_Knowledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON 文件未找到：{json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON 文件格式错误：应包含一个知识条目列表")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore, self.collection1_name)
        logging.info("Loaded PLAN_RAG data.")
        # Chroma 会自动持久化，无需显式调用 persist()

    def Load_Tool_RAG(self):
        """
        从 JSON 文件中加载知识条目，并存储到 Chroma 向量数据库。
        每个 JSON 条目作为一个独立单元进行存储和检索。
        """
        json_file_path = os.path.join(self.doc_dir, "Task_Knowledge.json")

        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON 文件未找到：{json_file_path}")

        with open(json_file_path, "r", encoding="utf-8") as file:
            knowledge_data = json.load(file)

        if not isinstance(knowledge_data, list):
            raise ValueError("JSON 文件格式错误：应包含一个知识条目列表")

        documents = [
            {
                "page_content": entry["content"],
                "metadata": entry.get("metadata", {})
            }
            for entry in knowledge_data
        ]
        self.add_documents_if_not_exists(documents, self.vectorstore_tool, self.collection2_name)
        logging.info("Loaded Tool_RAG data.")
        # Chroma 会自动持久化，无需显式调用 persist()

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
            'mkdir -p ./output/'+str({self.id})
        ]

        with open(shell_script_path, "w", encoding="utf-8") as file:
            # 先写入前缀命令
            file.write("#!/bin/bash\n")
            for command in code_prefix:
                file.write(command + "\n")

            # 写入实际的shell命令
            for command in commands:
                file.write(f"{command}\n")
        return shell_script_path

    def _truncate_text(self, text, max_length):
        return text if len(text) <= max_length else text[:max_length] + '...'

    def save_progress(self, step_data, output_dir, file_name):
        file_name = f"{self.id}_{file_name}"
        file_path = os.path.join(output_dir, file_name)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 写入数据
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

        # 遍历output目录下的所有文件
        for root, dirs, files in os.walk(output_dir_path):
            for file in files:
                if file.endswith(('.json', '.sh', '.txt')):  # 您可以根据文件类型进行过滤
                    output_files.append(os.path.join(root, file))

        return output_files

    def execute_PLAN(self, goal, datalist):
        """
        生成新的PLAN，覆盖之前的PLAN.json，同时保存旧的计划和步骤输出到历史记录。
        """
        plan_file_path = os.path.join(self.output_dir, "PLAN.json")
        existing_plan = self.load_progress(self.output_dir, "PLAN.json")
        print(existing_plan)
        print()
        if existing_plan:
            logging.info("existing PLAN found.")
        else:
            logging.info("No existing PLAN found. Proceeding to generate a new PLAN.")
        # 生成新的PLAN
        logging.info("Generating a new PLAN.")

        related_docs = self.vectorstore.similarity_search(goal, k=1)
        related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])
        logging.info(f"Related documents content: {related_docs_content}")
        # 构建参考内容：仅使用相关文档内容作为参考
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
        PLAN_results = Json_Format_Agent(PLAN_results, self.api_key, self.base_url)
        
        try:
            PLAN_results_dict = self.normalize_keys(json.loads(PLAN_results.strip().strip('"')))
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse PLAN_results: {e}")
            return {}

        # 保存新的PLAN，覆盖之前的PLAN.json
        self.save_progress(PLAN_results_dict, self.output_dir, "PLAN.json")
        logging.info("Saved new PLAN.json.")
        # 保存到执行历史记录，使用mode=0表示新计划

        logging.info("_____________________________________________________")
        logging.info(json.dumps(PLAN_results_dict, indent=4, ensure_ascii=False))
        logging.info("_____________________________________________________")
        
        return PLAN_results_dict

    def get_all_files_in_output_folder(self):
        """
        获取 output/{id} 文件夹下的所有文件路径
        """
        output_folder = os.path.join(self.output_dir, self.id)
        if not os.path.exists(output_folder):
            print(f"Folder {output_folder} does not exist.")
            return []

        # 遍历所有文件
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
        # 获取所有生成文件的路径，并将其添加到step['input filename']
        
        all_output_files = self.get_all_files_in_output_folder()
        print(f"All files in output/{ids}: {all_output_files}")

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

            related_docs = self.vectorstore_tool.similarity_search(step['description'], k=1)

            # 将完整内容拼接为字符串，确保不截断
            related_docs_content = "\n\n".join([doc.page_content for doc in related_docs])
            print(related_docs)
            # 将遍历到的文件路径添加到step['input filename']中
            additional_files = self.get_all_files_in_output_folder()
            step['input_filename'].extend(additional_files)

            self.check_stop()
            if self.stop_flag:
                break

            # print(step['input_filename'])

            generated_files = self._get_output_files()
            step['input_filename'].extend(generated_files)
            step['input_filename'] = list(set(step['input_filename']))  # 去重
            print(step['input_filename'])

            # Repeat Test count
            retry_count = 0
            # JSON error
            Json_Error = False

            while retry_count < self.repeat:
                if retry_count == 0 or Json_Error:

                    self.check_stop()
                    if self.stop_flag:
                        break
                    # 从 datalist 中提取文件路径
                    # 假设 step['input_filename'] 已经存在并是一个列表
                    new_input_filenames = [item.split(':')[0] for item in step_datalist]
                    # 更新 step['input_filename']，确保没有重复文件路径
                    step['input_filename'] = list(set(step['input_filename'] + new_input_filenames))
                    # print(step['input_filename'])

                    TASK_input = {
                        "input": json.dumps({
                            "task": step,
                            "id": ids,
                            "related_docs": related_docs_content,  # 使用related_docs_content
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

                    # 如果不执行，则直接跳过后续步骤
                    if not self.excutor:
                        shell_script_path = self.shell_writing(TASK_results, i)
                        break

                else:
                    TASK_results = DEBUG_output_dict.get("shell", "")

                # 写为sh脚本
                shell_script_path = self.shell_writing(TASK_results, i)
                # 执行脚本

                self.check_stop()
                if self.stop_flag:
                    break
                result = subprocess.run(["bash", shell_script_path], capture_output=True)#, text=True

                stdout_str = result.stdout.decode("utf-8", errors="replace")
                stderr_str = result.stderr.decode("utf-8", errors="replace")
                self.check_stop()
                if self.stop_flag:
                    break
                max_output_length = 5000  # 设置最大输出字符数

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
                # 保存上次输入
                PRE_DEBUG_output.append(DEBUG_output)

                # 规范格式
                DEBUG_output = Json_Format_Agent(DEBUG_output, self.api_key, self.base_url)

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
                        
                        # If CheckAgent modified the DEBUG output (i.e., found issues)
                        
                        if check_results.get("debug_output_modified", False):
                            # Reload the updated DEBUG output
                            with open(debug_output_path, 'r', encoding='utf-8') as f:
                                DEBUG_output_dict = json.load(f)
                            
                            # Give DebugAgent another chance if files failed verification
                            DEBUG_input = {
                                "input": json.dumps({
                                    "task": step,
                                    "pre debug": [json.dumps(DEBUG_output_dict)],
                                    "result": f"File verification failed. {DEBUG_output_dict.get('analyze', '')}",
                                    "related_docs": related_docs_content,
                                    "id": ids,
                                    "shell": TASK_results,
                                })
                            }
                            
                            # Run DebugAgent again and parse result
                            DEBUG_output = DEBUG_agent.invoke(DEBUG_input)
                            DEBUG_output = Json_Format_Agent(DEBUG_output, self.api_key, self.base_url)
                            
                            try:
                                new_DEBUG_output_dict = json.loads(DEBUG_output)
                                # Directly update the original DEBUG output file
                                DEBUG_output_dict = new_DEBUG_output_dict
                                self.save_progress(DEBUG_output_dict, self.output_dir, f"DEBUG_Output_{i}.json")
                            except json.JSONDecodeError:
                                logging.error(f"Error parsing DEBUG agent retry output for step {i}")
                        
                        # Continue only if final stats is True
                        if DEBUG_output_dict.get("stats", False):
                            previous_output_filenames = step['output_filename']
                            break  # Success
                        else:
                            print(f"Step {i} failed: {DEBUG_output_dict.get('analyze', 'Unknown reason')}. Attempt {retry_count + 1}")
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
