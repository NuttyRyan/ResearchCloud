# Skeleton module for deploying a Nutanix Files server.
#
# Phase 2 wires this to the nutanix_file_server resource (or a Calm DSL runbook).
# Kept as a documented placeholder so the Terraform layout is in place.

locals {
  file_server = {
    name           = var.name
    cluster_ext_id = var.cluster_ext_id
    size_gib       = var.size_gib
  }
}

output "file_server" {
  description = "Requested file server configuration"
  value       = local.file_server
}
