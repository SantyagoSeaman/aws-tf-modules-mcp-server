"""
Integration tests comparing embedding models for search quality and performance.

This test suite compares:
- thenlper/gte-small (384 dims, ~67MB)
- BAAI/bge-base-en-v1.5 (768 dims, ~220MB)

Tests verify that target modules appear in top-3 results for auto-generated
queries of varying lengths, and measures timing for each model.
"""

import logging
import time
from dataclasses import dataclass, field

import pytest

from tests.integration import PROJECT_ROOT
from tfmod_search_lib import build_index, compute_scores, load_index, save_index

# Models to compare
MODELS = [
    "thenlper/gte-small",
    "BAAI/bge-base-en-v1.5",
]

# Target modules for testing
TARGET_MODULES = ["s3-bucket", "rds", "ec2-instance"]


@dataclass
class QueryTestCase:
    """Test case linking a query to its expected target module."""

    query: str
    target_module: str
    query_type: str  # e.g., "1-word", "2-word", "short-phrase", "medium-phrase", "long-nlq"


@dataclass
class TimingResult:
    """Stores timing information for a model query."""

    model: str
    query: str
    target_module: str
    query_type: str
    duration_ms: float
    found_in_top3: bool
    rank: int | None  # 1, 2, 3, or None if not found


@dataclass
class ModelTimings:
    """Aggregates timing results for a model."""

    model: str
    results: list[TimingResult] = field(default_factory=list)

    @property
    def avg_duration_ms(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.duration_ms for r in self.results) / len(self.results)

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.found_in_top3) / len(self.results)

    @property
    def total_queries(self) -> int:
        return len(self.results)


# Module-level storage for timing results
_timing_results: dict[str, ModelTimings] = {}


def generate_queries_for_module(module_name: str) -> list[QueryTestCase]:
    """
    Generate 5 queries of different lengths for a target module.

    Query types:
    1. 1-word: Single keyword
    2. 2-word: Two related keywords
    3. short-phrase: 3-4 word phrase
    4. medium-phrase: 5-7 word phrase
    5. long-nlq: Natural language question (8+ words)
    """
    queries_by_module = {
        "s3-bucket": [
            QueryTestCase("s3", "s3-bucket", "1-word"),
            QueryTestCase("s3 bucket", "s3-bucket", "2-word"),
            QueryTestCase("s3 bucket encryption", "s3-bucket", "short-phrase"),
            QueryTestCase("s3 bucket with versioning and lifecycle", "s3-bucket", "medium-phrase"),
            QueryTestCase(
                "I need to create an S3 bucket with server-side encryption and object versioning enabled",
                "s3-bucket",
                "long-nlq",
            ),
        ],
        "rds": [
            QueryTestCase("rds", "rds", "1-word"),
            QueryTestCase("rds mysql", "rds", "2-word"),
            QueryTestCase("rds postgresql mariadb", "rds", "short-phrase"),
            QueryTestCase("rds instance with option groups and parameters", "rds", "medium-phrase"),
            QueryTestCase(
                "I need to create an RDS database instance with custom parameter groups and automated backups",
                "rds",
                "long-nlq",
            ),
        ],
        "ec2-instance": [
            QueryTestCase("ec2", "ec2-instance", "1-word"),
            QueryTestCase("ec2 instance", "ec2-instance", "2-word"),
            QueryTestCase("ec2 instance autoscaling", "ec2-instance", "short-phrase"),
            QueryTestCase("ec2 instance with ebs volumes attached", "ec2-instance", "medium-phrase"),
            QueryTestCase(
                "I need to launch EC2 instances with custom AMI and security groups for a web application",
                "ec2-instance",
                "long-nlq",
            ),
        ],
    }

    return queries_by_module.get(module_name, [])


def get_all_test_cases() -> list[QueryTestCase]:
    """Generate all test cases for all target modules."""
    all_cases = []
    for module in TARGET_MODULES:
        all_cases.extend(generate_queries_for_module(module))
    return all_cases


@pytest.fixture(scope="module")
def test_logger():
    """Provide a logger for tests."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture(scope="module")
def docs_dir():
    """Path to the documentation directory."""
    path = PROJECT_ROOT / "modules" / "terraform-aws-modules"
    assert path.exists(), f"Documentation directory not found: {path}"
    return str(path)


@pytest.fixture(scope="module")
def gte_small_index(tmp_path_factory, docs_dir, test_logger):
    """Build and return search index using thenlper/gte-small model."""
    model_name = "thenlper/gte-small"
    index_path = tmp_path_factory.mktemp("indexes") / "gte_small_index.pkl"

    test_logger.info(f"Building index with {model_name}...")
    start = time.time()
    idx = build_index(docs_dir, model_name=model_name, logger=test_logger)
    save_index(idx, str(index_path), logger=test_logger)
    duration = time.time() - start

    test_logger.info(f"Built {model_name} index in {duration:.2f}s ({len(idx.docs)} docs)")
    return load_index(str(index_path), logger=test_logger)


@pytest.fixture(scope="module")
def bge_base_index(tmp_path_factory, docs_dir, test_logger):
    """Build and return search index using BAAI/bge-base-en-v1.5 model."""
    model_name = "BAAI/bge-base-en-v1.5"
    index_path = tmp_path_factory.mktemp("indexes") / "bge_base_index.pkl"

    test_logger.info(f"Building index with {model_name}...")
    start = time.time()
    idx = build_index(docs_dir, model_name=model_name, logger=test_logger)
    save_index(idx, str(index_path), logger=test_logger)
    duration = time.time() - start

    test_logger.info(f"Built {model_name} index in {duration:.2f}s ({len(idx.docs)} docs)")
    return load_index(str(index_path), logger=test_logger)


@pytest.fixture(scope="module")
def model_indexes(gte_small_index, bge_base_index):
    """Provide both indexes keyed by model name."""
    return {
        "thenlper/gte-small": gte_small_index,
        "BAAI/bge-base-en-v1.5": bge_base_index,
    }


def record_timing(
    model: str,
    query: str,
    target_module: str,
    query_type: str,
    duration_ms: float,
    found_in_top3: bool,
    rank: int | None,
):
    """Record timing result for later summary."""
    if model not in _timing_results:
        _timing_results[model] = ModelTimings(model=model)

    _timing_results[model].results.append(
        TimingResult(
            model=model,
            query=query,
            target_module=target_module,
            query_type=query_type,
            duration_ms=duration_ms,
            found_in_top3=found_in_top3,
            rank=rank,
        )
    )


# Generate test parameters: (model, query_case)
def generate_test_params():
    """Generate pytest parameters for all model/query combinations."""
    params = []
    for model in MODELS:
        for case in get_all_test_cases():
            # Create a readable test ID
            test_id = f"{model.split('/')[-1]}-{case.target_module}-{case.query_type}"
            params.append(pytest.param(model, case, id=test_id))
    return params


@pytest.mark.parametrize("model,query_case", generate_test_params())
def test_search_finds_target_in_top3(model, query_case, model_indexes, test_logger):
    """
    Test that the target module appears in top-3 search results.

    This test is parametrized across:
    - 2 models (gte-small, bge-base-en-v1.5)
    - 3 modules (s3-bucket, rds, ec2-instance)
    - 5 query types per module (15 queries total)

    Total: 2 × 15 = 30 test cases
    """
    index = model_indexes[model]

    # Measure search time
    start = time.time()
    results = compute_scores(
        index,
        query_case.query,
        w_kw=1.0,
        w_exact=3.0,
        w_bm25=2.0,
        w_sem=3.0,
        top_k=3,
        logger=test_logger,
    )
    duration_ms = (time.time() - start) * 1000

    # Check if target module is in top-3
    top3_modules = []
    rank = None
    for i, (_score, doc_idx) in enumerate(results, 1):
        module_name = index.docs[doc_idx].module_name
        top3_modules.append(module_name)
        if module_name == query_case.target_module:
            rank = i

    found_in_top3 = query_case.target_module in top3_modules

    # Record timing for summary
    record_timing(
        model=model,
        query=query_case.query,
        target_module=query_case.target_module,
        query_type=query_case.query_type,
        duration_ms=duration_ms,
        found_in_top3=found_in_top3,
        rank=rank,
    )

    # Log result
    status = f"rank={rank}" if found_in_top3 else "NOT FOUND"
    test_logger.info(
        f"[{model.split('/')[-1]}] Query: '{query_case.query[:50]}...' -> "
        f"Target: {query_case.target_module} ({status}) [{duration_ms:.1f}ms]"
    )

    # Assert target is in top-3
    assert found_in_top3, (
        f"Target module '{query_case.target_module}' not in top-3 results.\n"
        f"Model: {model}\n"
        f"Query: {query_case.query}\n"
        f"Query type: {query_case.query_type}\n"
        f"Top-3 results: {top3_modules}"
    )


def test_print_timing_summary(request):
    """
    Print timing summary after all parametrized tests complete.

    This test must run last to capture all timing data.
    """
    # Skip if no timing data collected yet
    if not _timing_results:
        pytest.skip("No timing data collected yet")

    print("\n" + "=" * 80)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 80)

    for model in MODELS:
        if model not in _timing_results:
            continue

        timings = _timing_results[model]
        print(f"\n📊 {model}")
        print("-" * 60)
        print(f"  Total queries:    {timings.total_queries}")
        print(f"  Success rate:     {timings.success_rate * 100:.1f}% (target in top-3)")
        print(f"  Avg query time:   {timings.avg_duration_ms:.2f} ms")

        # Breakdown by query type
        by_type: dict[str, list[TimingResult]] = {}
        for r in timings.results:
            if r.query_type not in by_type:
                by_type[r.query_type] = []
            by_type[r.query_type].append(r)

        print("\n  By query type:")
        for qtype in ["1-word", "2-word", "short-phrase", "medium-phrase", "long-nlq"]:
            if qtype in by_type:
                type_results = by_type[qtype]
                avg_ms = sum(r.duration_ms for r in type_results) / len(type_results)
                success = sum(1 for r in type_results if r.found_in_top3)
                print(f"    {qtype:15} - Avg: {avg_ms:6.2f} ms, Success: {success}/{len(type_results)}")

        # Show any failures
        failures = [r for r in timings.results if not r.found_in_top3]
        if failures:
            print(f"\n  ❌ Failed queries ({len(failures)}):")
            for f in failures:
                print(f"    - [{f.query_type}] '{f.query[:40]}...' -> {f.target_module}")

    # Comparison
    if len(_timing_results) == 2:
        print("\n" + "=" * 80)
        print("COMPARISON")
        print("=" * 80)

        gte = _timing_results.get("thenlper/gte-small")
        bge = _timing_results.get("BAAI/bge-base-en-v1.5")

        if gte and bge:
            print("\n  Speed comparison:")
            print(f"    gte-small avg:     {gte.avg_duration_ms:.2f} ms")
            print(f"    bge-base avg:      {bge.avg_duration_ms:.2f} ms")

            if gte.avg_duration_ms > 0:
                speedup = gte.avg_duration_ms / bge.avg_duration_ms
                if speedup > 1:
                    print(f"    bge-base is {speedup:.2f}x faster")
                else:
                    print(f"    gte-small is {1 / speedup:.2f}x faster")

            print("\n  Success rate comparison:")
            print(f"    gte-small:         {gte.success_rate * 100:.1f}%")
            print(f"    bge-base:          {bge.success_rate * 100:.1f}%")

    print("\n" + "=" * 80)


# Ensure summary runs last by using a session-scoped finalizer
@pytest.fixture(scope="session", autouse=True)
def print_final_summary(request):
    """Print final summary when test session ends."""

    def _print_summary():
        if _timing_results:
            print("\n")
            test_print_timing_summary(None)

    request.addfinalizer(_print_summary)


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "-s", "--tb=short"])
