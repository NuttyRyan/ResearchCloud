# Root Terraform configuration wiring the ResearchCloud provisioning modules.
# These modules are skeletons in Phase 1 and are fleshed out in Phase 2, where the
# backend invokes Terraform/Calm DSL to perform real provisioning.

module "research_files" {
  source         = "./modules/nutanix-files"
  name           = "research-files"
  cluster_ext_id = "REPLACE_WITH_CLUSTER_EXT_ID"
  size_gib       = 4096
}

module "research_objects" {
  source         = "./modules/nutanix-objects"
  name           = "research-objects"
  cluster_ext_id = "REPLACE_WITH_CLUSTER_EXT_ID"
  capacity_gib   = 8192
}
