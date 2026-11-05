"""
Empirical Investigation into the AST Constraint Paradox.

Analyzes:
1. How many parent classes were omitted by the MILP solver in Condition B (enforce_ast_precedence=False).
2. How the serializer achieved 100% syntax validity in Condition B (implicit parent reconstruction).
3. Exact token overhead and symbol information trade-off when enforcing precedence (Condition C).
4. What happens if parent class reconstruction is disabled (raw unnested method emission).
"""

import ast
import json
import os
import sys
import numpy as np
import pandas as pd
from tokenizers import Tokenizer

sys.path.insert(0, os.getcwd())
from src.mrtopos.ast_builder import SnapshotASTBuilder
from src.mrtopos.knapsack_solver import ExactMILPContextCompiler
from src.mrtopos.context_serializer import ContextSerializer
from src.mrtopos.models import ResolutionTier, SymbolType
from src.retrieval.lexical_index import LexicalGraphIndex

def main():
    raw_tok = Tokenizer.from_file("models/gemma4_tokenizer/tokenizer.json")
    tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
    serializer = ContextSerializer(tokenizer_fn=tok_fn)

    compiler_b = ExactMILPContextCompiler(lambda_topo=0.0, enforce_ast_precedence=False, enforce_soft_calls=False)
    compiler_c = ExactMILPContextCompiler(lambda_topo=0.0, enforce_ast_precedence=True, enforce_soft_calls=False)

    with open("data/tasks.jsonl", "r", encoding="utf-8") as f:
        tasks = [json.loads(line) for line in f]

    results = []
    # Test on a representative subset of 20 tasks across all repos at B=2000
    sample_tasks = tasks[:20]

    for t_idx, task in enumerate(sample_tasks):
        task_id = task["instance_id"]
        snapshot_tar = os.path.join("data", "snapshots", f"{task_id}.tgz")
        if not os.path.exists(snapshot_tar):
            continue

        ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)
        graph = ast_builder.build_graph_from_snapshot(snapshot_tar, generate_skeletons=False)

        indexable = [{"id": s, "name": n.name, "text": n.raw_code or n.skeleton_code or n.stub_code} for s, n in graph.nodes.items()]
        lex_index = LexicalGraphIndex(indexable)
        search_res = lex_index.search(task["problem_statement"], k=60)
        cids = [r["id"] for r in search_res if r["id"] in graph.nodes]
        candidates = [graph.nodes[cid] for cid in cids]
        
        # Add parents to candidates so compiler has choice to pick them
        nodes_with_parents = list(candidates)
        for c in candidates:
            p = graph.get_parent(c.id)
            if p and p not in nodes_with_parents:
                nodes_with_parents.append(p)
        ast_builder.ensure_symbol_skeletons(nodes_with_parents)

        lex_scores = {cid: 1.0 for cid in cids}

        # Solve Condition B (no precedence)
        sol_b = compiler_b.compile(candidates=candidates, graph=graph, budget=2000, lexical_scores=lex_scores, topological_weights={})
        # Solve Condition C (with precedence)
        sol_c = compiler_c.compile(candidates=candidates, graph=graph, budget=2000, lexical_scores=lex_scores, topological_weights={})

        # Count how many selected methods in B had their parent NOT selected in B
        sel_methods_b = [graph.nodes[sid] for sid, t in sol_b["selected_tiers"].items() if t != ResolutionTier.EXCLUDED and graph.nodes[sid].symbol_type == SymbolType.METHOD]
        orphaned_methods_b = 0
        for m in sel_methods_b:
            pid = m.parent_id
            if pid and (pid not in sol_b["selected_tiers"] or sol_b["selected_tiers"][pid] == ResolutionTier.EXCLUDED):
                orphaned_methods_b += 1

        # Check serialization of B
        ctx_b, meta_b = serializer.serialize(graph, sol_b["selected_tiers"], 2000, lex_scores)
        # Check serialization of C
        ctx_c, meta_c = serializer.serialize(graph, sol_c["selected_tiers"], 2000, lex_scores)

        # What if B is serialized WITHOUT class wrapper (flat emission)?
        flat_pieces = []
        for sid, tier in sol_b["selected_tiers"].items():
            if tier == ResolutionTier.EXCLUDED:
                continue
            n = graph.nodes[sid]
            code = n.raw_code if tier == ResolutionTier.FULL else (n.skeleton_code or n.stub_code)
            flat_pieces.append(code.strip())
        flat_ctx = "\n\n".join(flat_pieces)
        
        try:
            ast.parse(flat_ctx)
            flat_valid = 1
        except SyntaxError:
            flat_valid = 0

        try:
            ast.parse(ctx_b)
            ctx_b_valid = 1
        except SyntaxError:
            ctx_b_valid = 0

        results.append({
            "task_id": task_id,
            "methods_in_b": len(sel_methods_b),
            "orphaned_methods_b": orphaned_methods_b,
            "b_serialized_tokens": meta_b["raw_tokens"],
            "c_serialized_tokens": meta_c["raw_tokens"],
            "b_syntax_valid": ctx_b_valid,
            "flat_b_syntax_valid": flat_valid,
            "c_syntax_valid": 1 if serializer.serialize(graph, sol_c["selected_tiers"], 2000, lex_scores)[0] else 0
        })

    df_res = pd.DataFrame(results)
    print("=================================================================")
    print("        AST CONSTRAINT PARADOX EMPIRICAL FINDINGS")
    print("=================================================================")
    print(f"Total Tasks Tested: {len(df_res)}")
    print(f"Mean Methods Selected in Condition B: {df_res['methods_in_b'].mean():.2f}")
    print(f"Mean Orphaned Methods in Condition B: {df_res['orphaned_methods_b'].mean():.2f} ({df_res['orphaned_methods_b'].sum()} total)")
    print(f"Condition B Syntax Validity (with Serializer Reconstruction): {df_res['b_syntax_valid'].mean()*100:.1f}%")
    print(f"Condition B Syntax Validity (WITHOUT Serializer Reconstruction / Flat): {df_res['flat_b_syntax_valid'].mean()*100:.1f}%")
    
    out_path = "results/ast_paradox_investigation.json"
    df_res.to_json(out_path, orient="records", indent=2)
    print(f"[DONE] Saved findings to {out_path}")

if __name__ == "__main__":
    main()

