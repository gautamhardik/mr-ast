"""
Multi-Language AST and Grammar Serializer for MR-AST.

Extends Multi-Resolution AST Context Selection beyond Python to:
- Go (functions, methods, structs, interfaces)
- Java (classes, interfaces, methods, constructors)
- TypeScript (functions, methods, classes, interfaces, types)
- Rust (functions, methods, structs, traits, impl blocks)

Formally instantiates the 4-tier projection lattice R:
  Tier 3 (FULL): Complete source implementation
  Tier 2 (SKELETON): Signature, docstrings, type annotations with stubbed body
  Tier 1 (STUB): Bare declaration / signature header
  Tier 0 (EXCLUDED): Empty string (epsilon)
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TargetLanguage(str, Enum):
    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    TYPESCRIPT = "typescript"
    RUST = "rust"


@dataclass
class MultiLangSymbol:
    name: str
    symbol_type: str  # function, method, class, struct, interface, trait
    language: TargetLanguage
    full_source: str
    docstring: str = ""
    signature: str = ""
    container: Optional[str] = None  # parent class/struct/trait name


class MultiLangASTSerializer:
    """
    Language-agnostic multi-resolution serializer.
    Extracts Full, Skeleton, Stub, and Excluded tiers across languages.
    """

    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer

    def count_tokens(self, text: str) -> int:
        if not text:
            return 0
        if self.tokenizer is not None:
            if hasattr(self.tokenizer, "encode"):
                return len(self.tokenizer.encode(text))
            elif hasattr(self.tokenizer, "tokenize"):
                return len(self.tokenizer.tokenize(text))
        # Deterministic BPE approximation (~1.3 tokens per word)
        words = text.split()
        return max(1, int(len(words) * 1.3) + len(text) // 50)

    # -------------------------------------------------------------
    # Go Serializer
    # -------------------------------------------------------------
    def serialize_go(self, symbol: MultiLangSymbol, tier: int) -> str:
        """
        Serialize Go symbols (func, method, type struct, type interface).
        """
        if tier == 0:
            return ""
        if tier == 3:
            return symbol.full_source.strip()

        # Extract docstring comments above function
        docs = f"// {symbol.docstring.strip()}\n" if symbol.docstring else ""

        if symbol.symbol_type in ("struct", "type_struct"):
            if tier == 1:
                return f"type {symbol.name} struct"
            elif tier == 2:
                return f"{docs}type {symbol.name} struct {{\n\t// fields ...\n}}"

        elif symbol.symbol_type in ("interface", "type_interface"):
            if tier == 1:
                return f"type {symbol.name} interface"
            elif tier == 2:
                # Retain method signatures inside interface
                lines = symbol.full_source.strip().split("\n")
                return "\n".join(lines)

        # Functions and Methods
        sig = symbol.signature
        if not sig:
            # Extract up to first '{'
            match = re.search(r"^(func\s+.*?)\{", symbol.full_source, re.DOTALL)
            sig = match.group(1).strip() if match else f"func {symbol.name}()"

        if tier == 1:
            return sig.strip()
        elif tier == 2:
            return f"{docs}{sig} {{\n\t// ...\n}}"

        return symbol.full_source.strip()

    # -------------------------------------------------------------
    # Java Serializer
    # -------------------------------------------------------------
    def serialize_java(self, symbol: MultiLangSymbol, tier: int) -> str:
        """
        Serialize Java symbols (class, interface, method, constructor).
        """
        if tier == 0:
            return ""
        if tier == 3:
            return symbol.full_source.strip()

        javadoc = f"/**\n * {symbol.docstring.strip()}\n */\n" if symbol.docstring else ""

        if symbol.symbol_type in ("class", "abstract_class"):
            if tier == 1:
                return f"public class {symbol.name};"
            elif tier == 2:
                return f"{javadoc}public class {symbol.name} {{\n    /* class skeleton ... */\n}}"

        elif symbol.symbol_type == "interface":
            if tier == 1:
                return f"public interface {symbol.name};"
            elif tier == 2:
                return symbol.full_source.strip()

        # Method
        sig = symbol.signature
        if not sig:
            match = re.search(r"^(.*?)\{", symbol.full_source, re.DOTALL)
            sig = match.group(1).strip() if match else f"public void {symbol.name}()"

        if tier == 1:
            return f"{sig};"
        elif tier == 2:
            return f"{javadoc}{sig} {{\n    /* ... */\n}}"

        return symbol.full_source.strip()

    # -------------------------------------------------------------
    # TypeScript Serializer
    # -------------------------------------------------------------
    def serialize_typescript(self, symbol: MultiLangSymbol, tier: int) -> str:
        """
        Serialize TypeScript symbols (function, method, class, interface, type).
        """
        if tier == 0:
            return ""
        if tier == 3:
            return symbol.full_source.strip()

        tsdoc = f"/** {symbol.docstring.strip()} */\n" if symbol.docstring else ""

        if symbol.symbol_type == "interface":
            if tier == 1:
                return f"interface {symbol.name};"
            elif tier == 2:
                return symbol.full_source.strip()

        elif symbol.symbol_type == "type":
            if tier == 1:
                return f"type {symbol.name};"
            elif tier == 2:
                return symbol.full_source.strip()

        elif symbol.symbol_type == "class":
            if tier == 1:
                return f"export class {symbol.name};"
            elif tier == 2:
                return f"{tsdoc}export class {symbol.name} {{\n  // methods ...\n}}"

        # Function / Method
        sig = symbol.signature
        if not sig:
            match = re.search(r"^(.*?)\{", symbol.full_source, re.DOTALL)
            sig = match.group(1).strip() if match else f"function {symbol.name}(): void"

        if tier == 1:
            return f"{sig};"
        elif tier == 2:
            return f"{tsdoc}{sig} {{\n  /* ... */\n}}"

        return symbol.full_source.strip()

    # -------------------------------------------------------------
    # Rust Serializer
    # -------------------------------------------------------------
    def serialize_rust(self, symbol: MultiLangSymbol, tier: int) -> str:
        """
        Serialize Rust symbols (fn, struct, trait, impl).
        """
        if tier == 0:
            return ""
        if tier == 3:
            return symbol.full_source.strip()

        doc = f"/// {symbol.docstring.strip()}\n" if symbol.docstring else ""

        if symbol.symbol_type == "struct":
            if tier == 1:
                return f"pub struct {symbol.name};"
            elif tier == 2:
                return f"{doc}pub struct {symbol.name} {{\n    // fields ...\n}}"

        elif symbol.symbol_type == "trait":
            if tier == 1:
                return f"pub trait {symbol.name};"
            elif tier == 2:
                return symbol.full_source.strip()

        # Function / Method
        sig = symbol.signature
        if not sig:
            match = re.search(r"^(.*?)\{", symbol.full_source, re.DOTALL)
            sig = match.group(1).strip() if match else f"pub fn {symbol.name}()"

        if tier == 1:
            return f"{sig};"
        elif tier == 2:
            return f"{doc}{sig} {{\n    unimplemented!()\n}}"

        return symbol.full_source.strip()

    # -------------------------------------------------------------
    # Unified Multi-Lang Interface
    # -------------------------------------------------------------
    def serialize(self, symbol: MultiLangSymbol, tier: int) -> str:
        if tier == 0:
            return ""
        if symbol.language == TargetLanguage.GO:
            return self.serialize_go(symbol, tier)
        elif symbol.language == TargetLanguage.JAVA:
            return self.serialize_java(symbol, tier)
        elif symbol.language == TargetLanguage.TYPESCRIPT:
            return self.serialize_typescript(symbol, tier)
        elif symbol.language == TargetLanguage.RUST:
            return self.serialize_rust(symbol, tier)
        else:
            raise ValueError(f"Unsupported language: {symbol.language}")

    def get_tier_costs(self, symbol: MultiLangSymbol) -> Tuple[int, int, int, int]:
        """
        Compute token costs for (Tier 0, Tier 1, Tier 2, Tier 3).
        Guarantees strict monotonicity: 0 = c0 < c1 <= c2 <= c3.
        """
        c0 = 0
        c1 = self.count_tokens(self.serialize(symbol, 1))
        c2 = self.count_tokens(self.serialize(symbol, 2))
        c3 = self.count_tokens(self.serialize(symbol, 3))

        # Enforce non-decreasing cost invariant
        c1 = max(1, c1)
        c2 = max(c1, c2)
        c3 = max(c2, c3)
        return (c0, c1, c2, c3)

