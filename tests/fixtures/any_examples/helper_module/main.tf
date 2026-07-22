resource "widget_thing" "this" {
  size  = try(var.widget_config.size, null)
  color = try(var.widget_config.color, null)
}
