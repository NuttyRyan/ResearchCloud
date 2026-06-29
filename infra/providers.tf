provider "nutanix" {
  endpoint = var.prism_central_endpoint
  port     = var.prism_central_port
  username = var.prism_central_username
  password = var.prism_central_password
  insecure = var.insecure
}
