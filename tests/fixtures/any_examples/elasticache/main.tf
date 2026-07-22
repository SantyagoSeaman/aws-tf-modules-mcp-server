locals {
  in_replication_group = var.replication_group_id != null

  tags = merge(var.tags, { terraform-aws-modules = "elasticache" })
}

resource "aws_elasticache_cluster" "this" {
  count = var.create && var.create_cluster ? 1 : 0

  apply_immediately          = var.apply_immediately
  auto_minor_version_upgrade = var.auto_minor_version_upgrade
  availability_zone          = var.availability_zone
  az_mode                    = local.in_replication_group ? null : var.az_mode
  cluster_id                 = var.cluster_id
  engine                     = local.in_replication_group ? null : var.engine
  engine_version             = local.in_replication_group ? null : var.engine_version
  final_snapshot_identifier  = var.final_snapshot_identifier
  ip_discovery               = var.ip_discovery

  dynamic "log_delivery_configuration" {
    for_each = { for k, v in var.log_delivery_configuration : k => v if var.engine != "memcached" && !local.in_replication_group }

    content {
      destination      = try(log_delivery_configuration.value.create_cloudwatch_log_group, true) && log_delivery_configuration.value.destination_type == "cloudwatch-logs" ? aws_cloudwatch_log_group.this[log_delivery_configuration.key].name : log_delivery_configuration.value.destination
      destination_type = log_delivery_configuration.value.destination_type
      log_format       = log_delivery_configuration.value.log_format
      log_type         = try(log_delivery_configuration.value.log_type, log_delivery_configuration.key)
    }
  }

  maintenance_window           = local.in_replication_group ? null : var.maintenance_window
  network_type                 = var.network_type
  node_type                    = local.in_replication_group ? null : var.node_type
  notification_topic_arn       = local.in_replication_group ? null : var.notification_topic_arn
  num_cache_nodes              = local.in_replication_group ? null : var.num_cache_nodes
  outpost_mode                 = var.outpost_mode
  port                         = local.in_replication_group ? null : coalesce(var.port, local.port)
  preferred_availability_zones = var.preferred_availability_zones
  preferred_outpost_arn        = var.preferred_outpost_arn
  replication_group_id         = var.create && var.create_replication_group ? aws_elasticache_replication_group.this[0].id : var.replication_group_id
  snapshot_arns                = local.in_replication_group ? null : var.snapshot_arns
  snapshot_name                = local.in_replication_group ? null : var.snapshot_name
  snapshot_retention_limit     = local.in_replication_group ? null : var.snapshot_retention_limit
  snapshot_window               = local.in_replication_group ? null : var.snapshot_window
  transit_encryption_enabled   = var.engine == "memcached" ? var.transit_encryption_enabled : null

  tags = local.tags

  timeouts {
    create = try(var.timeouts.create, null)
    update = try(var.timeouts.update, null)
    delete = try(var.timeouts.delete, null)
  }
}

locals {
  create_cloudwatch_log_group = var.create && var.engine != "memcached"
}

resource "aws_cloudwatch_log_group" "this" {
  for_each = { for k, v in var.log_delivery_configuration : k => v if local.create_cloudwatch_log_group && try(v.create_cloudwatch_log_group, true) && try(v.destination_type, "") == "cloudwatch-logs" }

  name              = "/aws/elasticache/${try(each.value.cloudwatch_log_group_name, coalesce(var.cluster_id, var.replication_group_id), "")}"
  retention_in_days = try(each.value.cloudwatch_log_group_retention_in_days, 14)
  kms_key_id        = try(each.value.cloudwatch_log_group_kms_key_id, null)
  skip_destroy      = try(each.value.cloudwatch_log_group_skip_destroy, null)
  log_group_class   = try(each.value.cloudwatch_log_group_class, null)

  tags = merge(local.tags, try(each.value.tags, {}))
}
