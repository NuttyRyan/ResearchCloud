# Skeleton module for deploying a Nutanix Objects store.
#
# Phase 2 wires this to the nutanix_object_store resource (or a Calm DSL runbook).
# Kept as a documented placeholder so the Terraform layout is in place.

locals {
  object_store = {
    name           = var.name
    cluster_ext_id = var.cluster_ext_id
    capacity_gib   = var.capacity_gib
  }
}

output "object_store" {
  description = "Requested object store configuration"
  value       = local.object_store
}
