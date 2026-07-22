module "widget" {
  source = "../.."

  widget_config = {
    size  = "large"
    color = "blue"
  }
}

# Helper module with a same-named argument - must NOT be attributed to the
# target module above (its source is a registry id, not "../.." or a
# "../../modules/X" submodule path).
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  widget_config = {
    bogus = "should-not-be-attributed"
  }
}
