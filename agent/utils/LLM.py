import time

from openai import OpenAI
import openai
from groq import AsyncGroq


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

    def call_chatgpt_api(self, prompt:list):
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
                temperature=chat_gpt["temperature"]
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

        