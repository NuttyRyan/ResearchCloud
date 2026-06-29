variable "name" {
  description = "File server name"
  type        = string
}

variable "cluster_ext_id" {
  description = "Target cluster external ID"
  type        = string
}

variable "size_gib" {
  description = "File server size in GiB"
  type        = number
  default     = 1024
}
