"""
Unit tests for Multi-Turn Developer Agent Framework and Hermetic Sandbox.
Verifies that iterative block editing completely eliminates line-drift failure modes.
"""

import os
import shutil
import tempfile
import pytest

from experiments.multi_turn_agent.agent_loop import (
    HermeticRepositorySandbox,
    MultiTurnDeveloperAgent,
)


@pytest.fixture
def temp_sandbox_repo():
    temp_dir = tempfile.mkdtemp()
    # Initialize mock git repository
    os.system(f"git init -q {temp_dir}")

    # Create sample Python source file
    sample_file = os.path.join(temp_dir, "calculator.py")
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write('''def add(a: int, b: int) -> int:
    return a - b  # Bug: subtraction instead of addition

def multiply(a: int, b: int) -> int:
    return a * b
''')

    # Commit initial state
    cwd = os.getcwd()
    os.chdir(temp_dir)
    os.system("git add calculator.py")
    os.system('git -c user.name="Test" -c user.email="test@test.com" commit -q -m "Initial commit"')
    os.chdir(cwd)

    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_01_sandbox_block_editing(temp_sandbox_repo):
    sandbox = HermeticRepositorySandbox(temp_sandbox_repo)

    # 1. Read file
    content = sandbox.read_file("calculator.py")
    assert "return a - b" in content

    # 2. Block edit
    target = "    return a - b  # Bug: subtraction instead of addition"
    replacement = "    return a + b  # Fixed: addition"
    success, msg = sandbox.apply_block_edit("calculator.py", target, replacement)

    assert success is True
    assert "SUCCESS" in msg

    # 3. Verify content
    updated = sandbox.read_file("calculator.py")
    assert "return a + b" in updated
    assert "return a - b" not in updated

    # 4. Extract diff
    patch = sandbox.extract_patch()
    assert "-    return a - b" in patch
    assert "+    return a + b" in patch


def test_02_multi_turn_agent_trajectory(temp_sandbox_repo):
    sandbox = HermeticRepositorySandbox(temp_sandbox_repo)
    agent = MultiTurnDeveloperAgent(
        sandbox=sandbox,
        context_str="# Sample MR-AST Context: calculator.py\ndef add(a: int, b: int) -> int: ...",
        problem_statement="Function add returns incorrect result due to subtraction operator.",
    )

    # Turn 1: View context
    obs1 = agent.execute_turn("view_context", {})
    assert "calculator.py" in obs1

    # Turn 2: Read target file
    obs2 = agent.execute_turn("read_file", {"file_path": "calculator.py"})
    assert "def add" in obs2

    # Turn 3: Apply fix
    obs3 = agent.execute_turn(
        "edit_block",
        {
            "file_path": "calculator.py",
            "target": "return a - b",
            "replacement": "return a + b",
        },
    )
    assert "SUCCESS" in obs3

    # Turn 4: Submit
    obs4 = agent.execute_turn("submit", {})
    assert obs4 == "SUBMITTED"

    assert len(agent.trajectory) == 4
    patch = sandbox.extract_patch()
    assert "+    return a + b" in patch

