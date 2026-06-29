terraform {
  required_version = ">= 1.6.0"

  required_providers {
    nutanix = {
      source  = "nutanix/nutanix"
      version = ">= 2.0.0"
    }
  }
}
