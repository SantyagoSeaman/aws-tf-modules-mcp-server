locals {
  # Mirrors the real terraform-aws-modules/eventbridge idiom exactly: the
  # locals RHS that merge()-injects the synthetic "Name" key ALSO references
  # a SECOND var (append_pipe_postfix) in the same expression -- a strict
  # "this RHS references ONLY var_name" check never recognizes
  # local.eventbridge_pipes as an alias of var.pipes, so the merge-injected
  # key it introduces is never subtracted, and it leaks through as a bogus
  # observed field name once a downstream resource's for_each comprehension
  # reads it back off `each.value`.
  eventbridge_pipes = flatten([
    for index, pipe in var.pipes :
    merge(pipe, {
      "Name" = var.append_pipe_postfix ? "${index}-pipe" : index
    })
  ])
}

resource "example_pipe" "this" {
  for_each = { for k, v in local.eventbridge_pipes : k => v }

  name   = each.value.Name
  source = each.value.source
  target = each.value.target
}

resource "example_pipe_direct" "this" {
  # A second, more literal idiom: the merge() call lives directly in the
  # RESOURCE's own for_each comprehension RHS, with no locals indirection at
  # all -- "Direct" is injected here and read back off each.value below.
  for_each = { for k, v in var.pipes : k => merge(v, { "Direct" = k }) }

  direct = each.value.Direct
  arn    = each.value.arn
}
