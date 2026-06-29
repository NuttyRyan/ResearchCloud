variable "prism_central_endpoint" {
  description = "Prism Central host or IP"
  type        = string
}

variable "prism_central_port" {
  description = "Prism Central port"
  type        = number
  default     = 9440
}

variable "prism_central_username" {
  description = "Prism Central username"
  type        = string
}

variable "prism_central_password" {
  description = "Prism Central password or API key"
  type        = string
  sensitive   = true
}

variable "insecure" {
  description = "Skip TLS verification (lab only)"
  type        = bool
  default     = true
}
