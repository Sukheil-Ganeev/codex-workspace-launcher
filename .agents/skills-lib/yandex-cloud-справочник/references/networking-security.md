# Networking & Security

## VPC (Virtual Private Cloud)

```bash
# Создать сеть
yc vpc network create --name tourism-network

# Создать подсеть
yc vpc subnet create \
  --name tourism-subnet-a \
  --network-name tourism-network \
  --zone ru-central1-a \
  --range 10.1.0.0/24
```

## Security Groups (Firewall)

```bash
yc vpc security-group create \
  --name web-server-sg \
  --rule "direction=ingress,port=22,protocol=tcp,v4-cidrs=[YOUR_IP/32]" \
  --rule "direction=ingress,port=80,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=ingress,port=443,protocol=tcp,v4-cidrs=[0.0.0.0/0]" \
  --rule "direction=egress,protocol=any,v4-cidrs=[0.0.0.0/0]" \
  --network-name tourism-network
```

## Load Balancer

```bash
# Network Load Balancer (L3)
yc load-balancer network-load-balancer create \
  --name web-lb \
  --target-group target-group-id=$TG_ID

# Application Load Balancer (L7)
yc application-load-balancer load-balancer create \
  --name web-alb
```

**Best Practice:** Ограничивай SSH (port 22) только своим IP.
