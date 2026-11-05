"""
Downstream Gemma 4 Autonomous Software Repair Evaluation Pipeline.
Evaluates SWE-bench task resolution rates across compiled context methods.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.getcwd())

import urllib.request
from transformers import AutoTokenizer

from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.causal_path import CausalPathExtractor
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.knapsack_solver import (
    ConstraintAwareGreedyContextCompiler,
    ExactMILPContextCompiler,
)
from src.mrtopos.models import DualViewGraph, ResolutionTier, SymbolNode
from src.retrieval.lexical_index import LexicalGraphIndex


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


def call_vllm_api(endpoint_url: str, prompt: str, max_tokens: int = 4096) -> str:
    """Send prompt to vLLM OpenAI-compatible completion endpoint."""
    url = f"{endpoint_url}/chat/completions" if not endpoint_url.endswith("/chat/completions") else endpoint_url
    payload = json.dumps({
        "model": "google/gemma-4-31B-it-qat-w4a16-ct",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]


def extract_diff_block(response_text: str) -> Optional[str]:
    """Extract unified diff content from LLM response."""
    match = re.search(r"```diff\n(.*?)\n```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback: search for diff header directly
    match_raw = re.search(r"(diff --git .*?)(?=\n\n\w|\Z)", response_text, re.DOTALL)
    if match_raw:
        return match_raw.group(1).strip()
    return None


def run_test_harness(repo_dir: str, patch_str: str, test_cmd: str) -> Tuple[bool, str]:
    """Apply patch to target repository and execute test suite."""
    patch_file = os.path.join(repo_dir, "proposed_fix.patch")
    with open(patch_file, "w", encoding="utf-8") as f:
        f.write(patch_str + "\n")

    # Try applying with git apply
    apply_res = subprocess.run(
        ["git", "apply", "--ignore-whitespace", "proposed_fix.patch"],
        cwd=repo_dir,
        capture_output=True,
        text=True
    )
    if apply_res.returncode != 0:
        return False, f"PATCH_APPLY_FAILED: {apply_res.stderr.strip()}"

    # Execute test suite
    test_res = subprocess.run(
        test_cmd,
        shell=True,
        cwd=repo_dir,
        capture_output=True,
        text=True,
        timeout=180
    )
    passed = (test_res.returncode == 0)
    note = "RESOLVED" if passed else f"TESTS_FAILED (exit {test_res.returncode})"
    return passed, note


def main():
    parser = argparse.ArgumentParser(description="Downstream Gemma 4 Repair Benchmark Harness")
    parser.add_argument("--vllm_url", type=str, default="http://localhost:8000/v1")
    parser.add_argument("--tasks_file", type=str, default="data/tasks.jsonl")
    parser.add_argument("--budgets", nargs="+", type=int, default=[2000, 4000])
    parser.add_argument("--methods", nargs="+", type=str, default=["mrtopos_milp", "bm25_scoped"])
    parser.add_argument("--output_dir", type=str, default="results/gemma_repair")
    parser.add_argument("--dry_run", action="store_true", help="Simulate execution without vLLM endpoint")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    print(f"Loaded configuration: Budgets={args.budgets}, Methods={args.methods}, DryRun={args.dry_run}")


if __name__ == "__main__":
    main()

