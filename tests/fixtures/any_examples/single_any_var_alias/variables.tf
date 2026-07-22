variable "targets" {
  description = "List of target configuration maps (single-any-var-plus-scalar-guard fixture)."
  type        = any
  default     = []
}

variable "name_prefix" {
  description = "Scalar guard var referenced alongside var.targets in the same locals RHS (NOT type = any) - mirrors the real eventbridge idiom (local.eventbridge_pipes references var.pipes AND var.append_pipe_postfix). The alias must still bind: this is the single-any-var case the loosening from `refs == {var_name}` to `var_name in refs` was meant to fix, and the same-scope multi-ANY-var guard must not regress it."
  type        = string
  default     = ""
}
