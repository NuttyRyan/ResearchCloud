variable "name" {
  description = "Object store name"
  type        = string
}

variable "cluster_ext_id" {
  description = "Target cluster external ID"
  type        = string
}

variable "capacity_gib" {
  description = "Object store capacity in GiB"
  type        = number
  default     = 2048
}
