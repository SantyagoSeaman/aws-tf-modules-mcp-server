locals {
  # Single any-var (targets) referenced alongside a scalar guard var
  # (name_prefix, NOT type = any) in the same locals RHS - mirrors the real
  # eventbridge idiom. The alias must still bind: name_prefix is a scalar,
  # not an any-var, so it never counts toward the same-scope multi-any-var
  # guard added for the wafv2-composite regression.
  renamed_targets = [
    for t in var.targets : {
      arn      = t.arn
      role_arn = t.role_arn
      label    = "${var.name_prefix}-prefixed"
    }
  ]
}

resource "example_target" "this" {
  for_each = { for t in local.renamed_targets : t.label => t }

  arn  = each.value.arn
  role = each.value.role_arn
}
