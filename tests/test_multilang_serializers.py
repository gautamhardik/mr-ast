"""
Unit tests for Multi-Language AST Serializers across Go, Java, TypeScript, and Rust.
Validates the 4-tier projection lattice R and cost monotonicity.
"""

import os
import pytest
from transformers import PreTrainedTokenizerFast

from src.mrtopos.multilang_serializers import (
    MultiLangASTSerializer,
    MultiLangSymbol,
    TargetLanguage,
)


@pytest.fixture(scope="module")
def gemma_tokenizer():
    tokenizer_path = os.path.abspath("models/gemma4_tokenizer/tokenizer.json")
    if os.path.exists(tokenizer_path):
        return PreTrainedTokenizerFast(tokenizer_file=tokenizer_path)
    return None


def test_01_go_serialization(gemma_tokenizer):
    serializer = MultiLangASTSerializer(tokenizer=gemma_tokenizer)

    go_code = """func CalculateMetrics(ctx context.Context, data []float64) (*MetricsReport, error) {
    if len(data) == 0 {
        return nil, errors.New("empty dataset")
    }
    mean := computeMean(data)
    variance := computeVariance(data, mean)
    return &MetricsReport{Mean: mean, Variance: variance}, nil
}"""
    sym = MultiLangSymbol(
        name="CalculateMetrics",
        symbol_type="function",
        language=TargetLanguage.GO,
        full_source=go_code,
        docstring="CalculateMetrics computes statistical metrics for an array.",
        signature="func CalculateMetrics(ctx context.Context, data []float64) (*MetricsReport, error)",
    )

    t0 = serializer.serialize(sym, 0)
    t1 = serializer.serialize(sym, 1)
    t2 = serializer.serialize(sym, 2)
    t3 = serializer.serialize(sym, 3)

    assert t0 == ""
    assert "func CalculateMetrics" in t1
    assert "{" not in t1
    assert "// ..." in t2
    assert "computeMean(data)" in t3

    c0, c1, c2, c3 = serializer.get_tier_costs(sym)
    assert 0 == c0 < c1 <= c2 <= c3


def test_02_java_serialization(gemma_tokenizer):
    serializer = MultiLangASTSerializer(tokenizer=gemma_tokenizer)

    java_code = """public Response executeQuery(QueryContext ctx) throws ExecutionException {
    logger.info("Executing query id: " + ctx.getId());
    Transaction tx = transactionManager.beginTransaction();
    try {
        ResultTable result = engine.execute(ctx.getSql(), tx);
        tx.commit();
        return Response.ok(result);
    } catch (Exception e) {
        tx.rollback();
        throw new ExecutionException("Failed to execute", e);
    }
}"""
    sym = MultiLangSymbol(
        name="executeQuery",
        symbol_type="method",
        language=TargetLanguage.JAVA,
        full_source=java_code,
        docstring="Executes transactional database query with error handling.",
        signature="public Response executeQuery(QueryContext ctx) throws ExecutionException",
    )

    t0 = serializer.serialize(sym, 0)
    t1 = serializer.serialize(sym, 1)
    t2 = serializer.serialize(sym, 2)
    t3 = serializer.serialize(sym, 3)

    assert t0 == ""
    assert t1.endswith(";")
    assert "/* ... */" in t2
    assert "transactionManager.beginTransaction()" in t3

    c0, c1, c2, c3 = serializer.get_tier_costs(sym)
    assert 0 == c0 < c1 <= c2 <= c3


def test_03_typescript_serialization(gemma_tokenizer):
    serializer = MultiLangASTSerializer(tokenizer=gemma_tokenizer)

    ts_code = """export async function authenticateUser(req: Request, token: string): Promise<UserSession> {
    const claims = await verifyJwt(token, process.env.SECRET_KEY);
    if (!claims.isValid) {
        throw new AuthError("Token expired or invalid");
    }
    const user = await db.users.findById(claims.userId);
    return new UserSession(user, claims.permissions);
}"""
    sym = MultiLangSymbol(
        name="authenticateUser",
        symbol_type="function",
        language=TargetLanguage.TYPESCRIPT,
        full_source=ts_code,
        docstring="Authenticates bearer token and constructs UserSession.",
        signature="export async function authenticateUser(req: Request, token: string): Promise<UserSession>",
    )

    t0 = serializer.serialize(sym, 0)
    t1 = serializer.serialize(sym, 1)
    t2 = serializer.serialize(sym, 2)
    t3 = serializer.serialize(sym, 3)

    assert t0 == ""
    assert t1.endswith(";")
    assert "/* ... */" in t2
    assert "verifyJwt(token" in t3

    c0, c1, c2, c3 = serializer.get_tier_costs(sym)
    assert 0 == c0 < c1 <= c2 <= c3


def test_04_rust_serialization(gemma_tokenizer):
    serializer = MultiLangASTSerializer(tokenizer=gemma_tokenizer)

    rust_code = """pub fn compute_hash<H: Hasher>(input: &[u8], hasher: &mut H) -> Result<u64, HashError> {
    if input.is_empty() {
        return Err(HashError::EmptyInput);
    }
    hasher.write(input);
    Ok(hasher.finish())
}"""
    sym = MultiLangSymbol(
        name="compute_hash",
        symbol_type="function",
        language=TargetLanguage.RUST,
        full_source=rust_code,
        docstring="Hashes byte slice using generic Hasher implementation.",
        signature="pub fn compute_hash<H: Hasher>(input: &[u8], hasher: &mut H) -> Result<u64, HashError>",
    )

    t0 = serializer.serialize(sym, 0)
    t1 = serializer.serialize(sym, 1)
    t2 = serializer.serialize(sym, 2)
    t3 = serializer.serialize(sym, 3)

    assert t0 == ""
    assert t1.endswith(";")
    assert "unimplemented!()" in t2
    assert "hasher.write(input)" in t3

    c0, c1, c2, c3 = serializer.get_tier_costs(sym)
    assert 0 == c0 < c1 <= c2 <= c3

