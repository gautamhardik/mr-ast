"""
Parse Task 3018 Gemma 4 Repair Execution Output and save to CSV.
"""
import os
import re
import pandas as pd

log_path = r"C:\Users\hiten\.gemini\antigravity\brain\bcb8822d-5e62-4199-8766-fbe0c3955413\.system_generated\tasks\task-3018.log"

records = []
current_task = None
current_repo = None

# We know the 6 tasks and repos:
task_meta = {
    "fastapi_15588": "fastapi/fastapi",
    "fastapi_14964": "fastapi/fastapi",
    "rich_3905": "Textualize/rich",
    "rich_3061": "Textualize/rich",
    "requests_7505": "psf/requests",
    "requests_7328": "psf/requests"
}

with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for line in lines:
    m_task = re.search(r"--- Running Task: (\w+) \((.*?)\) ---", line)
    if m_task:
        current_task = m_task.group(1)
        current_repo = m_task.group(2)
        continue
        
    m_res = re.search(r"\[(\w+)\] Diff: (\w+), Applied: (\w+) \((.*?)\), Latency: ([\d\.]+)s", line)
    if m_res and current_task:
        method = m_res.group(1)
        has_diff = m_res.group(2) == "True"
        applied = m_res.group(3) == "True"
        note = m_res.group(4)
        lat = float(m_res.group(5))
        records.append({
            "task_id": current_task,
            "repo": current_repo,
            "method": method,
            "budget": 2000,
            "has_diff": has_diff,
            "applied_cleanly": applied,
            "apply_note": note,
            "latency_sec": lat
        })

df = pd.DataFrame(records)
os.makedirs("results/gemma_repair", exist_ok=True)
out_csv = "results/gemma_repair/pilot_execution.csv"
df.to_csv(out_csv, index=False)
print(f"Saved {len(df)} records to {out_csv}")
print(df.to_string())

summary = df.groupby("method")[["has_diff", "applied_cleanly", "latency_sec"]].agg(["mean", "count"])
print("\n=== Aggregated Pilot Summary ===")
print(summary)

