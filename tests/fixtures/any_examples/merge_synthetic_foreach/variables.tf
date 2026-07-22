variable "pipes" {
  description = "Map of pipe configuration (for_each-merge-injection fixture, mirrors the real terraform-aws-modules/eventbridge `pipes` idiom)."
  type        = any
  default     = {}
}

variable "append_pipe_postfix" {
  description = "Whether to append a postfix to the injected Name (a SECOND var referenced alongside var.pipes in the same locals expression -- the real eventbridge idiom)."
  type        = bool
  default     = true
}
