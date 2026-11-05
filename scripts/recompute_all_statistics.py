import os
import json
import re
import numpy as np
import pandas as pd
from scipy import stats

def main():
    tasks = []
    with open('data/tasks.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                tasks.append(json.loads(line))

    task_map = {}
    for t in tasks:
        tid = t['instance_id']
        patch = t.get('patch', '')
        diffs = re.split(r'\n(?=diff --git |--- )', patch)
        pre = []
        new = []
        for d in diffs:
            m = re.search(r'\+\+\+ b/(.+?)\n', d)
            if m:
                fp = m.group(1).strip()
                if fp != '/dev/null':
                    if '--- /dev/null' in d or re.search(r'@@ -0,0 ', d):
                        new.append(fp)
                    else:
                        pre.append(fp)
        task_map[tid] = {
            'all_gold': list(set(pre + new)),
            'pre': list(set(pre)),
            'new': list(set(new)),
            'repo': t.get('repo', '')
        }

    df = pd.read_csv('results/final_benchmark/per_task.csv')

    results = {}

    for b in [2000, 4000, 8000, 16000]:
        df_b = df[df['budget'] == b]
        scoped = df_b[df_b['method'] == 'bm25_scoped'].sort_values('task_id')
        milp = df_b[df_b['method'] == 'mrtopos_milp'].sort_values('task_id')
        
        # 1. Macro Recall All (N=129)
        s_all = scoped['gold_file_recall'].values
        m_all = milp['gold_file_recall'].values
        diff_all = m_all - s_all
        t_stat_all, p_val_all = stats.ttest_rel(m_all, s_all)
        non_zero_diff_all = diff_all[diff_all != 0]
        if len(non_zero_diff_all) > 0:
            w_res = stats.wilcoxon(non_zero_diff_all)
            w_pval_all = float(w_res.pvalue)
            w_stat_all = float(w_res.statistic)
        else:
            w_pval_all = 1.0
            w_stat_all = 0.0
            
        std_all = float(np.std(diff_all, ddof=1))
        mean_diff_all = float(np.mean(diff_all))
        ci_all = stats.t.interval(0.95, df=len(diff_all)-1, loc=mean_diff_all, scale=std_all/np.sqrt(len(diff_all)))

        # 2. Pre-existing Recall (N=128, excluding 1 task with 0 pre-existing files)
        task_ids = milp['task_id'].values
        pre_s = []
        pre_m = []
        for tid, rs, rm in zip(task_ids, s_all, m_all):
            n_all = len(task_map[tid]['all_gold'])
            n_pre = len(task_map[tid]['pre'])
            if n_pre > 0:
                hits_s = round(rs * n_all)
                hits_m = round(rm * n_all)
                pre_s.append(hits_s / n_pre)
                pre_m.append(hits_m / n_pre)
        
        pre_s = np.array(pre_s)
        pre_m = np.array(pre_m)
        diff_pre = pre_m - pre_s
        t_stat_pre, p_val_pre = stats.ttest_rel(pre_m, pre_s)
        non_zero_diff_pre = diff_pre[diff_pre != 0]
        if len(non_zero_diff_pre) > 0:
            w_res_pre = stats.wilcoxon(non_zero_diff_pre)
            w_pval_pre = float(w_res_pre.pvalue)
            w_stat_pre = float(w_res_pre.statistic)
        else:
            w_pval_pre = 1.0
            w_stat_pre = 0.0
            
        std_pre = float(np.std(diff_pre, ddof=1))
        mean_diff_pre = float(np.mean(diff_pre))
        ci_pre = stats.t.interval(0.95, df=len(diff_pre)-1, loc=mean_diff_pre, scale=std_pre/np.sqrt(len(diff_pre)))

        results[b] = {
            "all_references_129_tasks": {
                "scoped_mean": float(np.mean(s_all)),
                "milp_mean": float(np.mean(m_all)),
                "mean_difference": mean_diff_all,
                "relative_improvement": float((np.mean(m_all) - np.mean(s_all)) / np.mean(s_all)),
                "t_statistic": float(t_stat_all),
                "p_value_t": float(p_val_all),
                "p_value_wilcoxon": w_pval_all,
                "cohens_d": float(mean_diff_all / std_all) if std_all > 0 else 0.0,
                "ci_95": [float(ci_all[0]), float(ci_all[1])]
            },
            "preexisting_references_128_tasks": {
                "scoped_mean": float(np.mean(pre_s)),
                "milp_mean": float(np.mean(pre_m)),
                "mean_difference": mean_diff_pre,
                "relative_improvement": float((np.mean(pre_m) - np.mean(pre_s)) / np.mean(pre_s)),
                "t_statistic": float(t_stat_pre),
                "p_value_t": float(p_val_pre),
                "p_value_wilcoxon": w_pval_pre,
                "cohens_d": float(mean_diff_pre / std_pre) if std_pre > 0 else 0.0,
                "ci_95": [float(ci_pre[0]), float(ci_pre[1])]
            }
        }

    with open('results/statistics/statistical_reanalysis.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Reanalysis complete:")
    print(json.dumps(results, indent=2))

if __name__ == '__main__':
    main()

