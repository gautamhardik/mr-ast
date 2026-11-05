"""
Multi-Turn SWE Developer Agent Framework with Dynamic MR-AST Context Memory.

Implements an iterative developer agent architecture:
- Working Memory: MR-AST dynamically compiles context within token budget B.
- Tool Interface:
    1. view_symbol(symbol_name): Inspect full source or skeleton
    2. edit_snippet(file_path, target_str, replacement_str): Exact block-replacement edit
    3. run_tests(): Executes task-specific pytest verification suite
    4. submit_solution(): Concludes trajectory and extracts clean git diff
- Resilient Multi-Turn Protocol: Replaces brittle single-turn diff generation
  with iterative edit-test-debug loops, eliminating line-offset drift.
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath("."))


@dataclass
class AgentTurn:
    turn_index: int
    action: str
    args: Dict[str, Any]
    observation: str
    execution_time_sec: float


class HermeticRepositorySandbox:
    """
    Manages isolated repository working copy for agent execution and testing.
    """

    def __init__(self, repo_dir: str):
        self.repo_dir = os.path.abspath(repo_dir)

    def read_file(self, file_path: str) -> str:
        full_path = os.path.join(self.repo_dir, file_path)
        if not os.path.exists(full_path):
            return f"ERROR: File not found: {file_path}"
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    def apply_block_edit(self, file_path: str, target: str, replacement: str) -> Tuple[bool, str]:
        """
        Applies exact string block replacement, eliminating line-number drift.
        """
        full_path = os.path.join(self.repo_dir, file_path)
        if not os.path.exists(full_path):
            return False, f"ERROR: File does not exist: {file_path}"

        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        if target not in content:
            return False, f"ERROR: Target block not found in {file_path}. Ensure exact match."

        count = content.count(target)
        if count > 1:
            return False, f"ERROR: Target block matches {count} occurrences in {file_path}. Ambiguous edit."

        new_content = content.replace(target, replacement, 1)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return True, f"SUCCESS: Modified {file_path} (replaced {len(target)} chars with {len(replacement)} chars)."

    def run_tests(self, test_cmd: str, timeout_sec: int = 60) -> Tuple[bool, str]:
        """
        Executes test command in sandbox.
        """
        try:
            res = subprocess.run(
                test_cmd,
                shell=True,
                cwd=self.repo_dir,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
            )
            passed = (res.returncode == 0)
            output = res.stdout if passed else (res.stderr + "\n" + res.stdout)
            return passed, output[:2000]  # truncate long logs
        except subprocess.TimeoutExpired:
            return False, "ERROR: Test execution timed out."
        except Exception as e:
            return False, f"ERROR: Test execution failed: {str(e)}"

    def extract_patch(self) -> str:
        """
        Extract clean git diff from sandbox.
        """
        res = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=self.repo_dir,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip()


class MultiTurnDeveloperAgent:
    """
    Autonomous multi-turn agent operating over MR-AST working memory.
    """

    def __init__(
        self,
        sandbox: HermeticRepositorySandbox,
        context_str: str,
        problem_statement: str,
        max_turns: int = 10,
    ):
        self.sandbox = sandbox
        self.context_str = context_str
        self.problem_statement = problem_statement
        self.max_turns = max_turns
        self.trajectory: List[AgentTurn] = []

    def execute_turn(self, action: str, args: Dict[str, Any]) -> str:
        """
        Dispatches agent tool action to sandbox or working memory.
        """
        turn_idx = len(self.trajectory) + 1
        obs = ""

        if action == "view_context":
            obs = self.context_str[:3000]
        elif action == "read_file":
            obs = self.sandbox.read_file(args.get("file_path", ""))
        elif action == "edit_block":
            success, msg = self.sandbox.apply_block_edit(
                args.get("file_path", ""),
                args.get("target", ""),
                args.get("replacement", ""),
            )
            obs = msg
        elif action == "run_tests":
            passed, test_log = self.sandbox.run_tests(args.get("test_cmd", "pytest -q"))
            obs = f"TESTS {'PASSED' if passed else 'FAILED'}:\n{test_log}"
        elif action == "submit":
            obs = "SUBMITTED"
        else:
            obs = f"UNKNOWN_ACTION: {action}"

        self.trajectory.append(
            AgentTurn(
                turn_index=turn_idx,
                action=action,
                args=args,
                observation=obs,
                execution_time_sec=0.1,
            )
        )
        return obs

