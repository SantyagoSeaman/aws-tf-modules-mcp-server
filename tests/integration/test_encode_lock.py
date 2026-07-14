"""Concurrent model loading must construct the model exactly once."""

import logging
import threading

import tfmod_search_lib

# _get_sentence_transformer calls logger.debug(...); a real (silent) Logger is
# used instead of None so the debug calls do not raise before construction.
_TEST_LOGGER = logging.getLogger("test_encode_lock")


class _SlowFakeModel:
    constructions = 0
    construction_lock = threading.Lock()

    def __init__(self, name, device=None):
        with _SlowFakeModel.construction_lock:
            _SlowFakeModel.constructions += 1
        # widen the race window: yield to other threads mid-construction
        import time

        time.sleep(0.05)

    def encode(self, *a, **kw):
        raise NotImplementedError


def test_concurrent_get_model_loads_once(monkeypatch):
    monkeypatch.setattr(tfmod_search_lib, "SentenceTransformer", _SlowFakeModel)
    monkeypatch.setattr(tfmod_search_lib, "_MODEL_CACHE", {})
    _SlowFakeModel.constructions = 0

    threads = [
        threading.Thread(target=tfmod_search_lib._get_sentence_transformer, args=("fake-model", _TEST_LOGGER))
        for _ in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert _SlowFakeModel.constructions == 1
