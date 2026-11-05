import time, os, sys
sys.path.insert(0, os.getcwd())
from tokenizers import Tokenizer
from src.mrtopos.ast_builder import SnapshotASTBuilder

raw_tok = Tokenizer.from_file('models/gemma4_tokenizer/tokenizer.json')
tok_fn = lambda t: len(raw_tok.encode(t, add_special_tokens=False).ids)
ast_builder = SnapshotASTBuilder(tokenizer_fn=tok_fn)

t0 = time.time()
graph = ast_builder.build_graph_from_snapshot('data/snapshots/fastapi_15661.tgz', generate_skeletons=False)
t1 = time.time()
print(f'Graph built: {t1-t0:.2f}s, nodes: {len(graph.nodes)}')

cands = list(graph.nodes.values())[:400]
t2 = time.time()
ast_builder.ensure_symbol_skeletons(cands)
t3 = time.time()
print(f'400 skeletons ensured: {t3-t2:.2f}s')

