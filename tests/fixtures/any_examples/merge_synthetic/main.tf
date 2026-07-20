locals {
  # Comprehension rebind + merge()-injected synthetic key (idiom N2): every
  # element of var.targets gets a synthetic "name" key added that is NOT
  # part of the user-supplied shape - it must be subtracted from
  # observed_field_names, even though a downstream consumer reads it.
  targets_with_index = flatten([
    for i, t in var.targets : merge(t, { "name" = i })
  ])
}

resource "example_thing" "this" {
  dynamic "target" {
    for_each = local.targets_with_index

    content {
      name     = target.value.name
      arn      = target.value.arn
      role_arn = target.value.role_arn
    }
  }
}
