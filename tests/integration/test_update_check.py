"""Update check: PyPI latest-version fetch and version comparison."""

from tfmod_registry_docs import fetch_latest_pypi_version, is_newer_version


class TestIsNewerVersion:
    def test_newer(self):
        assert is_newer_version("0.17.0", "0.16.0") is True
        assert is_newer_version("1.0.0", "0.99.99") is True

    def test_equal_and_older(self):
        assert is_newer_version("0.16.0", "0.16.0") is False
        assert is_newer_version("0.15.1", "0.16.0") is False

    def test_malformed_fails_closed(self):
        assert is_newer_version("1.0.0rc1", "0.16.0") is False
        assert is_newer_version("banana", "0.16.0") is False
        assert is_newer_version("0.17.0", "0.0.0.dev0") is False


class TestFetchLatestPypiVersion:
    def test_success_via_injected_fetcher(self):
        def fake_fetcher(url, timeout):
            assert url == "https://pypi.org/pypi/tfmodsearch/json"
            assert timeout == 5
            return {"info": {"version": "0.17.0"}}

        assert fetch_latest_pypi_version(fetcher=fake_fetcher) == "0.17.0"

    def test_fetch_error_returns_none(self):
        def failing_fetcher(url, timeout):
            raise OSError("network down")

        assert fetch_latest_pypi_version(fetcher=failing_fetcher) is None

    def test_garbage_payload_returns_none(self):
        assert fetch_latest_pypi_version(fetcher=lambda u, t: {"unexpected": True}) is None
        assert fetch_latest_pypi_version(fetcher=lambda u, t: {"info": {}}) is None
