output "minecraft_server_ip" {
  value = google_compute_address.minecraft_ip.address
}

output "minecraft_backup_bucket" {
  value = google_storage_bucket.minecraft_backups.name
}
