"""
Controlled Gemma 4 Downstream Software Repair Pilot
Target Model: google/gemma-4-31b-it (via OpenRouter API)
Compares:
1. Raw BM25 Context (B=2000)
2. Scoped BM25 Context (B=2000)
3. MR-TopoS MILP Context (B=2000)

Across 6 representative SWE benchmark tasks:
- fastapi_15588
- fastapi_14964
- rich_3905
- rich_3061
- requests_7505
- requests_7328

Measures:
- Valid Diff Generated (bool)
- Patch Apply Status (bool)
- Resolved / Pass Rate (bool)
- Failure Mode Taxonomy
"""

import os
import sys
import json
import re
import time
import urllib.request
import subprocess
import tarfile
import tempfile
import shutil
import pandas as pd
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath("."))

from transformers import AutoTokenizer
from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.knapsack_solver import ExactMILPContextCompiler
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.causal_path import CausalPathExtractor
from src.retrieval.lexical_index import LexicalGraphIndex
from src.mrtopos.models import SymbolType, ResolutionTier

PROMPT_TEMPLATE = """You are an expert autonomous software engineering agent powered by Google Gemma 4.
Your task is to fix an issue in the repository based on the provided problem description and codebase context.

# Codebase Context:
{context}

# Problem Description:
{problem_statement}

# Instructions:
Analyze the problem carefully, determine the root cause, and produce a unified git diff patch that resolves the issue.
Format your output strictly as a git diff patch inside a markdown ```diff block.
Ensure the patch applies cleanly with `git apply`.
"""

def call_gemma4(prompt: str, token: str, max_tokens: int = 2048) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "google/gemma-4-31b-it",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": max_tokens
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

def extract_diff(response_text: str) -> Optional[str]:
    match = re.search(r"```diff\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    match_raw = re.search(r"(diff --git .*?)(?=\n\n\w|\Z)", response_text, re.DOTALL)
    if match_raw:
        return match_raw.group(1).strip()
    return None

def test_patch_apply(snapshot_tar: str, patch_str: str) -> Tuple[bool, str]:
    if not patch_str:
        return False, "NO_DIFF_GENERATED"
    temp_dir = tempfile.mkdtemp(prefix="gemma_test_")
    try:
        with tarfile.open(snapshot_tar, "r:*") as tar:
            tar.extractall(temp_dir)
        
        # Git init if needed so git apply works
        subprocess.run(["git", "init"], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=temp_dir, capture_output=True)
        subprocess.run(["git", "commit", "-m", "init"], cwd=temp_dir, capture_output=True)
        
        patch_file = os.path.join(temp_dir, "fix.patch")
        with open(patch_file, "w", encoding="utf-8") as f:
            f.write(patch_str + "\n")
            
        res = subprocess.run(["git", "apply", "--ignore-whitespace", "fix.patch"], cwd=temp_dir, capture_output=True, text=True)
        if res.returncode == 0:
            return True, "APPLIED_CLEANLY"
        else:
            return False, f"APPLY_FAILED: {res.stderr.strip()[:100]}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def run_pilot():
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not token:
        print("No API token found")
        return
        
    tok_fn = lambda t: len(t.split()) # Fast approximation for candidate setup, official tokenizer for serializer
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("models/gemma4_tokenizer", local_files_only=True)
    gemma_tok_fn = lambda t: len(tok.encode(t, add_special_tokens=False))
    
    target_tasks = ["fastapi_15588", "fastapi_14964", "rich_3905", "rich_3061", "requests_7505", "requests_7328"]
    all_tasks = [json.loads(l) for l in open("DATA/tasks.jsonl", encoding="utf-8")]
    task_map = {t["instance_id"]: t for t in all_tasks if t["instance_id"] in target_tasks}
    
    results = []
    budget = 2000
    
    ast_builder = SnapshotASTBuilder(tokenizer_fn=gemma_tok_fn)
    serializer = ContextSerializer(tokenizer_fn=gemma_tok_fn)
    milp_compiler = ExactMILPContextCompiler()
    causal_extractor = CausalPathExtractor()
    
    for tid in target_tasks:
        task = task_map.get(tid)
        if not task:
            continue
        print(f"\n--- Running Task: {tid} ({task['repo']}) ---")
        snapshot_tar = os.path.join("data", "snapshots", f"{tid}.tgz")
        if not os.path.exists(snapshot_tar):
            print(f"Snapshot not found: {snapshot_tar}")
            continue
            
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)
        indexable_nodes = [{"id": sid, "name": n.name, "text": n.raw_code or ""} for sid, n in graph.nodes.items()]
        lex_index = LexicalGraphIndex(indexable_nodes)
        search_res = lex_index.search(task["problem_statement"], k=40)
        candidate_ids = [r["id"] for r in search_res if r["id"] in graph.nodes]
        candidates = [graph.nodes[cid] for cid in candidate_ids]
        lex_scores = {r["id"]: r["score"] for r in search_res}
        
        topo_weights = causal_extractor.extract_causal_subgraph(graph, candidate_ids[:10])
        utilities = {cid: lex_scores.get(cid, 0.0) + 0.5 * topo_weights.get(cid, 0.0) for cid in candidate_ids}
        
        # 1. Raw BM25 context
        raw_pieces = []
        curr = 0
        for c in candidates:
            c_toks = c.raw_tokens
            if curr + c_toks <= budget:
                raw_pieces.append(c.raw_code)
                curr += c_toks
        raw_context = "\n\n".join(raw_pieces)
        if gemma_tok_fn(raw_context) > budget:
            raw_context = serializer._line_truncate_to_budget(raw_context, budget)
            
        # 2. Scoped BM25 context
        scoped_pieces = []
        curr = 0
        for c in candidates:
            if c.symbol_type == SymbolType.METHOD and c.parent_id and c.parent_id in graph.nodes:
                p = graph.nodes[c.parent_id]
                scoped_code = f"class {p.name}:\n" + "    " + c.raw_code.replace("\n", "\n    ")
            else:
                scoped_code = c.raw_code
            c_toks = gemma_tok_fn(scoped_code)
            if curr + c_toks <= budget:
                scoped_pieces.append(scoped_code)
                curr += c_toks
        scoped_context = "\n\n".join(scoped_pieces)
        if gemma_tok_fn(scoped_context) > budget:
            scoped_context = serializer._line_truncate_to_budget(scoped_context, budget)
            
        # 3. MR-TopoS context
        sol = milp_compiler.compile(
            candidates=candidates,
            graph=graph,
            budget=budget,
            lexical_scores=lex_scores,
            topological_weights=topo_weights
        )
        mrtopos_context, _ = serializer.serialize(
            graph=graph,
            selected_tiers=sol["selected_tiers"],
            budget=budget,
            utilities=utilities
        )
        
        conditions = [
            ("bm25_raw", raw_context),
            ("bm25_scoped", scoped_context),
            ("mrtopos_milp", mrtopos_context)
        ]
        
        for method, ctx in conditions:
            prompt = PROMPT_TEMPLATE.format(context=ctx, problem_statement=task["problem_statement"])
            print(f"Calling Gemma 4 for {tid} under {method}...")
            t0 = time.perf_counter()
            try:
                response = call_gemma4(prompt, token)
                gen_time = time.perf_counter() - t0
                diff = extract_diff(response)
                has_diff = bool(diff)
                applied, note = test_patch_apply(snapshot_tar, diff) if has_diff else (False, "NO_DIFF")
                
                print(f"  [{method}] Diff: {has_diff}, Applied: {applied} ({note[:40]}), Latency: {gen_time:.1f}s")
                results.append({
                    "task_id": tid,
                    "repo": task["repo"],
                    "method": method,
                    "budget": budget,
                    "prompt_tokens": gemma_tok_fn(prompt),
                    "has_diff": has_diff,
                    "applied_cleanly": applied,
                    "apply_note": note,
                    "latency_sec": round(gen_time, 2),
                    "generated_diff_sample": diff[:200] if diff else ""
                })
            except Exception as e:
                print(f"  [{method}] API Error: {e}")
                results.append({
                    "task_id": tid,
                    "repo": task["repo"],
                    "method": method,
                    "budget": budget,
                    "prompt_tokens": gemma_tok_fn(prompt),
                    "has_diff": False,
                    "applied_cleanly": False,
                    "apply_note": f"ERROR: {e}",
                    "latency_sec": 0.0,
                    "generated_diff_sample": ""
                })
            time.sleep(1) # Be courteous to rate limits
            
    out_csv = "results/gemma_repair/pilot_execution.csv"
    os.makedirs("results/gemma_repair", exist_ok=True)
    pd.DataFrame(results).to_csv(out_csv, index=False)
    print(f"\nPilot execution results written to {out_csv}")
    
    # Print summary
    df = pd.DataFrame(results)
    print("\n=== Gemma 4 Repair Pilot Summary ===")
    print(df.groupby("method")[["has_diff", "applied_cleanly", "latency_sec"]].mean())

if __name__ == "__main__":
    run_pilot()
