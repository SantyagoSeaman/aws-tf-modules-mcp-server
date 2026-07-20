variable "action" {
  description = "Action rule (wafv2-composite fixture, mirrors the real terraform-aws-modules/wafv2 web-acl-rule idiom)."
  type        = any
  default     = null
}

variable "override_action" {
  description = "Override action rule."
  type        = any
  default     = null
}

variable "statement" {
  description = "Statement rule."
  type        = any
  default     = null
}
