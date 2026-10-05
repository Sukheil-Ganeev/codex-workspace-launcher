# API Gateway

**OpenAPI 3.0 спецификация** для создания REST API.

## Пример

```yaml
openapi: 3.0.0
info:
  title: Tourism API
  version: 1.0.0

paths:
  /tours:
    get:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: d4e...
      responses:
        200:
          description: List of tours

  /bookings:
    post:
      x-yc-apigateway-integration:
        type: cloud_functions
        function_id: d4e...
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                tourId:
                  type: integer
                customerName:
                  type: string
      responses:
        201:
          description: Booking created
```

## Deploy

```bash
yc serverless api-gateway create \
  --name tourism-api \
  --spec=api-gateway.yaml

# Получить URL
yc serverless api-gateway get tourism-api
```

**См. также:** `assets/templates/serverless-api-gateway.yaml`
