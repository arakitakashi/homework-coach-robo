# VPC Module Outputs

output "network_id" {
  description = "The ID of the VPC network"
  value       = google_compute_network.main.id
}

output "network_name" {
  description = "The name of the VPC network"
  value       = google_compute_network.main.name
}

output "network_self_link" {
  description = "The self link of the VPC network"
  value       = google_compute_network.main.self_link
}

output "connector_id" {
  description = "The ID of the VPC Access Connector"
  value       = google_vpc_access_connector.main.id
}

output "connector_name" {
  description = "The name of the VPC Access Connector"
  value       = google_vpc_access_connector.main.name
}

output "connector_self_link" {
  description = "The self link of the VPC Access Connector"
  value       = google_vpc_access_connector.main.self_link
}

output "private_vpc_connection" {
  description = "The private VPC connection for managed services"
  value       = google_service_networking_connection.private_vpc_connection.network
}
