"""Opt-in live smoke test for grep_module_docs against the real Terraform Registry.

Hits the public registry API end-to-end (fetch -> assemble -> cache -> grep), so it
is gated behind RUN_REGISTRY_BENCHMARK=1 (reusing the same opt-in switch as
test_registry_comparison.py) to keep normal CI hermetic. Enable with::

    RUN_REGISTRY_BENCHMARK=1 pytest tests/integration/test_grep_module_docs_live.py -v

When the env var is unset the tests skip; when it is set but the registry is
unreachable they skip gracefully rather than fail.
"""

import os
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tfmod_mcp_server import grep_module_docs_impl  # noqa: E402

pytestmark = pytest.mark.benchmark

REGISTRY_BENCHMARK_ENABLED = os.getenv("RUN_REGISTRY_BENCHMARK") == "1"

skip_unless_enabled = pytest.mark.skipif(
    not REGISTRY_BENCHMARK_ENABLED,
    reason="set RUN_REGISTRY_BENCHMARK=1 to run the live grep_module_docs smoke test",
)


@skip_unless_enabled
def test_live_grep_finds_input_variable(tmp_path):
    """Pinned fetch of a real module, grep for a known input variable."""
    try:
        out = grep_module_docs_impl(
            "terraform-aws-modules/vpc/aws",
            r"enable_nat_gateway",
            version="6.6.1",
            cache_dir=tmp_path,
        )
    except (urllib.error.URLError, OSError) as exc:  # network hiccup -> skip, don't fail
        pytest.skip(f"Terraform Registry unreachable: {exc}")

    assert out.resolved_version == "6.6.1"
    assert out.total_matches >= 1
    assert any("enable_nat_gateway" in m.line for m in out.matches)
    assert any(m.section.startswith("root/") for m in out.matches)
    assert out.cache.policy == "pinned"


@skip_unless_enabled
def test_live_pinned_second_call_is_cache_hit(tmp_path):
    """A repeated pinned request is served from the on-disk cache (no refetch)."""
    try:
        first = grep_module_docs_impl("terraform-aws-modules/vpc/aws", r"subnet", version="6.6.1", cache_dir=tmp_path)
    except (urllib.error.URLError, OSError) as exc:
        pytest.skip(f"Terraform Registry unreachable: {exc}")

    assert first.cache.hit is False  # first call fetched
    second = grep_module_docs_impl("terraform-aws-modules/vpc/aws", r"subnet", version="6.6.1", cache_dir=tmp_path)
    assert second.cache.hit is True  # served from cache
    assert second.resolved_version == "6.6.1"
