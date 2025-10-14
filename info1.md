terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.0"
    }
  }
}

variable "project_id" {
  description = "The ID of the Google Cloud project."
  type        = string
}

variable "region" {
  description = "The region for the resources."
  type        = string
}

data "google_project" "project" {}

resource "google_service_account" "gke_sa" {
  project      = var.project_id
  account_id   = "gke-sa"
  display_name = "GKE Service Account"
}

resource "google_project_iam_member" "kms_encrypter_decrypter" {
  project = var.project_id
  role    = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "container_node_service_account" {
  project = var.project_id
  role    = "roles/container.nodeServiceAccount" # Corrected from roles/container.defaultNodeServiceAccount
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_kms_key_ring" "gke_keyring" {
  project  = var.project_id
  name     = "gke-keyring"
  location = var.region
}

resource "google_kms_crypto_key" "gke_boot_key" {
  name      = "gke-boot-key"
  key_ring  = google_kms_key_ring.gke_keyring.id
  purpose   = "ENCRYPT_DECRYPT"
}

resource "google_kms_crypto_key_iam_member" "gke_boot_key_iam" {
  crypto_key_id = google_kms_crypto_key.gke_boot_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:service-${data.google_project.project.number}@compute-system.iam.gserviceaccount.com"
}

resource "google_project_iam_member" "monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "artifactregistry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}

resource "google_project_iam_member" "artifactregistry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.gke_sa.email}"
}
















project_id     = "your-gcp-project-id"
region         = "your-gcp-region"
