import os
import json
import logging
import re
from typing import Dict, List, Tuple, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class CheckAgent:
    """
    CheckAgent, core functions:
    - Verify expected output files exist and are non-empty (0 bytes)
    - Scan directory and use LLM to identify possible output files when expected files don't exist
    - Update status in DEBUG_Output file
    """
    
    def __init__(self, api_key: str, base_url: str, model: str = "o1-2024-12-17", **kwargs):
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.model = ChatOpenAI(model=model, base_url=base_url)
        
        # Create prompt template
        self.file_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are a bioinformatics file analysis expert. Based on the step information and file list,
            determine which files are likely valid outputs. Return JSON with:
            {{
                "analysis": "Detailed analysis of why files are valid or invalid",
                "output_filename": ["file1: description", "file2: description", ...],
                "stats": true/false (whether files are valid outputs)
            }}
            """),
            ("human", """
            Step details:
            - Step number: {step_number}
            - Tool: {tool_name}
            - Description: {step_description}
            
            Available files: {file_list}
            
            Expected output files: {expected_files}
            """)
        ])
    
    def check_file_size(self, file_path: str) -> Tuple[bool, str]:
        """Check if file exists and is not empty (0 bytes)"""
        if not os.path.exists(file_path):
            return False, f"File doesn't exist: {file_path}"
        
        if os.path.getsize(file_path) == 0:
            return False, f"File is empty (0 bytes): {file_path}"
            
        return True, f"File exists and has content"
    
    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Scan all non-empty files in the directory"""
        if not os.path.exists(directory):
            return []
        
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                path = os.path.join(root, filename)
                if os.path.exists(path) and os.path.getsize(path) > 0:
                    files.append({
                        "path": path,
                        "size": os.path.getsize(path)
                    })
        return files
    
    def get_step_details(self, task_id: str, step_number: str) -> Dict[str, Any]:
        """Get step details from PLAN.json"""
        plan_path = f"./output/{task_id}_PLAN.json"
        if not os.path.exists(plan_path):
            return {}
        
        try:
            with open(plan_path, 'r', encoding='utf-8') as plan_file:
                plan = json.load(plan_file)
                
            for step in plan.get("plan", []):
                if str(step.get("step_number", "")) == step_number:
                    return step
        except:
            return {}
        
        return {}
    
    def check_output_files(self, debug_output_path: str) -> Dict[str, Any]:
        """
        Main check function: Check if files exist and are non-empty, scan directory for analysis if not
        Returns a dictionary with analysis and stats
        """
        # Check and load DEBUG_Output file
        if not os.path.exists(debug_output_path):
            return {
                "analysis": "DEBUG_Output file doesn't exist",
                "stats": False
            }
            
        try:
            with open(debug_output_path, 'r', encoding='utf-8') as debug_file:
                debug_output = json.load(debug_file)
        except:
            return {
                "analysis": "Failed to read DEBUG_Output file",
                "stats": False
            }
        
        # Keep original stats value
        original_stats = debug_output.get("stats", True)
        
        # Extract task ID and step number from path
        path_match = re.search(r'(\d+)_DEBUG_Output_(\d+)\.json', debug_output_path)
        if not path_match:
            return {
                "analysis": "Failed to extract task ID and step number from path",
                "stats": False
            }
        
        task_id = path_match.group(1)
        step_number = path_match.group(2)
        output_dir = f"./output/{task_id}"
        
        # Get expected output file list
        output_files = debug_output.get("output_filename", [])
        expected_files = []
        for file_entry in output_files:
            if ':' in file_entry:
                path = file_entry.split(':', 1)[0].strip()
            else:
                path = file_entry.strip()
            expected_files.append(path)
        
        # 1. Check if all expected files exist and are non-empty
        if expected_files:
            all_valid = True
            has_empty_file = False
            failed_files = []
            
            for file_path in expected_files:
                valid, message = self.check_file_size(file_path)
                if not valid:
                    all_valid = False
                    failed_files.append(message)
                    if os.path.exists(file_path) and os.path.getsize(file_path) == 0:
                        has_empty_file = True
            
            if has_empty_file:
                return {
                    "analysis": "there's an empty file",
                    "stats": False
                }
            
            # If all expected files are valid, return success without changing stats
            if all_valid:
                with open(debug_output_path, 'w', encoding='utf-8') as out_file:
                    json.dump(debug_output, out_file, indent=4)
                return {
                    "analysis": "All expected files exist and are non-empty",
                    "stats": True
                }
                    
        # 2. If no expected files or missing expected files, scan directory
        all_files = self.scan_directory(output_dir)
        if not all_files:
            # No files found, but don't change stats
            analysis_message = f"No files found in {output_dir}"
            debug_output["analyze"] = debug_output.get("analyze", "") + f"\n\n{analysis_message}"
            
            with open(debug_output_path, 'w', encoding='utf-8') as out_file:
                json.dump(debug_output, out_file, indent=4)
            
            return {
                "analysis": analysis_message,
                "stats": False
            }
        
        # 3. Get step details and format file list
        step_details = self.get_step_details(task_id, step_number)
        file_list_text = "\n".join([f"- {f['path']} ({f['size']} bytes)" for f in all_files])
        
        # 4. Call LLM for analysis
        response = self.file_prompt.invoke({
            "step_number": step_details.get("step_number", "unknown"),
            "tool_name": step_details.get("tools", "unknown"),
            "step_description": step_details.get("description", "unknown"),
            "file_list": file_list_text,
            "expected_files": ", ".join(expected_files) if expected_files else "not specified"
        })
        
        result = self.model.invoke(response)
        
        # 5. Parse model response
        try:
            model_response = json.loads(result.content)
            analysis = model_response.get("analysis", "")
            new_output_files = model_response.get("output_filename", [])
            model_stats = model_response.get("stats", True)  # Default to True
        except:
            analysis = "Failed to parse LLM response, but continuing processing"
            new_output_files = []
            model_stats = True
        
        # 6. Update PLAN.json if new output files found
        if model_stats and new_output_files:
            plan_path = f"./output/{task_id}_PLAN.json"
            if os.path.exists(plan_path):
                try:
                    with open(plan_path, 'r', encoding='utf-8') as plan_file:
                        plan_data = json.load(plan_file)
                    
                    # Find current step and next step
                    current_step = None
                    next_step = None
                    steps = plan_data.get("plan", [])
                    
                    for i, step in enumerate(steps):
                        if str(step.get("step_number", "")) == step_number:
                            current_step = step
                            if i + 1 < len(steps):
                                next_step = steps[i + 1]
                            break
                    
                    # Update current step's output_filename
                    if current_step:
                        current_outputs = current_step.get("output_filename", [])
                        existing_paths = [f.split(": ")[0] if ": " in f else f for f in current_outputs]
                        
                        for file in new_output_files:
                            file_path = file.split(": ")[0] if ": " in file else file
                            if file_path not in existing_paths:
                                current_outputs.append(file)
                                existing_paths.append(file_path)
                        
                        current_step["output_filename"] = current_outputs
                    
                    # Update next step's input_filename
                    if next_step:
                        next_inputs = next_step.get("input_filename", [])
                        existing_paths = [f.split(": ")[0] if ": " in f else f for f in next_inputs]
                        
                        for file in new_output_files:
                            file_path = file.split(": ")[0] if ": " in file else file
                            if file_path not in existing_paths:
                                next_inputs.append(file)
                                existing_paths.append(file_path)
                        
                        next_step["input_filename"] = next_inputs
                    
                    # Save updated PLAN.json
                    with open(plan_path, 'w', encoding='utf-8') as plan_file:
                        json.dump(plan_data, plan_file, indent=4)
                except Exception as e:
                    analysis += f"\nError updating PLAN.json: {str(e)}"
        
        # 7. Update DEBUG_Output file
        # Maintain original stats unless file exists but is empty
        debug_output["analyze"] = debug_output.get("analyze", "") + f"\n\n{analysis}"
        if new_output_files:
            debug_output["output_filename"] = new_output_files
        
        with open(debug_output_path, 'w', encoding='utf-8') as out_file:
            json.dump(debug_output, out_file, indent=4)
        
        return {
            "analysis": analysis,
            "output_filename": new_output_files,
            "stats": model_stats and debug_output.get("stats", True)  # Return combined status
        }
