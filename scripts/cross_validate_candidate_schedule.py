import pandas as pd
import numpy as np

df_heldout = pd.read_csv('results/heldout_authoritative_matched_baselines.csv')
heldout_task_ids = set(df_heldout['task_id'].unique())

df_ledger = pd.read_csv('results/strategic_reset/experiment_ledger.csv')
all_task_ids = set(df_ledger['task_id'].unique())
dev_task_ids = all_task_ids - heldout_task_ids

# Filter for the 4 candidate pool conditions
# E_mrtopos_con_greedy is K=60
cond_map = {
    'E_mrtopos_con_greedy': 60,
    'saturation_K100': 100,
    'saturation_K200': 200,
    'saturation_K400': 400
}
df_k = df_ledger[df_ledger['condition'].isin(cond_map.keys())].copy()
df_k['K'] = df_k['condition'].map(cond_map)

print("=== 2-FOLD COMMIT-DISJOINT CROSS-VALIDATION OF CANDIDATE-DEPTH SCHEDULE ===")

for fold_name, train_ids, test_ids in [
    ("Fold 1 (Train on 63 Dev Tasks -> Test on 66 Heldout Tasks)", dev_task_ids, heldout_task_ids),
    ("Fold 2 (Train on 66 Heldout Tasks -> Test on 63 Dev Tasks)", heldout_task_ids, dev_task_ids)
]:
    print(f"\n--- {fold_name} ---")
    df_train = df_k[df_k['task_id'].isin(train_ids)]
    df_test = df_k[df_k['task_id'].isin(test_ids)]
    
    selected_schedule = {}
    for b in [2000, 4000, 8000, 16000]:
        train_means = df_train[df_train['budget'] == b].groupby('K')['gold_recall_all'].mean()
        best_k = train_means.idxmax()
        selected_schedule[b] = best_k
        print(f"  Budget {b}: Train Means: {dict(train_means.round(4))} -> Selected K={best_k}")
        
    print(f"  Resulting Selected Policy K(B): {selected_schedule}")
    
    # Evaluate policy on Test
    test_recalls = []
    for b in [2000, 4000, 8000, 16000]:
        k = selected_schedule[b]
        test_mean = df_test[(df_test['budget'] == b) & (df_test['K'] == k)]['gold_recall_all'].mean()
        test_recalls.append((b, k, test_mean))
        print(f"  Test Evaluation at Budget {b} (K={k}): Mean Recall = {test_mean*100:.2f}%")

