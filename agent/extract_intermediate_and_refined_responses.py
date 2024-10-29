# %%
import yaml
import pathlib
import pandas as pd

OUTPUT_DIR = "../output_dir"
DATA_PATH = "../dataset/dataset_158_copy.xlsx"
# %%
evaluation_config_file = f"{OUTPUT_DIR}/eval_result.yaml"
with open(evaluation_config_file, mode='r') as file:
    eval_config = yaml.load(file, Loader=yaml.Loader)

# %%
repeat_number = 1
successful_list = eval_config["check_result_each_repeat"][repeat_number]["success_list"].split(',')
successful_list = [instance.strip() for instance in successful_list]
successful_list

# %%
def load_success_log(task_name):
    log_file_path = f"{OUTPUT_DIR}/{task_name}/{task_name}_log.yaml"
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
def get_new_task_name(task_name):
    row_index = int(task_name.split('_')[0]) - 1
    tasks = pd.read_excel(DATA_PATH)
    task_no = tasks.iloc[row_index]["No."]
    new_task_name = "_".join([str(task_no), task_name.split('_')[1]])
    return new_task_name


# %%
def save_dictionary(save_path, task_name, dictionary):
    pathlib.Path(f"{save_path}").mkdir(parents=True, exist_ok=True)
    new_task_name = get_new_task_name(task_name)
    with open(f"{save_path}/{new_task_name}.yaml", mode="w") as file:
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
    save_dictionary(save_path=f"{OUTPUT_DIR}/intermediate_responses", task_name=success_task_name, dictionary=intermediate_response_dict)
    save_dictionary(save_path=f"{OUTPUT_DIR}/refined_responses", task_name=success_task_name, dictionary=refined_response_dict)

# %%



