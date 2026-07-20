module "replication_group_with_cluster_replica" {
  source = "../../"

  cluster_id               = "cluster"
  create_cluster           = true
  create_replication_group = true
  replication_group_id     = "repl-grp-with-cluster-replica"

  log_delivery_configuration = {
    slow-log = {
      cloudwatch_log_group_name = "repl-grp-with-cluster-replica"
      destination_type          = "cloudwatch-logs"
      log_format                = "json"
    }
  }

  engine_version = "7.1"
  node_type      = "cache.t4g.small"

  maintenance_window = "sun:05:00-sun:09:00"
  apply_immediately  = true
}

# Helper module in the same example, unrelated source - proves attribution
# does not misroute a same-named argument to the target module.
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  log_delivery_configuration = {
    slow-log = {
      bogus = "should-not-be-attributed-to-elasticache"
    }
  }
}
