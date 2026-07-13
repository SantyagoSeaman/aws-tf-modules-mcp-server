"""
Reproducible retrieval benchmark: TFModSearch MCP vs. the public Terraform Registry.

This compares what our hybrid-semantic search returns against what a plain
keyword search over the public Terraform Registry returns for the same queries.
The registry endpoint used here (`GET /v1/modules/search?q=...&provider=aws`) is
exactly the API that the official HashiCorp `terraform-mcp-server`'s
`search_modules` tool wraps, so this doubles as an apples-to-apples comparison
against that competitor's module search.

Golden set: the 55-module x 3-query-type set from
``test_all_modules_searchable.py`` (165 labeled queries) — the single source of
truth for "which module is the right answer for this query".

Metric: is the EXPECTED module in the top-1 / top-3 results?
  - ours          : hybrid search over the AWS-only curated index (production
                    weights from ``config.yaml``).
  - reg_official  : registry hit only if it comes from the
                    ``terraform-aws-modules`` namespace (the same official module
                    we document).
  - reg_any       : registry hit if any namespace returns a name-matching module
                    (a deliberately generous scoring in the registry's favor).

The live-network comparison is OPT-IN to keep normal CI hermetic and to avoid
hammering the public registry. Enable it with::

    RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_registry_comparison.py -v -s

With ``-s`` the full comparison table (the one reproduced in the README) is
printed. When the env var is unset the live tests skip; when it is set but the
registry is unreachable they skip gracefully rather than fail.

``test_our_top3_is_perfect_on_golden_set`` needs no network and always runs — it
pins the "Our MCP: 100% top-3" claim from the README to a real assertion.
"""

import json
import logging
import os
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.integration import PROJECT_ROOT
from tests.integration.test_all_modules_searchable import MODULE_TEST_DATA
from tfmod_mcp_server import ConfigLoader, SearchWeights
from tfmod_search_lib import compute_scores, load_index

pytestmark = pytest.mark.benchmark

REGISTRY_BENCHMARK_ENABLED = os.getenv("RUN_REGISTRY_BENCHMARK") == "1"
_REGISTRY_URL = "https://registry.terraform.io/v1/modules/search"
_REG_CACHE: dict[str, list[dict]] = {}

_LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Query-type definitions (shared by every test in this module)
# ---------------------------------------------------------------------------
QUERY_TYPES = (
    ("keyword", lambda tc: tc.keyword_query),
    ("exact-name", lambda tc: tc.module_name),
    ("natural-lang", lambda tc: tc.natural_language_query),
)


def _name_match(a: str, b: str) -> bool:
    """Substring-both-ways match, mirroring test_all_modules_searchable."""
    a, b = a.lower(), b.lower()
    return a == b or a in b or b in a


def _registry_search(query: str, limit: int = 10) -> list[dict]:
    """Query the public Terraform Registry (AWS provider), cached per-process."""
    if query in _REG_CACHE:
        return _REG_CACHE[query]
    url = _REGISTRY_URL + "?" + urllib.parse.urlencode({"q": query, "provider": "aws", "limit": limit})
    with urllib.request.urlopen(url, timeout=25) as resp:  # noqa: S310 (trusted host)
        modules = json.load(resp).get("modules", [])
    _REG_CACHE[query] = modules
    time.sleep(0.05)  # be polite to the public API
    return modules


def _registry_reachable() -> bool:
    try:
        _registry_search("vpc", limit=1)
        return True
    except Exception as exc:  # noqa: BLE001 - any network failure -> skip, don't fail
        _LOG.warning("Terraform Registry unreachable, skipping live benchmark: %s", exc)
        return False


@dataclass
class Rates:
    top1: int = 0
    top3: int = 0
    n: int = 0

    def add(self, ranked: list[str], expected: str) -> None:
        self.n += 1
        if any(_name_match(name, expected) for name in ranked[:1]):
            self.top1 += 1
        if any(_name_match(name, expected) for name in ranked[:3]):
            self.top3 += 1

    @property
    def top1_rate(self) -> float:
        return self.top1 / self.n if self.n else 0.0

    @property
    def top3_rate(self) -> float:
        return self.top3 / self.n if self.n else 0.0


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def search_index():
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    return load_index(str(index_path), _LOG)


@pytest.fixture(scope="module")
def production_weights() -> SearchWeights:
    """The exact weights the MCP server serves with (from config.yaml)."""
    config_path = PROJECT_ROOT / "config.yaml"
    return ConfigLoader.load_weights(config_path=config_path if config_path.exists() else None)


def _our_ranked(index, weights: SearchWeights, query: str) -> list[str]:
    results = compute_scores(
        index,
        query,
        w_kw=weights.w_kw,
        w_exact=weights.w_exact,
        w_bm25=weights.w_bm25,
        w_sem=weights.w_sem,
        top_k=3,
        logger=_LOG,
    )
    return [index.docs[i].module_name for _, i in results]


def _our_rates_by_type(index, weights: SearchWeights) -> dict[str, Rates]:
    rates = {qtype: Rates() for qtype, _ in QUERY_TYPES}
    for qtype, getq in QUERY_TYPES:
        for tc in MODULE_TEST_DATA:
            rates[qtype].add(_our_ranked(index, weights, getq(tc)), tc.module_name)
    return rates


# ---------------------------------------------------------------------------
# Network-free regression guard (always runs)
# ---------------------------------------------------------------------------
class TestOurSideRegression:
    """Pins the README's 'Our MCP: 100% top-3' claim. No network required."""

    def test_our_top3_is_perfect_on_golden_set(self, search_index, production_weights):
        rates = _our_rates_by_type(search_index, production_weights)
        overall_top3 = sum(r.top3 for r in rates.values())
        overall_n = sum(r.n for r in rates.values())

        misses = []
        for qtype, getq in QUERY_TYPES:
            for tc in MODULE_TEST_DATA:
                ranked = _our_ranked(search_index, production_weights, getq(tc))
                if not any(_name_match(n, tc.module_name) for n in ranked[:3]):
                    misses.append(f"{qtype}:{tc.module_name} q={getq(tc)!r} got={ranked}")

        assert overall_top3 == overall_n, (
            f"Expected 100% top-3 on the golden set, got " f"{overall_top3}/{overall_n}. Misses: {misses}"
        )


# ---------------------------------------------------------------------------
# Live registry comparison (opt-in)
# ---------------------------------------------------------------------------
@pytest.mark.skipif(
    not REGISTRY_BENCHMARK_ENABLED,
    reason="set RUN_REGISTRY_BENCHMARK=1 to run the live Terraform Registry comparison",
)
class TestRegistryComparison:
    """Compare our search against the public registry over the full golden set."""

    @pytest.fixture(scope="class", autouse=True)
    def _require_registry(self):
        if not _registry_reachable():
            pytest.skip("Terraform Registry is not reachable")

    @pytest.fixture(scope="class")
    def metrics(self, search_index, production_weights):
        """Run the full 162-query benchmark once and return per-type rates.

        Returns a dict: system -> qtype -> Rates, plus a `coverage` count of how
        many of the 55 modules exist as a standalone official registry module.
        """
        systems = ("ours", "reg_official", "reg_any")
        rates = {s: {qtype: Rates() for qtype, _ in QUERY_TYPES} for s in systems}
        covered: set[str] = set()

        for qtype, getq in QUERY_TYPES:
            for tc in MODULE_TEST_DATA:
                expected = tc.module_name
                query = getq(tc)

                rates["ours"][qtype].add(_our_ranked(search_index, production_weights, query), expected)

                reg = _registry_search(query, limit=10)
                official = [m["name"] for m in reg if m.get("namespace") == "terraform-aws-modules"]
                any_author = [m["name"] for m in reg]
                rates["reg_official"][qtype].add(official, expected)
                rates["reg_any"][qtype].add(any_author, expected)

                # Coverage: does the official standalone module exist at all?
                if any(m.get("namespace") == "terraform-aws-modules" and _name_match(m["name"], expected) for m in reg):
                    covered.add(expected)

        return {"rates": rates, "coverage": len(covered)}

    def test_print_comparison_table(self, metrics):
        """Print the README table. Visible with `pytest -s`."""
        rates = metrics["rates"]
        label = {
            "ours": "Our MCP (semantic, AWS curated)",
            "reg_official": "Registry: official terraform-aws-modules",
            "reg_any": "Registry: any-author aws module",
        }

        def line(system: str, r: Rates) -> str:
            return f"  {label[system]:44} {r.top1_rate * 100:6.1f}% {r.top3_rate * 100:6.1f}%"

        print("\n" + "=" * 78)
        print("TOP-1 / TOP-3 HIT RATE — golden set: 55 modules x 3 query types (165 queries)")
        print("=" * 78)
        for qtype, _ in QUERY_TYPES:
            n = rates["ours"][qtype].n
            print(f"\n### {qtype} (n={n})")
            print(f"  {'system':44} {'top-1':>7} {'top-3':>6}")
            for system in ("ours", "reg_official", "reg_any"):
                print(line(system, rates[system][qtype]))

        print("\n### OVERALL (n=162)")
        print(f"  {'system':44} {'top-1':>7} {'top-3':>6}")
        for system in ("ours", "reg_official", "reg_any"):
            agg = Rates()
            agg.top1 = sum(rates[system][q].top1 for q, _ in QUERY_TYPES)
            agg.top3 = sum(rates[system][q].top3 for q, _ in QUERY_TYPES)
            agg.n = sum(rates[system][q].n for q, _ in QUERY_TYPES)
            print(line(system, agg))
        print(
            f"\nCoverage: {metrics['coverage']}/{len(MODULE_TEST_DATA)} modules exist as an "
            f"official standalone registry module\n"
        )

    def test_our_search_wins_on_natural_language(self, metrics):
        """The headline finding: semantic search dominates keyword search on
        free-text queries. Assert the *relationship* (robust to registry drift)
        rather than exact registry percentages."""
        ours = metrics["rates"]["ours"]["natural-lang"]
        reg = metrics["rates"]["reg_official"]["natural-lang"]

        assert ours.top3_rate >= 0.95, f"Our NL top-3 should be ~100%, got {ours.top3_rate:.1%}"
        assert ours.top3_rate - reg.top3_rate >= 0.5, (
            f"Our NL top-3 ({ours.top3_rate:.1%}) should beat official registry "
            f"({reg.top3_rate:.1%}) by >= 50 percentage points"
        )

    def test_our_search_wins_overall(self, metrics):
        """Overall, we beat even the generous any-author registry scoring."""
        ours = Rates()
        reg = Rates()
        for system, agg in (("ours", ours), ("reg_any", reg)):
            agg.top3 = sum(metrics["rates"][system][q].top3 for q, _ in QUERY_TYPES)
            agg.n = sum(metrics["rates"][system][q].n for q, _ in QUERY_TYPES)

        assert ours.top3_rate - reg.top3_rate >= 0.3, (
            f"Our overall top-3 ({ours.top3_rate:.1%}) should beat any-author "
            f"registry ({reg.top3_rate:.1%}) by >= 30 percentage points"
        )

    def test_all_catalog_modules_exist_in_registry(self, metrics):
        """Sanity check: this is a retrieval-quality story, not a coverage story
        — every module we curate does exist as a standalone registry module."""
        assert metrics["coverage"] == len(MODULE_TEST_DATA), (
            f"Expected all {len(MODULE_TEST_DATA)} modules to exist as official "
            f"standalone registry modules, found {metrics['coverage']}"
        )
