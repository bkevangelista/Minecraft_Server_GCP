terraform {
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 1.6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region = var.region
  zone = var.zone
  credentials = file("~/minecraft-sa-key.json")
}


resource "google_compute_network" "default" {
  name = "minecraft-network"
  auto_create_subnetworks = true
}

resource "google_compute_firewall" "minecraft" {
  name = "minecraft-fw"
  network = google_compute_network.default.name

  allow {
    protocol = "tcp"
    ports = ["25565"]
  }

  target_tags = ["minecraft-server"]
  source_ranges = ["192.168.0.160/32"]

  description = "Allow Minecraft traffic on port 25565"
}

resource "google_compute_address" "minecraft_ip" {
  name   = "minecraft-ip"
  region = var.region
}

resource "google_compute_instance" "minecraft_vm" {
  name         = "mc-server-v1"
  machine_type = var.machine_type
  zone         = var.zone
  tags         = ["minecraft-server"]

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"
      size  = 30
      type  = "pd-balanced"
    }
  }

  network_interface {
    network = google_compute_network.default.id
    access_config {
      nat_ip = google_compute_address.minecraft_ip.address
    }
  }

  metadata_startup_script = <<-EOT
    #!/bin/bash
    apt-get update
    apt-get install -y default-jre unzip wget

    mkdir -p /minecraft
    cd /minecraft

    # Download Cobbleverse server pack
    wget https://storage.googleapis.com/minecraft-cobblemon-bucket/cobblemon-server-pack/cobbleverse_server.zip -O server.zip
    unzip server.zip -d cobbleverse
    cd cobbleverse

    # Install Forge server
    java -jar forge-installer.jar --installServer

    # Accept EULA
    echo "eula=true" > eula.txt

    # Start server
    java -Xmx6G -Xms4G -jar forge-*.jar nogui
  EOT

  scheduling {
    preemptible       = false
    automatic_restart = true
  }

  service_account {
    email  = var.service_account_email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }
}

resource "google_storage_bucket" "minecraft_backups" {
  name          = "${var.project_id}-minecraft-backups"
  location      = var.region
  storage_class = "STANDARD"
  force_destroy = true
  uniform_bucket_level_access = true
}

output "minecraft_ip" {
  value = google_compute_address.minecraft_ip.address
}

output "backup_bucket" {
  value = google_storage_bucket.minecraft_backups.name
}