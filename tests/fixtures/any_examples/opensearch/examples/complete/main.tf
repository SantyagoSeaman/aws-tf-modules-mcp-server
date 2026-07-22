module "opensearch" {
  source = "../.."

  # Domain
  cluster_config = {
    instance_count           = 3
    dedicated_master_enabled = true
    dedicated_master_type    = "c6g.large.search"
    instance_type            = "r6g.large.search"

    node_options = {
      coordinator = {
        node_config = {
          enabled = true
          count   = 3
          type    = "m6g.large.search"
        }
      }
    }

    zone_awareness_config = {
      availability_zone_count = 3
    }

    zone_awareness_enabled = true
  }
}

# Helper module in the same example, unrelated source - proves attribution
# does not misroute a same-named argument to the target module.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 6.0"

  name = local.name
  cidr = local.vpc_cidr

  cluster_config = {
    bogus = "should-not-be-attributed-to-opensearch"
  }
}
