"""
Unit tests for `_collapse_type_expression` (fatrun5 / Change 1, 0.26.0
candidate): the serve-time collapser that renders oversized Registry-declared
HCL object types down to their first-level attribute keys so a handful of
monster types (eks's `self_managed_node_groups`: 18,561 chars) cannot alone
blow a complete inputs table past `_COMPLETE_TABLE_BYTE_CAP`.

See evals/specs/2026-07-22-type-collapse-and-interface-contract-design.md,
Change 1, for the design this implements.
"""

import json

import pytest

from tests.integration import PROJECT_ROOT
from tfmod_mcp_server import _collapse_type_expression

ANY_OVERLAY_DIR = PROJECT_ROOT / "model" / "any_overlay"


class TestShortTypesPassThroughVerbatim:
    def test_short_type_returned_verbatim(self):
        rendered, collapsed = _collapse_type_expression("string")
        assert rendered == "string"
        assert collapsed is False

    def test_short_object_type_returned_verbatim(self):
        raw = "object({\n  name = string\n  size = number\n})"
        rendered, collapsed = _collapse_type_expression(raw)
        assert rendered == raw
        assert collapsed is False

    def test_threshold_boundary_exact_length_is_verbatim(self):
        raw = "a" * 200
        rendered, collapsed = _collapse_type_expression(raw, threshold=200)
        assert rendered == raw
        assert collapsed is False

    def test_threshold_boundary_one_over_collapses(self):
        raw = "a" * 201
        rendered, collapsed = _collapse_type_expression(raw, threshold=200)
        assert collapsed is True
        assert rendered != raw


class TestObjectCollapseShapes:
    def _long_object(self, n_keys: int, wrapper: str | None = None) -> str:
        attrs = "\n".join(f"    field_{i} = optional(string)" for i in range(n_keys))
        body = f"object({{\n{attrs}\n  }})"
        if wrapper:
            return f"{wrapper}({body})"
        return body

    def test_bare_object_collapses_without_wrapper_prefix(self):
        raw = self._long_object(30)
        assert len(raw) > 200
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.startswith("object{")
        assert rendered.endswith("}")
        assert "field_0" in rendered
        assert "field_11" in rendered
        assert "field_12" not in rendered
        assert ", ... 30 keys" in rendered

    def test_list_object_collapses_with_wrapper_prefix(self):
        raw = self._long_object(30, wrapper="list")
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.startswith("list(object{")
        assert rendered.endswith("})")

    def test_set_object_collapses_with_wrapper_prefix(self):
        raw = self._long_object(30, wrapper="set")
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.startswith("set(object{")
        assert rendered.endswith("})")

    def test_map_object_collapses_with_wrapper_prefix(self):
        raw = self._long_object(30, wrapper="map")
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.startswith("map(object{")
        assert rendered.endswith("})")

    def test_twelve_or_fewer_keys_shows_all_with_no_elision_marker(self):
        raw = self._long_object(11) + ("x" * 200)  # pad past threshold, keys stay 11
        # Rebuild so the padding does not corrupt the object body: append a
        # long description-like comment instead, which the collapser ignores.
        attrs = "\n".join(f"    field_{i} = optional(string)" for i in range(11))
        raw = "object({\n" + attrs + "\n    # " + ("x" * 220) + "\n  })"
        assert len(raw) > 200
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert "... 11 keys" not in rendered
        assert "field_10" in rendered
        for i in range(11):
            assert f"field_{i}" in rendered

    def test_more_than_twelve_keys_elided_with_true_count(self):
        raw = self._long_object(38)
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert ", ... 38 keys" in rendered
        shown = rendered[rendered.index("{") + 1 : rendered.rindex("}")]
        keys = [k.strip() for k in shown.split(",")]
        # 12 real keys plus the trailing "... 38 keys" marker token.
        assert len(keys) == 13
        assert keys[-1] == "... 38 keys"

    def test_nested_object_keys_do_not_leak(self):
        raw = (
            "object({\n"
            "    forwarded_values = optional(object({\n"
            "      cookies = object({\n"
            '        forward           = optional(string, "none")\n'
            "        whitelisted_names = optional(list(string))\n"
            "      })\n"
            "      headers = optional(list(string))\n"
            "    }))\n"
            '    padding_to_force_collapse = optional(string, "' + ("x" * 200) + '")\n'
            "  })"
        )
        assert len(raw) > 200
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        shown = rendered[rendered.index("{") + 1 : rendered.rindex("}")]
        keys = [k.strip() for k in shown.split(",")]
        assert "forwarded_values" in keys
        assert "padding_to_force_collapse" in keys
        assert "cookies" not in keys
        assert "forward" not in keys
        assert "whitelisted_names" not in keys
        assert "headers" not in keys


class TestMalformedAndNonObjectFallback:
    def test_long_non_object_type_hard_truncates(self):
        raw = "string" + ("x" * 250)
        rendered, collapsed = _collapse_type_expression(raw, threshold=200)
        assert collapsed is True
        assert rendered.endswith("...")
        assert len(rendered) == 203  # 200 chars + "..."
        assert rendered[:200] == raw[:200]

    def test_unbalanced_object_falls_back_to_hard_truncate(self):
        raw = "object({\n" + "\n".join(f"    field_{i} = string" for i in range(20))
        assert len(raw) > 200
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.endswith("...")
        assert "field_19}" not in rendered

    def test_unbalanced_wrapped_object_falls_back_to_hard_truncate(self):
        """The object literal's OWN `{`/`}` never balances (no closing brace
        for the body at all) -- a missing/extra WRAPPER paren after an
        otherwise well-formed object body is a separate, harmless case (the
        collapsed rendering is synthesized fresh and never echoes the
        original wrapper parens), so this exercises the case that actually
        matters: the object body itself is malformed."""
        raw = "list(object({\n" + "\n".join(f"    field_{i} = string" for i in range(20))
        assert len(raw) > 200
        rendered, collapsed = _collapse_type_expression(raw)
        assert collapsed is True
        assert rendered.endswith("...")

    def test_non_string_input_never_raises(self):
        rendered, collapsed = _collapse_type_expression(None)  # type: ignore[arg-type]
        assert isinstance(rendered, str)
        assert isinstance(collapsed, bool)

    @pytest.mark.parametrize(
        "garbage",
        [
            "object({" * 50,
            "}" * 300,
            "map(object({" + "{" * 100 + "x" * 100,
            "object({" + '"' + "x" * 300,
            "object({ a = " + "(" * 150 + "x" * 100,
        ],
    )
    def test_pathological_inputs_never_raise(self, garbage):
        rendered, collapsed = _collapse_type_expression(garbage)
        assert isinstance(rendered, str)
        assert isinstance(collapsed, bool)


class TestRealEksSelfManagedNodeGroupsType:
    """Golden-in-test extraction correctness against the actual committed
    overlay data (not a paraphrase) -- eks's `self_managed_node_groups` root
    input, the largest realistic monster type in the catalog (18,561 chars,
    `map(object({...}))`, carries inline `#` comments)."""

    @staticmethod
    @pytest.fixture(scope="class")
    def raw_type():
        path = ANY_OVERLAY_DIR / "terraform-aws-modules__eks__aws.json"
        if not path.is_file():
            pytest.skip(f"overlay fixture not found at {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        item = next(i for i in data["all_inputs"]["root"] if i["name"] == "self_managed_node_groups")
        return item["type"]

    @staticmethod
    @pytest.fixture(scope="class")
    def independent_key_count(raw_type):
        """Independent oracle: the real overlay text happens to indent every
        first-level attribute with exactly 4 spaces (verified by inspection),
        so a simple indentation regex is a legitimate cross-check for a TEST
        -- distinct from the collapser itself, which must not rely on
        indentation (registry type strings are not consistently indented in
        general)."""
        import re

        lines = raw_type.splitlines()[1:]
        return len([line for line in lines if re.match(r"^ {4}[A-Za-z_][A-Za-z0-9_-]*\s*=", line)])

    def test_length_sanity(self, raw_type):
        assert len(raw_type) > 18000

    def test_collapses(self, raw_type):
        rendered, collapsed = _collapse_type_expression(raw_type)
        assert collapsed is True
        assert len(rendered) < 300

    def test_wrapper_is_map(self, raw_type):
        rendered, _ = _collapse_type_expression(raw_type)
        assert rendered.startswith("map(object{")
        assert rendered.endswith("})")

    def test_key_count_matches_independent_oracle(self, raw_type, independent_key_count):
        rendered, _ = _collapse_type_expression(raw_type)
        assert f"... {independent_key_count} keys" in rendered

    def test_first_keys_present_and_correctly_ordered(self, raw_type):
        rendered, _ = _collapse_type_expression(raw_type)
        shown = rendered[rendered.index("{") + 1 : rendered.rindex("}")]
        shown_keys = [k.strip() for k in shown.split(",")][:12]
        assert shown_keys == [
            "create",
            "kubernetes_version",
            "create_autoscaling_group",
            "name",
            "use_name_prefix",
            "availability_zones",
            "subnet_ids",
            "min_size",
            "max_size",
            "desired_size",
            "desired_size_type",
            "capacity_rebalance",
        ]

    def test_nested_second_level_keys_do_not_leak(self, raw_type):
        """`taints` nests its own `object({ key = ...; value = ...; effect =
        ...  })` -- those must not appear as first-level keys."""
        rendered, _ = _collapse_type_expression(raw_type)
        shown = rendered[rendered.index("{") + 1 : rendered.rindex("}")]
        keys = [k.strip() for k in shown.split(",")]
        assert "key" not in keys
        assert "value" not in keys
        assert "effect" not in keys

    def test_inline_comments_do_not_corrupt_extraction(self, raw_type):
        """The raw type carries `# Will fall back to map key`-style inline
        comments right after some attributes -- these must never get fused
        into a neighboring identifier."""
        rendered, _ = _collapse_type_expression(raw_type)
        shown = rendered[rendered.index("{") + 1 : rendered.rindex("}")]
        keys = [k.strip() for k in shown.split(",")]
        for key in keys[:-1]:  # last entry is the "... N keys" marker
            assert key.isidentifier() or all(c.isalnum() or c in "_-" for c in key), key
