resource "aws_opensearch_domain" "this" {
  dynamic "cluster_config" {
    for_each = length(var.cluster_config) > 0 ? [var.cluster_config] : []

    content {
      dynamic "cold_storage_options" {
        for_each = try([cluster_config.value.cold_storage_options], [])

        content {
          enabled = try(cold_storage_options.value.enabled, null)
        }
      }

      dedicated_master_count        = try(cluster_config.value.dedicated_master_count, 3)
      dedicated_master_enabled      = try(cluster_config.value.dedicated_master_enabled, true)
      dedicated_master_type         = try(cluster_config.value.dedicated_master_type, "c6g.large.search")
      instance_count                = try(cluster_config.value.instance_count, 3)
      instance_type                 = try(cluster_config.value.instance_type, "r6g.large.search")
      multi_az_with_standby_enabled = try(cluster_config.value.multi_az_with_standby_enabled, null)
      warm_count                    = try(cluster_config.value.warm_count, null)
      warm_enabled                  = try(cluster_config.value.warm_enabled, null)
      warm_type                     = try(cluster_config.value.warm_type, null)

      dynamic "node_options" {
        for_each = try(cluster_config.value.node_options, [])

        content {

          dynamic "node_config" {
            for_each = try([node_options.value.node_config], [])

            content {
              count   = try(node_config.value.count, null)
              enabled = try(node_config.value.enabled, true)
              type    = try(node_config.value.type, null)
            }
          }

          node_type = try(node_options.value.node_type, node_options.key, null)
        }
      }

      dynamic "zone_awareness_config" {
        for_each = try(cluster_config.value.zone_awareness_enabled, true) ? try([cluster_config.value.zone_awareness_config], []) : []

        content {
          availability_zone_count = try(zone_awareness_config.value.availability_zone_count, null)
        }
      }

      zone_awareness_enabled = try(cluster_config.value.zone_awareness_enabled, true)
    }
  }
}
