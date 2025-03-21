import time
import pathlib
import yaml

from openai import OpenAI
import openai
from groq import Groq
import groq


class LLM:
    def __init__(
        self,
        agent_configuration,
        agent_name,
        model_name,
        config_file="./config/config.yaml",
        output_path="../benchmark_dir",
    ):
        self.agent_name = agent_name
        self.model_name = model_name
        self.agent_config = agent_configuration
        self.config_file = config_file
        self.output_path = output_path

    def call_chatgpt_api(self, prompt: list):
        chat_gpt = self.agent_config[self.agent_name]
        client = OpenAI(
            api_key=chat_gpt["api_keys"][0],
            timeout=chat_gpt["timeout"],
            max_retries=chat_gpt["max_retries"],
        )
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=prompt,
                temperature=chat_gpt["temperature"],
            )
        except openai.OpenAIError as e:
            if isinstance(e, openai.RateLimitError):
                print("Rate limit exceeded. Retrying in 5 seconds...")
                time.sleep(5)
                return self.call_chatgpt_api(prompt)  # Retry
            elif isinstance(e, openai.APIConnectionError):
                print("Network error. Check your internet connection.")
            elif isinstance(e, openai.AuthenticationError):
                print("Authentication error. Check your API key.")
            else:
                print(f"Unexpected error: {e}")

        return response.choices[0].message.content

    def call_groq_api(self, prompt: list):
        groq_model = self.agent_config[self.agent_name]
        client = Groq(
            api_key=groq_model["api_keys"][0],
            timeout=groq_model["timeout"],
            max_retries=groq_model["max_retries"],
        )
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=prompt,
                temperature=groq_model["temperature"],
            )
            time.sleep(10)  # Workaround to avoid rate limit exceeding per minute
        except groq.APIConnectionError as e:
            print("The server could not be reached")
            print(e.__cause__)  # an underlying Exception, likely raised within httpx.
        except groq.RateLimitError as e:
            print("A 429 status code was received; we should back off a bit.")
        except groq.APIStatusError as e:
            print("Another non-200-range status code was received")
            print(e.status_code)
            print(e.response)

        return response.choices[0].message.content

    {
        ## Deprecated (TODO: Need to fix if planning to save the prompts)
        ## With the current implementation saving the prompts is not necessary
        # def save_prompt(self, prompt, test_input_file_path, agent_config, few_shot_count):
        #     prompt_filename = test_input_file_path.split('\\')[-1].split('.')[0] + '_prompt.txt'
        #     agent_name = agent_config["ChatGPT_1"]["model_name"]
        #     create_path_if_non_existing(f"{OUTPUT_PATH}/{agent_name}/prompts/{few_shot_count}_shot")
        #     with open(f"{OUTPUT_PATH}/{agent_name}/prompts/{few_shot_count}_shot/{prompt_filename}", "w") as file:
        #         file.write(prompt)
    }

    def create_path_if_non_existing(self, path):
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def save_response(self, predicted_instructions, test_input_path, few_shot_count):
        model_response_filename = (
            test_input_path.split("\\")[-1].split(".")[0] + "_response.yaml"
        )
        model_response = {f"{self.model_name}_response": predicted_instructions}
        self.create_path_if_non_existing(
            f"{self.output_path}/{self.model_name}/model_responses/{few_shot_count}_shot"
        )
        with open(
            f"{self.output_path}/{self.model_name}/model_responses/{few_shot_count}_shot/{model_response_filename}",
            "w",
        ) as file:
            yaml.dump(model_response, file)

    def save_prompt(self, prompt, test_input_path, few_shot_count):
        prompt_filename = test_input_path.split("\\")[-1].split(".")[0] + "_prompt.txt"
        self.create_path_if_non_existing(
            f"{self.output_path}/{self.model_name}/prompts/{few_shot_count}_shot"
        )
        with open(
            f"{self.output_path}/{self.model_name}/prompts/{few_shot_count}_shot/{prompt_filename}",
            "w",
        ) as file:
            for line in prompt:
                file.write(f"{line}\n")
