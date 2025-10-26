variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-west2"
}

variable "zone" {
  type        = string
  default     = "us-west2-a"
}

variable "machine_type" {
  type        = string
  default     = "e2-standard-4"
}

variable "service_account_email" {
  type        = string
  description = "Service account for the VM"
}
