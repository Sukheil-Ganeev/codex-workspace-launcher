# Terraform Infrastructure as Code

## Setup

```bash
# Install Terraform
brew install terraform  # macOS
# или
choco install terraform  # Windows

# Provider
cat > provider.tf << 'EOT'
terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
      version = "~> 0.100"
    }
  }
}

provider "yandex" {
  token     = var.yc_token
  cloud_id  = var.cloud_id
  folder_id = var.folder_id
  zone      = "ru-central1-a"
}
EOT
```

## Example: VM

```hcl
resource "yandex_compute_instance" "web" {
  name = "web-server"
  platform_id = "standard-v3"

  resources {
    cores  = 2
    memory = 4
  }

  boot_disk {
    initialize_params {
      image_id = "fd8fte6bebi857ortlja"  # Ubuntu 22.04
      size     = 20
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.default.id
    nat       = true
  }
}
```

## Commands

```bash
terraform init
terraform plan
terraform apply
terraform destroy
```

**См. также:** `assets/templates/terraform-*/`
