import pathlib
import time
import yaml

from Agent.xwAPI import xwBackend
from utils.construct_prompt import get_api_doc


class Prompt:
    def __init__(
        self,
        agent_configuration,
        agent_name,
        model_name,
        config_file="./config/config.yaml",
        output_path="../benchmark_dir",
        few_shot_count=10,
    ):
        self.few_shot_count = few_shot_count
        self.agent_name = agent_name
        self.model_name = model_name
        self.agent_config = agent_configuration
        self.config_file = config_file
        self.output_path = output_path

    def get_few_shot_count(self):
        return self.few_shot_count

    def create_path_generator(self, file_path):
        return pathlib.Path(f"{file_path}").glob("**/*")

    def get_source_excel_filenames(self, path_generator):
        response_paths = [
            str(path).split("\\")[-1] for path in path_generator if path.is_file()
        ]
        return [f"{log_file.split('_')[-1][:-5]}.xlsx" for log_file in response_paths]

    def get_filepaths(self):
        input_path_generator = self.create_path_generator(
            file_path=f"{self.output_path}/refined_responses/"
        )
        input_filepaths = [str(path) for path in input_path_generator]
        excel_path_generator = self.create_path_generator(
            file_path=f"{self.output_path}/refined_responses/"
        )
        excel_filenames = self.get_source_excel_filenames(
            path_generator=excel_path_generator
        )
        excel_filepaths = [
            f"../dataset/task_sheets/{filename}" for filename in excel_filenames
        ]

        response_path_generator = self.create_path_generator(
            file_path=f"{self.output_path}/intermediate_responses/"
        )
        response_filepaths = [str(path) for path in response_path_generator]

        return {
            "excel": excel_filepaths,
            "input": input_filepaths,
            "response": response_filepaths,
        }

    def get_api_documentation(self):
        with open(self.agent_config["api_doc_path"]) as f:
            api_doc = yaml.load(f, Loader=yaml.FullLoader)
        return api_doc

    def get_excel_backend(self):
        api_doc = self.get_api_documentation()
        if self.agent_config["API_backend"] == "xw":
            xw_backend = xwBackend(self.agent_config["APP_backend"], api_doc)
        return xw_backend

    def get_sheet_state(self, filepath):
        backend = self.get_excel_backend()
        if filepath is not None:
            time.sleep(0.5)
            backend.OpenWorkbook(filepath)
        return backend.GetSheetsState()

    def extract_input_function_docs(self, input_filepath):
        # Get detailed full documentation of xwAPI
        with open(input_filepath) as file:
            input_functions = yaml.load(file, Loader=yaml.Loader)
        prompt_format = self.agent_config["ChatGPT_1"]["prompt_format"]
        api_doc = self.get_api_documentation()
        _, _, api_detail_doc = get_api_doc(prompt_format, api_doc)

        # Flatten the 2D list of functions
        input_functions["refined_response"] = [
            item for sublist in input_functions["refined_response"] for item in sublist
        ]
        # Filter upto first open paranthesis of input functions
        unique_input_functions = set(
            [
                function[: function.find("(")]
                for function in input_functions["refined_response"]
            ]
        )

        # Extract docs of unique input functions
        input_function_docs = [api_detail_doc[name] for name in unique_input_functions if name in api_detail_doc.keys()]
        return input_function_docs

    def get_input_functions(self, input_filepath):
        with open(input_filepath) as file:
            input_functions = yaml.load(file, Loader=yaml.Loader)
        return yaml.dump(input_functions["refined_response"])

    def get_correct_summarization(self, correct_filepath):
        with open(correct_filepath) as file:
            correct_summarizations = yaml.load(file, Loader=yaml.Loader)
        return yaml.dump(correct_summarizations["intermediate response"])

    def create_few_shot_examples(self):
        few_shot_examples = []
        filepaths = self.get_filepaths()
        for example_index in range(self.few_shot_count):
            # Paths
            example_source_path = filepaths["excel"][example_index]
            example_input_path = filepaths["input"][example_index]
            example_response_path = filepaths["response"][example_index]

            # Few-shot example information
            example_sheet_state = self.get_sheet_state(example_source_path)
            example_doc = self.extract_input_function_docs(example_input_path)
            example_input = self.get_input_functions(example_input_path)
            example_response = self.get_correct_summarization(example_response_path)

            few_shot_examples.append(
                {
                    "role": "user",
                    "content": (
                        f"{example_input}\n"
                        "Here is the supplementary documentation you can reference:\n"
                        f"{example_doc}\n"
                        "Here is the corresponding sheet state:\n"
                        f"{example_sheet_state}\n\n"
                    ),
                }
            )
            few_shot_examples.append(
                {"role": "assistant", "content": f"{example_response}\n"}
            )
        return few_shot_examples

    def create_actual_prompt(self, index):
        filepaths = self.get_filepaths()

        # Paths
        source_path = filepaths["excel"][index]
        input_path = filepaths["input"][index]
        response_path = filepaths["response"][index]

        # Actual information
        sheet_state = self.get_sheet_state(source_path)
        documentation = self.extract_input_function_docs(input_path)
        input_ = self.get_input_functions(input_path)

        system_prompt = {}
        if (self.agent_name == "ChatGPT_1") or (self.agent_name == "ChatGPT_2"):
            system_prompt["role"] = "developer"
        else:
            system_prompt["role"] = "system"

        system_prompt["content"] = (
            "Summarize the each sub-step of instructions into explanations in natural language.\n"
            "Be brief and do not provide verbose explanations.\n"
            "Do not add text formatting such as bold, italic.\n"
            "Do not provide extra notes or postscriptum.\n"
            "Avoid redundant steps and provide minimal steps\n\n"
        )

        user_promopt = {
            "role": "user",
            "content": (
                f"{input_}\n"
                "Here is the supplementary documentation you can reference:\n"
                f"{documentation}\n"
                "Here is the corresponding sheet state:\n"
                f"{sheet_state}\n\n"
            ),
        }

        return system_prompt, user_promopt
