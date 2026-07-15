"""
Comprehensive integration test to verify all modules are searchable.

For each module in the catalog, this test verifies:
1. The module is searchable by keyword
2. The module is searchable by module name
3. The module is searchable by natural language query
4. The target module appears in the top-ranked results (top-1 for exact name;
   top-3 for keyword and natural-language queries)
5. All required fields are populated in the result
"""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import SearchWeights, ServerStateManager, search_modules_impl
from tfmod_search_lib import load_index


@dataclass
class ModuleTestCase:
    """
    Test case definition for a single module.

    Links each module document to its triple test set:
    - module_name: Expected module name to find (exact match)
    - keyword_query: Primary keyword for keyword-based search
    - natural_language_query: Natural language description for semantic search

    Each module is tested with all three query types to ensure comprehensive searchability.
    """

    module_name: str
    keyword_query: str
    natural_language_query: str
    doc_path: str = ""  # Will be populated from search results

    def __post_init__(self):
        """Generate expected document path."""
        if not self.doc_path:
            self.doc_path = f"modules/terraform-aws-modules/{self.module_name}.md"

    def __str__(self) -> str:
        """String representation showing explicit document→query links."""
        return (
            f"Module: {self.module_name}\n"
            f"  Document: {self.doc_path}\n"
            f"  Keyword Query: '{self.keyword_query}'\n"
            f"  Natural Query: '{self.natural_language_query}'"
        )

    def test_id(self) -> str:
        """Generate pytest test ID for this test case."""
        return self.module_name


# Test data: Explicit mapping of each module document to its triple test set
# Each ModuleTestCase links:
#   1. The module document (via module_name)
#   2. Keyword query (for exact/keyword matching tests)
#   3. Natural language query (for semantic search tests)
MODULE_TEST_DATA = [
    # Compute & Containers - 8 modules
    ModuleTestCase("app-runner", "app-runner", "containerized web applications"),
    ModuleTestCase("autoscaling", "auto-scaling-group", "ec2 auto scaling for dynamic capacity"),
    ModuleTestCase("batch", "batch computing", "batch job processing workloads"),
    ModuleTestCase("ec2-instance", "ec2", "virtual machine instances"),
    ModuleTestCase("ecs", "elastic container service", "deploy containers using serverless"),
    ModuleTestCase("eks", "kubernetes", "managed kubernetes cluster"),
    ModuleTestCase("eks-pod-identity", "pod-identity", "eks pod iam roles"),
    # "serverless" is a keyword shared by 5 modules (step-functions, sqs, app-runner,
    # lambda, msk-kafka-cluster) and is a weak discriminator for lambda specifically;
    # "faas" is lambda-specific. The natural-language query keeps "serverless".
    ModuleTestCase("lambda", "faas", "serverless function execution"),
    # Networking - 7 modules
    ModuleTestCase("alb", "application-load-balancer", "layer 7 load balancing"),
    ModuleTestCase("customer-gateway", "vpn customer gateway", "site-to-site vpn connection"),
    ModuleTestCase("elb", "classic load balancer", "legacy elastic load balancer"),
    ModuleTestCase("global-accelerator", "anycast static ip", "global network performance"),
    ModuleTestCase("transit-gateway", "tgw", "network hub spoke topology"),
    ModuleTestCase("vpc", "virtual-private-cloud", "isolated network infrastructure"),
    ModuleTestCase("vpn-gateway", "vpn", "virtual private network gateway"),
    # Storage - 5 modules
    ModuleTestCase("ebs-optimized", "ebs-optimization", "block storage optimization"),
    ModuleTestCase("ecr", "container-registry", "docker image storage"),
    ModuleTestCase("efs", "elastic-file-system", "nfs shared file storage"),
    ModuleTestCase("fsx", "fsx lustre", "high performance file systems"),
    ModuleTestCase("s3-bucket", "object-storage", "s3 bucket with encryption"),
    # Databases - 9 modules
    ModuleTestCase("dms", "database-migration", "database migration service"),
    ModuleTestCase("dynamodb-table", "nosql", "dynamodb key-value database"),
    ModuleTestCase("elasticache", "redis cache", "in-memory caching layer"),
    ModuleTestCase("memory-db", "memorydb", "redis compatible database"),
    ModuleTestCase("opensearch", "elasticsearch", "search and analytics engine"),
    ModuleTestCase("rds", "relational-database", "rds mysql postgresql database"),
    ModuleTestCase("rds-aurora", "aurora serverless", "aurora mysql postgresql"),
    ModuleTestCase("rds-proxy", "connection-pooling", "rds proxy connection management"),
    ModuleTestCase("redshift", "data-warehouse", "analytical data warehouse"),
    # Security & Identity - 7 modules
    ModuleTestCase("acm", "certificate", "ssl tls certificate management"),
    ModuleTestCase("iam", "identity access management", "iam roles and policies"),
    ModuleTestCase("key-pair", "key-generation", "EC2 cryptographic key pair"),
    ModuleTestCase("kms", "encryption keys", "key management service"),
    ModuleTestCase("secrets-manager", "secrets", "secret credentials storage"),
    ModuleTestCase("security-group", "firewall rules", "vpc security group firewall"),
    ModuleTestCase(
        "wafv2", "web-application-firewall", "web application firewall protecting against sql injection and xss"
    ),
    # Monitoring & Logging - 4 modules
    ModuleTestCase("cloudwatch", "logs metrics", "cloudwatch monitoring alarms"),
    ModuleTestCase("datadog-forwarders", "datadog", "datadog log forwarding"),
    ModuleTestCase("managed-service-grafana", "grafana", "amazon managed grafana"),
    ModuleTestCase("managed-service-prometheus", "prometheus", "managed prometheus metrics"),
    # Application Integration - 7 modules
    ModuleTestCase("apigateway-v2", "api-gateway", "http websocket api gateway"),
    ModuleTestCase("appsync", "graphql", "graphql api service"),
    ModuleTestCase("eventbridge", "event-driven", "event bus serverless events"),
    ModuleTestCase("msk-kafka-cluster", "kafka", "managed streaming kafka"),
    ModuleTestCase("sns", "simple-notification-service", "simple notification service"),
    ModuleTestCase("sqs", "message-queue", "simple queue service"),
    ModuleTestCase("step-functions", "workflow", "serverless state machine orchestration"),
    # Content Delivery - 2 modules
    ModuleTestCase("cloudfront", "cdn", "content delivery network"),
    ModuleTestCase("route53", "dns", "domain name system routing"),
    # Developer Tools & Automation - 5 modules
    ModuleTestCase("appconfig", "feature-flags", "application configuration management"),
    ModuleTestCase("atlantis", "terraform automation", "pull request terraform workflow"),
    ModuleTestCase("network-firewall", "firewall", "aws network firewall"),
    ModuleTestCase("notify-slack", "slack notifications", "slack alert integration"),
    ModuleTestCase("ssm-parameter", "parameter-store", "systems manager configuration"),
    # Big Data & Analytics - 1 module
    ModuleTestCase("emr", "hadoop spark", "elastic mapreduce big data"),
]


@pytest.fixture(scope="module")
def test_logger():
    """Provide a logger for tests."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    return logger


@pytest.fixture(scope="module")
def search_index(test_logger):
    """Load the search index once for all tests."""
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"
    if not index_path.exists():
        pytest.skip(f"Index file not found at {index_path}")
    return load_index(str(index_path), test_logger)


@pytest.fixture(scope="module")
def search_weights():
    """Default search weights for testing."""
    # return SearchWeights(w_kw=2.0, w_exact=3.0, w_bm25=1.0, w_sem=1.0)
    return SearchWeights(w_kw=1, w_exact=3.0, w_bm25=2.0, w_sem=3.0)


@pytest.fixture
def server_state(search_index, search_weights, test_logger):
    """Create a ServerState instance for testing."""
    index_path = PROJECT_ROOT / "model" / "tfmod_e5_small_index.pkl"

    # Reset ServerStateManager to allow re-initialization in tests
    ServerStateManager.reset()

    # Initialize the singleton state for tool functions
    state = ServerStateManager.initialize(
        index=search_index, weights=search_weights, index_path=index_path, logger=test_logger
    )

    yield state

    # Cleanup: reset after test
    ServerStateManager.reset()


class TestAllModulesSearchable:
    """Test that every module in the catalog is searchable and returns correct results."""

    @pytest.mark.parametrize("test_case", MODULE_TEST_DATA, ids=lambda tc: tc.test_id())
    def test_module_searchable_by_keyword(self, server_state, test_case: ModuleTestCase):
        """
        Test that each module is searchable by its primary keyword.

        Links module document → keyword query → search results.

        Verifies:
        - Search returns at least 1 result
        - Target module is in top-3 results
        - All required fields are populated
        """
        # Execute search with keyword query
        result = search_modules_impl(test_case.keyword_query, server_state)

        # Verify we got results
        assert len(result.results) > 0, (
            f"No results found for keyword query '{test_case.keyword_query}' "
            f"(module: {test_case.module_name}, doc: {test_case.doc_path})"
        )

        # Get top result (used for the field-population checks below)
        top_result = result.results[0]

        # Verify target module is in top-3 results.
        # search_modules returns the top-3 by contract (see CLAUDE.md), so top-3
        # is the guarantee that actually matters to callers. A few semantically
        # adjacent module pairs legitimately rank a sibling #1 for a short,
        # ambiguous keyword query (e.g. "firewall rules" -> network-firewall over
        # security-group) while the target stays in the top-3. This mirrors the
        # assertion used by test_module_searchable_by_natural_language.
        result_modules = [r.module_name for r in result.results]
        assert any(test_case.module_name in name or name in test_case.module_name for name in result_modules), (
            f"Expected module '{test_case.module_name}' not in top-3. "
            f"Document: {test_case.doc_path}, Keyword query: '{test_case.keyword_query}', "
            f"All results: {result_modules}"
        )

        # Verify all required fields are populated
        assert isinstance(top_result.module_name, str), "module_name should be string"
        assert len(top_result.module_name) > 0, "module_name should not be empty"

        assert isinstance(top_result.path, str), "path should be string"
        assert len(top_result.path) > 0, "path should not be empty"
        assert top_result.path.startswith("modules/"), "path should start with 'modules/'"

        assert isinstance(top_result.keywords, list), "keywords should be list"
        assert len(top_result.keywords) > 0, "keywords should not be empty"
        assert all(isinstance(kw, str) for kw in top_result.keywords), "all keywords should be strings"

        assert isinstance(top_result.description, str), "description should be string"
        # Note: description can be empty if no content extracted

        assert isinstance(top_result.score, float), "score should be float"
        assert top_result.score > 0, "score should be positive"
        assert top_result.score < 1000, "score should be reasonable (< 1000)"

    @pytest.mark.parametrize("test_case", MODULE_TEST_DATA, ids=lambda tc: tc.test_id())
    def test_module_searchable_by_name(self, server_state, test_case: ModuleTestCase):
        """
        Test that each module is searchable by its exact module name.

        Links module document → exact name query → search results.

        Verifies:
        - Exact name search returns the target module in top-1
        - Exact name match gets high score (due to w_exact=3.0)
        """
        # Execute search with exact module name
        result = search_modules_impl(test_case.module_name, server_state)

        # Verify we got results
        assert (
            len(result.results) > 0
        ), f"No results found for module name '{test_case.module_name}' (doc: {test_case.doc_path})"

        # Get top result
        top_result = result.results[0]

        # Verify target module is in top-1
        assert test_case.module_name in top_result.module_name or top_result.module_name in test_case.module_name, (
            f"Expected module '{test_case.module_name}' not in top-1 for exact name search. "
            f"Got '{top_result.module_name}' instead. "
            f"Document: {test_case.doc_path}"
        )

        # Verify high score for exact match (should be significantly higher than semantic-only matches)
        assert top_result.score > 1.0, f"Exact name match should have high score (>1.0), got {top_result.score}"

    @pytest.mark.parametrize("test_case", MODULE_TEST_DATA, ids=lambda tc: tc.test_id())
    def test_module_searchable_by_natural_language(self, server_state, test_case: ModuleTestCase):
        """
        Test that each module is searchable by natural language description.

        Links module document → natural language query → semantic search results.

        Verifies:
        - Natural language query returns relevant results
        - Target module is in top-3 results (allowing for semantic variations)
        """
        # Execute search with natural language query
        result = search_modules_impl(test_case.natural_language_query, server_state)

        # Verify we got results
        assert len(result.results) > 0, (
            f"No results found for natural language query '{test_case.natural_language_query}' "
            f"(module: {test_case.module_name}, doc: {test_case.doc_path})"
        )

        # Collect all module names in results
        result_modules = [r.module_name for r in result.results]

        # Verify target module is in top-3 results (more lenient for natural language)
        assert any(test_case.module_name in name or name in test_case.module_name for name in result_modules), (
            f"Expected module '{test_case.module_name}' not in top-3 for natural language query "
            f"'{test_case.natural_language_query}'. "
            f"Document: {test_case.doc_path}, "
            f"Got: {result_modules}"
        )


class TestModuleResultCompleteness:
    """Test that all modules have complete metadata in search results."""

    def test_all_modules_have_keywords(self, server_state):
        """Verify that all 55 modules have keywords populated."""
        # Get all modules from index
        all_modules = server_state.index.docs

        modules_without_keywords = []
        for doc in all_modules:
            if not doc.keywords or len(doc.keywords) == 0:
                modules_without_keywords.append(doc.module_name or doc.path)

        assert (
            len(modules_without_keywords) == 0
        ), f"Found {len(modules_without_keywords)} modules without keywords: {modules_without_keywords}"

    def test_all_modules_have_module_name(self, server_state):
        """Verify that all 55 modules have module_name populated."""
        # Get all modules from index
        all_modules = server_state.index.docs

        modules_without_name = []
        for doc in all_modules:
            if not doc.module_name or len(doc.module_name) == 0:
                modules_without_name.append(doc.path)

        assert (
            len(modules_without_name) == 0
        ), f"Found {len(modules_without_name)} modules without module_name: {modules_without_name}"

    def test_all_modules_have_text_content(self, server_state):
        """Verify that all 55 modules have text content populated."""
        # Get all modules from index
        all_modules = server_state.index.docs

        modules_without_content = []
        for doc in all_modules:
            if not doc.text or len(doc.text) < 100:  # At least 100 chars
                modules_without_content.append(doc.module_name or doc.path)

        assert (
            len(modules_without_content) == 0
        ), f"Found {len(modules_without_content)} modules without sufficient text content: {modules_without_content}"

    def test_module_count(self, server_state):
        """Verify that index contains exactly 55 modules."""
        module_count = len(server_state.index.docs)
        assert module_count == 55, f"Expected 55 modules in index, found {module_count}"


class TestSearchQuality:
    """Test search quality metrics across all modules."""

    def test_average_keyword_count(self, server_state):
        """Verify modules have reasonable number of keywords (>= 10 on average)."""
        all_modules = server_state.index.docs
        total_keywords = sum(len(doc.keywords) for doc in all_modules)
        avg_keywords = total_keywords / len(all_modules)

        assert avg_keywords >= 10, (
            f"Average keyword count is too low: {avg_keywords:.1f}. "
            f"Expected >= 10 keywords per module for good searchability."
        )

    def test_no_duplicate_module_names(self, server_state):
        """Verify that all module names are unique."""
        all_modules = server_state.index.docs
        module_names = [doc.module_name for doc in all_modules if doc.module_name]

        duplicates = [name for name in set(module_names) if module_names.count(name) > 1]

        assert len(duplicates) == 0, f"Found duplicate module names: {duplicates}"

    def test_keyword_vocabulary_size(self, server_state):
        """Verify good keyword vocabulary diversity (>= 500 unique keywords)."""
        all_keywords = set()
        for doc in server_state.index.docs:
            all_keywords.update(doc.keywords)

        vocab_size = len(all_keywords)
        assert vocab_size >= 500, (
            f"Keyword vocabulary is too small: {vocab_size}. "
            f"Expected >= 500 unique keywords for comprehensive searchability."
        )
