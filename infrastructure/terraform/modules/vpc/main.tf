# VPC Module
# Creates a VPC network and VPC Access Connector for serverless services.

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.name_prefix}-vpc"
  project                 = var.project_id
  auto_create_subnetworks = false
  description             = "VPC network for ${var.name_prefix}"
}

# Subnet for VPC Connector
resource "google_compute_subnetwork" "connector" {
  name          = "${var.name_prefix}-connector-subnet"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.main.id
  ip_cidr_range = var.connector_subnet_cidr

  private_ip_google_access = true

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# VPC Access Connector for Cloud Run to access Redis
resource "google_vpc_access_connector" "main" {
  name          = "${var.name_prefix}-connector"
  project       = var.project_id
  region        = var.region
  network       = google_compute_network.main.id
  ip_cidr_range = var.vpc_connector_cidr

  machine_type  = var.connector_machine_type
  min_instances = var.connector_min_instances
  max_instances = var.connector_max_instances
}

# Private Service Connection for managed services (Redis, etc.)
resource "google_compute_global_address" "private_ip_range" {
  name          = "${var.name_prefix}-private-ip-range"
  project       = var.project_id
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# Firewall rule to allow internal traffic
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.name_prefix}-allow-internal"
  project = var.project_id
  network = google_compute_network.main.name

  allow {
    protocol = "icmp"
  }

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  source_ranges = [var.connector_subnet_cidr, var.vpc_connector_cidr]
  priority      = 1000
}

# Firewall rule to allow health checks from Google
resource "google_compute_firewall" "allow_health_check" {
  name    = "${var.name_prefix}-allow-health-check"
  project = var.project_id
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
  }

  # Google Cloud health check IP ranges
  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
  priority      = 1000
}
