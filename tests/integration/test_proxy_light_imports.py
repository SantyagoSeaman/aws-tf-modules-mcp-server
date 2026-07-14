"""The proxy entry path must never import the ML stack.

tfmod_entry dispatches --proxy-url to tfmod_proxy/tfmod_server_args; importing
those three modules must not pull torch, sentence_transformers, or the heavy
tfmod_search_lib/tfmod_mcp_server modules. Run in a subprocess so previously
imported modules in the test session cannot mask a regression.
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def test_entry_and_proxy_modules_do_not_import_ml_stack():
    code = (
        "import sys; sys.path.insert(0, 'src'); "
        "import tfmod_entry, tfmod_proxy, tfmod_server_args; "
        "heavy = {'torch', 'sentence_transformers', 'tfmod_search_lib', 'tfmod_mcp_server'}; "
        "loaded = heavy & set(sys.modules); "
        "assert not loaded, f'heavy modules imported: {loaded}'"
    )
    subprocess.run([sys.executable, "-c", code], check=True, cwd=PROJECT_ROOT)


def test_redact_userinfo_strips_credentials():
    sys.path.insert(0, str(PROJECT_ROOT / "src"))
    from tfmod_proxy import _redact_userinfo

    assert _redact_userinfo("http://user:secret@host:8765/mcp") == "http://host:8765/mcp"
    assert _redact_userinfo("http://host:8765/mcp") == "http://host:8765/mcp"
