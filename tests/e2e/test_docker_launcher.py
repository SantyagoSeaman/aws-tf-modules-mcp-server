"""
Tests for the dual-mode launcher shipped with the Claude Code plugin
(plugins/tfmod-search/bin/tfmodsearch_launch.py). It selects between the
default local `uvx tfmodsearch` and the opt-in `docker run -i --rm <image>`
backend based on the TFMODSEARCH_DOCKER env flag — see
docs/docker-container-support.md §4.6.

Loaded as a module (not run as a subprocess) so `select_backend()` — the pure
dispatch function — can be exercised directly, without needing a real `docker`
or `uvx` binary on PATH.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
LAUNCHER_PATH = PROJECT_ROOT / "plugins" / "tfmod-search" / "bin" / "tfmodsearch_launch.py"


def _load_launcher():
    spec = importlib.util.spec_from_file_location("tfmodsearch_launch", LAUNCHER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


launcher = _load_launcher()


@pytest.mark.e2e
def test_default_env_selects_uvx():
    command, argv, docker_unavailable = launcher.select_backend({}, [])
    assert command == "uvx"
    assert argv == ["uvx", "tfmodsearch"]
    assert docker_unavailable is False


@pytest.mark.e2e
def test_docker_flag_unset_or_zero_selects_uvx():
    for env in ({"TFMODSEARCH_DOCKER": "0"}, {"TFMODSEARCH_DOCKER": ""}):
        command, argv, docker_unavailable = launcher.select_backend(env, [])
        assert command == "uvx"
        assert docker_unavailable is False


@pytest.mark.e2e
@pytest.mark.parametrize("value", ["false", "False", "FALSE", "no", "No", "off", "Off", " 0 ", " "])
def test_docker_flag_other_falsy_variants_select_uvx(value):
    command, argv, docker_unavailable = launcher.select_backend({"TFMODSEARCH_DOCKER": value}, [])
    assert command == "uvx"
    assert docker_unavailable is False


@pytest.mark.e2e
@pytest.mark.parametrize("value", ["1", "true", "True", "yes", "on", " 1 "])
def test_docker_flag_truthy_variants_select_docker(monkeypatch, value):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/usr/bin/docker" if name == "docker" else None)
    command, argv, docker_unavailable = launcher.select_backend({"TFMODSEARCH_DOCKER": value}, [])
    assert command == "docker"
    assert docker_unavailable is False


@pytest.mark.e2e
def test_extra_args_pass_through_to_uvx():
    command, argv, _ = launcher.select_backend({}, ["--warmup"])
    assert command == "uvx"
    assert argv == ["uvx", "tfmodsearch", "--warmup"]


@pytest.mark.e2e
def test_docker_flag_selects_docker_when_available(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/usr/bin/docker" if name == "docker" else None)
    command, argv, docker_unavailable = launcher.select_backend({"TFMODSEARCH_DOCKER": "1"}, [])
    assert command == "docker"
    assert argv == ["docker", "run", "-i", "--rm", launcher.DEFAULT_IMAGE]
    assert docker_unavailable is False


@pytest.mark.e2e
def test_docker_image_override(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/usr/bin/docker" if name == "docker" else None)
    env = {"TFMODSEARCH_DOCKER": "1", "TFMODSEARCH_IMAGE": "ghcr.io/santyagoseaman/tfmodsearch:0.15.0-test"}
    command, argv, _ = launcher.select_backend(env, [])
    assert command == "docker"
    assert argv == ["docker", "run", "-i", "--rm", "ghcr.io/santyagoseaman/tfmodsearch:0.15.0-test"]


@pytest.mark.e2e
def test_docker_extra_args_pass_through(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/usr/bin/docker" if name == "docker" else None)
    command, argv, _ = launcher.select_backend({"TFMODSEARCH_DOCKER": "1"}, ["--warmup"])
    assert argv == ["docker", "run", "-i", "--rm", launcher.DEFAULT_IMAGE, "--warmup"]


@pytest.mark.e2e
def test_docker_requested_but_missing_falls_back_to_uvx(monkeypatch):
    monkeypatch.setattr(launcher.shutil, "which", lambda name: None)
    command, argv, docker_unavailable = launcher.select_backend({"TFMODSEARCH_DOCKER": "1"}, [])
    assert command == "uvx"
    assert argv == ["uvx", "tfmodsearch"]
    assert docker_unavailable is True


@pytest.mark.e2e
def test_default_image_matches_project_version():
    import tomllib

    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        version = tomllib.load(f)["project"]["version"]
    assert launcher.DEFAULT_IMAGE == f"ghcr.io/santyagoseaman/tfmodsearch:{version}"


@pytest.mark.e2e
def test_main_execs_uvx_by_default(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["tfmodsearch_launch.py"])
    monkeypatch.delenv("TFMODSEARCH_DOCKER", raising=False)
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda command, argv: calls.append((command, argv)))

    launcher.main()

    assert calls == [("uvx", ["uvx", "tfmodsearch"])]
    assert capsys.readouterr().err == ""


@pytest.mark.e2e
def test_main_warns_and_falls_back_when_docker_missing(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["tfmodsearch_launch.py", "--warmup"])
    monkeypatch.setenv("TFMODSEARCH_DOCKER", "1")
    monkeypatch.setattr(launcher.shutil, "which", lambda name: None)
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda command, argv: calls.append((command, argv)))

    launcher.main()

    assert calls == [("uvx", ["uvx", "tfmodsearch", "--warmup"])]
    assert "not on PATH" in capsys.readouterr().err


# --- TFMODSEARCH_URL proxy mode (0.18.0) ---


@pytest.mark.e2e
def test_resolve_proxy_url_unset_and_falsy_return_none():
    for env in ({}, {"TFMODSEARCH_URL": ""}, {"TFMODSEARCH_URL": "0"}, {"TFMODSEARCH_URL": "off"}):
        assert launcher.resolve_proxy_url(env) is None


@pytest.mark.e2e
@pytest.mark.parametrize("value", ["1", "true", "True", "yes", "on", " 1 "])
def test_resolve_proxy_url_truthy_shorthand_gives_default(value):
    assert launcher.resolve_proxy_url({"TFMODSEARCH_URL": value}) == launcher.DEFAULT_PROXY_URL


@pytest.mark.e2e
def test_resolve_proxy_url_full_url_passes_through():
    url = "http://127.0.0.1:9000/mcp"
    assert launcher.resolve_proxy_url({"TFMODSEARCH_URL": url}) == url


@pytest.mark.e2e
def test_health_url_for_replaces_path():
    assert launcher.health_url_for("http://127.0.0.1:9000/mcp") == "http://127.0.0.1:9000/health"
    assert launcher.health_url_for(launcher.DEFAULT_PROXY_URL) == "http://127.0.0.1:8765/health"


@pytest.mark.e2e
def test_daemon_healthy_true_on_200_false_otherwise():
    assert launcher.daemon_healthy("http://x/health", fetcher=lambda u, t: 200) is True
    assert launcher.daemon_healthy("http://x/health", fetcher=lambda u, t: 503) is False

    def boom(u, t):
        raise OSError("refused")

    assert launcher.daemon_healthy("http://x/health", fetcher=boom) is False


@pytest.mark.e2e
def test_main_proxy_healthy_execs_proxy(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: True)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "1"})
    assert calls == [
        (
            "uvx",
            ["uvx", "--from", launcher.PROXY_PACKAGE_SPEC, "tfmodsearch", "--proxy-url", launcher.DEFAULT_PROXY_URL],
        )
    ]


@pytest.mark.e2e
def test_main_proxy_precedence_notice_over_docker(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: True)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "1", "TFMODSEARCH_DOCKER": "1"})
    assert "TFMODSEARCH_URL takes precedence" in capsys.readouterr().err
    assert calls[0][0] == "uvx"
    assert "--proxy-url" in calls[0][1]


@pytest.mark.e2e
def test_main_proxy_unhealthy_falls_back_to_local(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(launcher.os, "execvp", lambda cmd, argv: calls.append((cmd, argv)))
    monkeypatch.setattr(launcher, "daemon_healthy", lambda url: False)
    monkeypatch.setattr(launcher.sys, "argv", ["tfmodsearch_launch.py"])
    launcher.main(env={"TFMODSEARCH_URL": "http://127.0.0.1:9999/mcp"})
    assert "not responding" in capsys.readouterr().err
    assert calls == [("uvx", ["uvx", "tfmodsearch"])]
