locals {
  # Synthetic single-rule object mirroring the real terraform-aws-modules/
  # wafv2 web-acl-rule idiom: the RHS references THREE any-vars of the same
  # scope (action, override_action, statement). Must NOT bind as an alias
  # for any of the three - each stays honest-empty, never a shared union.
  #
  # Historical note: earlier drafts referenced `var.action.commented_direct`
  # here before the merge into local.rule; this text must never surface as
  # an observed field name (comment-only, not code).
  #
  # Lets us reuse the rule body from the root module's `dynamic "rule"`
  # block by rewriting every `rule.value.X` reference to `local.rule.X`.
  rule = {
    action          = var.action
    override_action = var.override_action
    statement       = var.statement
  }
}

resource "example_wafv2_web_acl_rule" "this" {
  dynamic "action" {
    for_each = try(local.rule.action, null) != null ? [local.rule.action] : []
    content {
      allow = action.value.allow
    }
  }

  dynamic "override_action" {
    for_each = try(local.rule.override_action, null) != null ? [local.rule.override_action] : []
    content {
      none = override_action.value.none
    }
  }

  dynamic "statement" {
    for_each = [local.rule.statement]
    content {
      ip_set_reference_statement = statement.value.ip_set_reference_statement
    }
  }
}
