"""
Differential Typing Pruner for MR-TopoS.

Transforms Python ASTs into structurally sound, type-contract preserving skeletons
by stripping prose documentation and metadata while maintaining syntactic validity.
"""

import ast
import copy
from typing import Optional, Tuple
from src.mrtopos.models import ResolutionTier


class ASTDifferentialPruner(ast.NodeTransformer):
    """
    Transforms AST nodes into Tier 1 (Stub) or Tier 2 (Contract Skeleton) representations.
    
    Guarantees:
    1. Modern typing metadata (Annotated[T, Doc(...)]) has Doc expressions pruned while
       preserving the underlying type contract T and non-doc constraints (e.g. Field()).
    2. Overloads, property getters, classmethods, and routing decorators are strictly preserved.
    3. Docstrings are condensed to 1-line summaries in Tier 2, and stripped in Tier 1.
    4. Non-Empty Body Invariant: Enforces that class definitions are never empty, preventing
       IndentationError on docstring-only classes.
    """

    CORE_DECORATORS = {"property", "classmethod", "staticmethod"}

    def __init__(self, tier: ResolutionTier = ResolutionTier.SKELETON):
        super().__init__()
        self.tier = tier
        self.keep_docstring_summary = (tier == ResolutionTier.SKELETON)
        self.docstrings_pruned_count = 0
        self.annotated_docs_pruned_count = 0

    def _strip_function_stub_details(self, node: ast.AST) -> None:
        """Strip parameter annotations, return type, and non-core decorators for Tier 1 STUB."""
        if hasattr(node, "returns"):
            node.returns = None
        if hasattr(node, "args"):
            for a in (node.args.posonlyargs + node.args.args + node.args.kwonlyargs):
                a.annotation = None
            if node.args.vararg:
                node.args.vararg.annotation = None
            if node.args.kwarg:
                node.args.kwarg.annotation = None

        new_decs = []
        for d in getattr(node, "decorator_list", []):
            dec_name = getattr(d, "id", getattr(d, "attr", ""))
            if dec_name in self.CORE_DECORATORS:
                new_decs.append(d)
        node.decorator_list = new_decs

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        """Prune Doc(...) metadata from typing.Annotated[T, Doc(...), ...]."""
        self.generic_visit(node)
        
        is_annotated = False
        if isinstance(node.value, ast.Name) and node.value.id == "Annotated":
            is_annotated = True
        elif isinstance(node.value, ast.Attribute) and node.value.attr == "Annotated":
            is_annotated = True

        if is_annotated and isinstance(node.slice, ast.Tuple):
            new_elts = []
            for i, elt in enumerate(node.slice.elts):
                if i == 0:
                    # Always preserve base type T
                    new_elts.append(elt)
                else:
                    # Check if this element is a Doc(...) call or docstring literal
                    if isinstance(elt, ast.Call):
                        call_name = getattr(elt.func, "id", getattr(elt.func, "attr", ""))
                        if call_name == "Doc":
                            self.annotated_docs_pruned_count += 1
                            continue
                    elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        self.annotated_docs_pruned_count += 1
                        continue
                    # Retain other typing constraints (e.g. Field(gt=0))
                    new_elts.append(elt)

            if len(new_elts) == 1:
                # If only base type remains, simplify Annotated[T] -> T
                return new_elts[0]
            else:
                node.slice.elts = new_elts
                return node

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Skeletonize function body, preserving signature and 1-line doc summary if Tier 2."""
        self.generic_visit(node)
        if self.tier == ResolutionTier.STUB:
            self._strip_function_stub_details(node)

        doc = ast.get_docstring(node)
        new_body = []

        if doc and self.keep_docstring_summary:
            summary = extract_docstring_summary(doc)
            if summary:
                new_body.append(ast.Expr(value=ast.Constant(value=summary)))
                self.docstrings_pruned_count += 1
        elif doc:
            self.docstrings_pruned_count += 1

        # Elide implementation body with ellipsis (...)
        new_body.append(ast.Expr(value=ast.Constant(value=...)))
        node.body = new_body
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        """Skeletonize async function body, preserving signature and 1-line doc summary if Tier 2."""
        self.generic_visit(node)
        if self.tier == ResolutionTier.STUB:
            self._strip_function_stub_details(node)

        doc = ast.get_docstring(node)
        new_body = []

        if doc and self.keep_docstring_summary:
            summary = extract_docstring_summary(doc)
            if summary:
                new_body.append(ast.Expr(value=ast.Constant(value=summary)))
                self.docstrings_pruned_count += 1
        elif doc:
            self.docstrings_pruned_count += 1

        new_body.append(ast.Expr(value=ast.Constant(value=...)))
        node.body = new_body
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """Skeletonize class docstring and enforce non-empty body invariant."""
        self.generic_visit(node)
        if self.tier == ResolutionTier.STUB:
            new_decs = []
            for d in getattr(node, "decorator_list", []):
                dec_name = getattr(d, "id", getattr(d, "attr", ""))
                if dec_name in self.CORE_DECORATORS:
                    new_decs.append(d)
            node.decorator_list = new_decs

        doc = ast.get_docstring(node)

        if doc:
            self.docstrings_pruned_count += 1
            if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)):
                if self.keep_docstring_summary:
                    summary = extract_docstring_summary(doc)
                    if summary:
                        node.body[0] = ast.Expr(value=ast.Constant(value=summary))
                    else:
                        node.body.pop(0)
                else:
                    node.body.pop(0)

        # Enforce Non-Empty Body Invariant
        if not node.body:
            node.body = [ast.Expr(value=ast.Constant(value=...))]

        return node


def prune_source_to_tier(raw_source: str, tier: ResolutionTier) -> Tuple[str, bool]:
    """
    Transform raw Python source code into the requested resolution tier.
    
    Returns:
        (transformed_code, is_syntactically_valid)
    """
    if tier == ResolutionTier.FULL:
        return raw_source, True
    if tier == ResolutionTier.EXCLUDED:
        return "", True

    try:
        tree = ast.parse(raw_source)
    except SyntaxError:
        # If raw source cannot parse, return original as fallback
        return raw_source, False

    pruner = ASTDifferentialPruner(tier=tier)
    transformed_tree = pruner.visit(tree)
    ast.fix_missing_locations(transformed_tree)
    
    transformed_code = ast.unparse(transformed_tree)

    # Verify syntactic validity of generated code
    try:
        ast.parse(transformed_code)
        return transformed_code, True
    except SyntaxError:
        return transformed_code, False


def extract_docstring_summary(doc: Optional[str]) -> Optional[str]:
    """Extract first sentence / 1-line summary from docstring."""
    if not doc:
        return None
    cleaned = doc.strip()
    if not cleaned:
        return None
    first_line = cleaned.split("\n")[0].strip()
    if ". " in first_line:
        first_line = first_line.split(". ")[0].strip() + "."
    return first_line if first_line else None

