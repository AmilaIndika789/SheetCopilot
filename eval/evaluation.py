from compare_sheets import compare_workbooks
import tqdm
import yaml
import pandas as pd
import os
import time
import numpy as np
from datetime import datetime
import argparse

def evaluate(save_path, repeat_num):
    dataset_dir = "../dataset"
    task_path = os.path.join(dataset_dir, "dataset.xlsx")
    gt_path = os.path.join(dataset_dir, "task_sheet_answers")

    eval_result_path = os.path.join(save_path, 'eval_result1.yaml')

    if os.path.exists(eval_result_path):
        with open(eval_result_path, 'r') as f:
            eval_result = yaml.load(f, Loader=yaml.Loader)
    else:
        eval_result = {"check_result_each_repeat": {}}

    task_df = pd.read_excel(task_path, header=0)

    print("\033[0;36;40m========================================================\nEvaluate task result: {}\033[0m\n".format(save_path))
    
    for repeat_id in range(1, repeat_num + 1):
        t = time.time()
        if eval_result["check_result_each_repeat"].get(repeat_id, None) is None:
            eval_result["check_result_each_repeat"][repeat_id] = {
                "matched_gt_lst": [],
                "checked_list": [],
                "exec_success_list": [],
                "success_list": [],
                "gt_min_action_cnt_list": [],
                "action_cnt_list": [],
                "query_cnt_list": [],
                "query_wo_retry_cnt_list": [],
                "check_result_list": [],
                "error_log": [],
                "eval_results": {}
            }

        check_result = eval_result["check_result_each_repeat"][repeat_id]

        # number of tasks to evaluate
        num_tasks = len([x for x in os.listdir(save_path) if os.path.isdir(os.path.join(save_path, x))])

        remaining_task_cnt = max(0, num_tasks - len(check_result["checked_list"]))
        
        with tqdm.tqdm(total=remaining_task_cnt, desc=f"Processing the remaining {remaining_task_cnt}/{num_tasks} results of repeat {repeat_id}") as pbar:
            for index, row in task_df.iloc[:].iterrows():
                # Result file
                task_name = f"{row['No.']}_{row['Sheet Name']}"

                if task_name in check_result["checked_list"]: continue

                task_path = os.path.join(save_path, task_name)
                if not os.path.exists(task_path):
                    continue
                res_path = os.path.join(task_path, f"{task_name}_{repeat_id}.xlsx") #Claude

                # Load the running log of the task
                log_file = os.path.join(task_path, "{}_log.yaml".format(os.path.basename(task_path)))

                with open(log_file, 'r') as f:
                    log = yaml.load(f, yaml.Loader)

                # Check if the result xlsx file exists
                res_file_exists = os.path.exists(res_path)

                # Check if the number of result files equals log["Success Count"]
                equal = len([x for x in os.listdir(task_path) if x.endswith('.xlsx') and "source" not in x]) == log["Success Count"]

                if log["Success Count"] > 0 and res_file_exists and equal:
                    check_result["exec_success_list"].append(task_name)

                if os.path.exists(log_file) and 'conditional' not in row['Atomic actions'].lower() and res_file_exists and equal:
                    # Compare the result with all reference solutions.
                    # All reference solutions for one task is placed under a folder with the same name.

                    # Load GTs
                    gt_folder_this_task = os.path.join(gt_path, row['Sheet Name'], f"{row['No.']}_{row['Sheet Name']}")

                    for gt_file in [x for x in os.listdir(gt_folder_this_task) if x.endswith('.xlsx') and "$" not in x]:
                        gt = os.path.join(gt_folder_this_task, gt_file)
                        check_board = os.path.join(gt_folder_this_task, gt_file.replace(".xlsx", "_check.yaml"))

                        with open(check_board, 'r') as f:
                            check_board = yaml.load(f, Loader=yaml.Loader)

                        if not os.path.exists(gt):
                            check_result["error_log"].append("{} not exists".format(os.path.basename(res_path))) 
                            continue
                        
                        """
                        Comparing.......
                        """
                        check_res = compare_workbooks(gt, res_path, check_board["check_board"])


                        # If checking is successful
                        if check_res[1] and len(log["Success Response"]) > 0:
                            check_result["success_list"].append(task_name)

                            # Count actions
                            num_acts = 0
                            plan = log["Success Response"][repeat_id - 1]["refined response"]
                            for steps in plan:
                                num_acts += len(steps)
                            check_result["action_cnt_list"].append(num_acts)

                            # Count queries
                            # context_log_dir = "context_log" # for Claude
                            context_log_dir =  f"{os.path.basename(task_path)}_{repeat_id}"

                            context_logs = os.listdir(os.path.join(task_path, context_log_dir))

                            check_result["query_cnt_list"].append(len(context_logs))

                            # Count the number of actions without regarding re-trying
                            final_context_log_file = os.path.join(task_path, context_log_dir, "context_log_{}.yaml".format(len(context_logs)))
                            with open(final_context_log_file, 'r') as f:
                                final_context_log = yaml.load(f, Loader=yaml.Loader)
                            
                            query_wo_retry_set = set()
                            for query_i in range(12, len(final_context_log)):
                                content = final_context_log[query_i]["content"]
                                if content.startswith("Step"):
                                    query_wo_retry_set.add(content[:content.find(".")])
                            
                            query_wo_retry_cnt = len(query_wo_retry_set)  + 1 # step + 1 represents the last response "Done!"

                            check_result["query_wo_retry_cnt_list"].append(query_wo_retry_cnt)
                            assert check_result["query_wo_retry_cnt_list"][-1] <= check_result["query_cnt_list"][-1], f"{final_context_log_file} error"

                            # Count the minimum number of actions among Gts
                            gt_actions = [x for x in row['Atomic actions'].split(',') if "function" not in x]
                            check_result["gt_min_action_cnt_list"].append(len(gt_actions))
                            check_result["matched_gt_lst"].append(gt_file)
                            break

                    with open(eval_result_path, 'w') as f:
                        yaml.dump(eval_result, f)
                
                check_result["checked_list"].append(task_name)

                pbar.update(1)

        print("\033[0;33;40mEvaluation for Repeat {} has finished. Time elapse: {:.2f}s\033[0m".format(repeat_id, time.time() - t))

        if len(check_result["error_log"]) > 0:
            print("Error Log: {}\n".format('\n'.join(x for x in check_result["error_log"])))
        
        exec_success_cnt, success_cnt, total = len(check_result["exec_success_list"]), len(check_result["success_list"]), len(check_result["checked_list"])
        action_cnt_list, gt_min_action_cnt_list = np.array(check_result["action_cnt_list"]), np.array(check_result["gt_min_action_cnt_list"])
        query_cnt_list, query_wo_retry_cnt_list =  np.array(check_result["query_cnt_list"]), np.array(check_result["query_wo_retry_cnt_list"])

        check_result["eval_results"]["Total"] = total
        check_result["eval_results"]["Exec@1"] = exec_success_cnt / total
        check_result["eval_results"]["Pass@1"] = success_cnt / total

        # Action statistics
        check_result["eval_results"]["A_mean"] = np.mean(action_cnt_list).item()
        check_result["eval_results"]["A50"] = np.median(action_cnt_list / gt_min_action_cnt_list).item()
        check_result["eval_results"]["A90"] = np.percentile(action_cnt_list / gt_min_action_cnt_list, 90).item()

        # Query statistics
        check_result["eval_results"]["Q_mean"] = np.mean(query_cnt_list).item()
        check_result["eval_results"]["Q50"] = np.median(query_cnt_list / query_wo_retry_cnt_list).item()
        check_result["eval_results"]["Q90"] = np.percentile(query_cnt_list / query_wo_retry_cnt_list, 90).item()

        for k, v in check_result["eval_results"].items():
            print("{}: {}".format(k, v))
        
        print("========================================================\n")

        # Save the metrics to the eval_result and save it
        with open(eval_result_path, 'w') as f:
            yaml.dump(eval_result, f)

    print("{} have been evaluated ... . Time: {}".format(save_path, datetime.now().strftime("%H:%M:%S")))

parser = argparse.ArgumentParser(description='Process config.')
parser.add_argument('--result_dir', '-d', default="../results", type=str, help='path to the results folder')
parser.add_argument('--repeat_num', '-r', default=1, type=int, help='repeat numbers of each task')
args = parser.parse_args()

if __name__ == '__main__':
    evaluate(args.result_dir, args.repeat_num)
    print("Evaluate {}".format(args.result_dir))
