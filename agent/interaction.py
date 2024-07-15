import argparse, yaml, asyncio
from Agent.agent import Agent
import os
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

parser = argparse.ArgumentParser(description='Process config.')
parser.add_argument('--config', '-c', type=str, default="./config/config.yaml", help='path to config file')
args = parser.parse_args()

with open(args.config, 'r') as f:
    config = yaml.load(f, Loader=yaml.Loader)

config['interaction_mode'] = True
config['Agent']['ChatGPT_1']['api_keys'] = [os.environ['OPENAI_API_KEY']]
agent = Agent(config)
while True:
    instruction = input('Enter your instruction: \n')
    asyncio.run(agent.Instruction('', instruction, file=config['path']['source_path']))