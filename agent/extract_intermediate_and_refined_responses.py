# %%
import yaml
import pathlib

# %%
evaluation_config_file = "../output_dir/eval_result.yaml"
with open(evaluation_config_file, mode='r') as file:
    eval_config = yaml.load(file, Loader=yaml.Loader)

# %%
repeat_number = 1
successful_list = eval_config["check_result_each_repeat"][repeat_number]["success_list"].split(',')
successful_list = [instance.strip() for instance in successful_list]
successful_list

# %%
def load_success_log(task_name):
    log_file_path = f"../output_dir/{task_name}/{task_name}_log.yaml"
    with open(log_file_path, mode="r") as file:
        log_file = yaml.load(file, Loader=yaml.Loader)
    return log_file

# %%
def extract_intermediate_responses(log_file):
    intermediate_response = log_file["Success Response"][0]["intermediate response"]
    intermediate_response = [sub_step[:sub_step.find("\nAction API: ")] for sub_step in intermediate_response]
    intermediate_response_dict = {"intermediate response": intermediate_response}
    return intermediate_response_dict

# %%
def save_dictionary(save_path, task_name, dictionary):
    pathlib.Path(f"{save_path}").mkdir(parents=True, exist_ok=True)
    with open(f"{save_path}/{task_name}.yaml", mode="w") as file:
        yaml.dump(dictionary, file, default_flow_style=False)

# %%
def extract_refined_responses(log_file):
    refined_response = log_file["Success Response"][0]["refined response"]
    refined_response = [code_segment[0] for code_segment in refined_response]
    refined_response_dict = {"refined_response": refined_response}
    return refined_response_dict

# %%
for success_task_name in successful_list:
    log_file = load_success_log(success_task_name)
    intermediate_response_dict = extract_intermediate_responses(log_file)
    refined_response_dict = extract_refined_responses(log_file)
    save_dictionary(save_path="../output_dir/intermediate_responses", task_name=success_task_name, dictionary=intermediate_response_dict)
    save_dictionary(save_path="../output_dir/refined_responses", task_name=success_task_name, dictionary=refined_response_dict)

# %%


