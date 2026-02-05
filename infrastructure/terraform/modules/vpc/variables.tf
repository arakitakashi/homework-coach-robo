# VPC Module Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "asia-northeast1"
}

variable "name_prefix" {
  description = "Prefix for resource names"
  type        = string
  default     = "homework-coach"
}

variable "connector_subnet_cidr" {
  description = "CIDR range for the VPC connector subnet"
  type        = string
  default     = "10.8.0.0/28"
}

variable "vpc_connector_cidr" {
  description = "CIDR range for the VPC Access Connector"
  type        = string
  default     = "10.9.0.0/28"
}

variable "connector_machine_type" {
  description = "Machine type for VPC connector instances"
  type        = string
  default     = "e2-micro"
}

variable "connector_min_instances" {
  description = "Minimum number of connector instances"
  type        = number
  default     = 2
}

variable "connector_max_instances" {
  description = "Maximum number of connector instances"
  type        = number
  default     = 3
}
