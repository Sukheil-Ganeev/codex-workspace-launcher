# Shopify Cheatsheet -- CLI, API, Liquid, Webhooks, Тарифы

---

## Shopify CLI

```bash
# Установка
npm install -g @shopify/cli @shopify/theme

# Темы
shopify theme dev --store=myshop.myshopify.com   # Live preview
shopify theme push --store=myshop                 # Deploy
shopify theme pull --store=myshop                 # Download
shopify theme list --store=myshop                 # List themes
shopify theme info --store=myshop                 # Current theme info
shopify theme check                               # Lint theme (best practices)
shopify theme share                               # Share preview URL
shopify theme package                             # Package as ZIP

# Hydrogen (headless)
npm create @shopify/hydrogen@latest               # Create new store
shopify hydrogen dev                              # Run locally
shopify hydrogen deploy                           # Deploy to Oxygen

# Приложения
shopify app init                                  # Create new app
shopify app dev                                   # Run locally
shopify app deploy                                # Deploy
shopify app generate extension                    # Add extension
```

---

## REST Admin API Endpoints (Legacy)

**Base URL:** `https://{shop}.myshopify.com/admin/api/2025-01/`
**Auth:** `X-Shopify-Access-Token: {TOKEN}`

### Products
```
GET    /products.json                        # List products
GET    /products/{id}.json                   # Get product
POST   /products.json                        # Create product
PUT    /products/{id}.json                   # Update product
DELETE /products/{id}.json                   # Delete product
GET    /products/count.json                  # Count products
GET    /products/{id}/variants.json          # List variants
POST   /products/{id}/variants.json          # Create variant
GET    /products/{id}/images.json            # List images
POST   /products/{id}/images.json            # Upload image
```

### Orders
```
GET    /orders.json                          # List orders
GET    /orders/{id}.json                     # Get order
POST   /orders.json                          # Create order
PUT    /orders/{id}.json                     # Update order
POST   /orders/{id}/cancel.json              # Cancel order
GET    /orders/count.json                    # Count orders
GET    /orders/{id}/transactions.json        # List transactions
POST   /orders/{id}/fulfillments.json        # Create fulfillment
```

### Customers
```
GET    /customers.json                       # List customers
GET    /customers/{id}.json                  # Get customer
POST   /customers.json                       # Create customer
PUT    /customers/{id}.json                  # Update customer
GET    /customers/search.json?query=email:x  # Search customers
GET    /customers/count.json                 # Count customers
GET    /customers/{id}/orders.json           # Customer orders
```

### Collections
```
GET    /custom_collections.json              # Manual collections
GET    /smart_collections.json               # Auto collections
POST   /custom_collections.json              # Create collection
POST   /collects.json                        # Add product to collection
```

### Other
```
GET    /shop.json                            # Shop info
GET    /webhooks.json                        # List webhooks
POST   /webhooks.json                        # Create webhook
GET    /themes.json                          # List themes
GET    /metafields.json                      # List metafields
POST   /metafields.json                      # Create metafield
```

---

## GraphQL Admin API

**Endpoint:** `POST https://{shop}.myshopify.com/admin/api/2025-01/graphql.json`

### Products

```graphql
# List products
query {
  products(first: 50, query: "product_type:Tour") {
    edges {
      node { id title handle status priceRangeV2 { minVariantPrice { amount currencyCode } } }
      cursor
    }
    pageInfo { hasNextPage }
  }
}

# Create product
mutation {
  productCreate(input: {
    title: "Desert Safari"
    descriptionHtml: "<p>Premium tour</p>"
    productType: "Tour"
    vendor: "Dubai Tours"
    tags: ["desert", "adventure"]
    variants: [{ price: "350.00", sku: "DS-VIP" }]
  }) {
    product { id title handle }
    userErrors { field message }
  }
}

# Update product
mutation {
  productUpdate(input: { id: "gid://shopify/Product/123", title: "New Title" }) {
    product { id title }
    userErrors { field message }
  }
}
```

### Orders

```graphql
# List orders
query {
  orders(first: 20, sortKey: CREATED_AT, reverse: true) {
    edges {
      node {
        id name createdAt
        totalPriceSet { shopMoney { amount currencyCode } }
        customer { firstName lastName email }
        lineItems(first: 5) { edges { node { title quantity } } }
      }
    }
  }
}

# Fulfill order
mutation {
  fulfillmentCreateV2(fulfillment: {
    lineItemsByFulfillmentOrder: [{
      fulfillmentOrderId: "gid://shopify/FulfillmentOrder/123"
    }]
    trackingInfo: { number: "VOUCHER-1234" company: "Email" }
  }) {
    fulfillment { id status }
    userErrors { field message }
  }
}
```

### Metafields

```graphql
# Set metafield on product
mutation {
  metafieldsSet(metafields: [{
    ownerId: "gid://shopify/Product/123"
    namespace: "custom"
    key: "duration"
    value: "6 hours"
    type: "single_line_text_field"
  }]) {
    metafields { id namespace key value }
    userErrors { field message }
  }
}
```

### Webhooks

```graphql
# Create webhook subscription
mutation {
  webhookSubscriptionCreate(
    topic: ORDERS_CREATE
    webhookSubscription: {
      callbackUrl: "https://yourdomain.com/webhooks/orders"
      format: JSON
    }
  ) {
    webhookSubscription { id topic }
    userErrors { field message }
  }
}

# List webhooks
query {
  webhookSubscriptions(first: 20) {
    edges { node { id topic callbackUrl } }
  }
}
```

---

## Liquid Quick Reference

### Objects
```liquid
{{ shop.name }}                              <!-- Название магазина -->
{{ shop.email }}                             <!-- Email магазина -->
{{ shop.currency }}                          <!-- AED -->
{{ product.title }}                          <!-- Название продукта -->
{{ product.price | money }}                  <!-- 350.00 AED -->
{{ product.handle }}                         <!-- desert-safari-vip -->
{{ product.type }}                           <!-- Tour -->
{{ product.vendor }}                         <!-- Dubai Tours -->
{{ product.tags }}                           <!-- ["desert", "vip"] -->
{{ product.featured_image | image_url: width: 800 }}
{{ product.metafields.custom.duration }}      <!-- 6 hours -->
{{ collection.title }}                       <!-- Excursions -->
{{ collection.products_count }}              <!-- 25 -->
{{ customer.first_name }}                    <!-- Suheil -->
{{ customer.orders_count }}                  <!-- 5 -->
{{ order.name }}                             <!-- #1001 -->
{{ order.total_price | money }}              <!-- 350.00 AED -->
{{ request.locale.iso_code }}                <!-- en / ru / ar -->
{{ canonical_url }}                          <!-- Full URL -->
```

### Tags (Control Flow)
```liquid
{% if product.available %}
  In Stock
{% elsif product.compare_at_price > product.price %}
  On Sale
{% else %}
  Sold Out
{% endif %}

{% for product in collection.products %}
  {{ product.title }} - {{ product.price | money }}
{% endfor %}

{% unless product.type == 'Gift Card' %}
  <button>Add to Cart</button>
{% endunless %}

{% case product.type %}
  {% when 'Tour' %}Tour details...
  {% when 'Ticket' %}Ticket info...
  {% else %}General product
{% endcase %}

{% assign tours = collection.products | where: "type", "Tour" %}
{% assign sorted = collection.products | sort: "price" %}
{% capture tour_url %}/products/{{ product.handle }}{% endcapture %}
```

### Filters
```liquid
{{ 25000 | money }}                          <!-- 250.00 AED -->
{{ 25000 | money_with_currency }}            <!-- 250.00 AED -->
{{ 25000 | money_without_currency }}         <!-- 250.00 -->
{{ "Desert Safari" | handleize }}            <!-- desert-safari -->
{{ "Desert Safari" | downcase }}             <!-- desert safari -->
{{ "Desert Safari" | upcase }}               <!-- DESERT SAFARI -->
{{ product.description | strip_html }}       <!-- Plain text -->
{{ product.description | truncate: 160 }}    <!-- First 160 chars... -->
{{ "now" | date: "%Y-%m-%d" }}              <!-- 2026-02-13 -->
{{ "now" | date: "%B %d, %Y" }}             <!-- February 13, 2026 -->
{{ 350 | plus: 17.5 }}                       <!-- 367.5 (price + VAT) -->
{{ 350 | times: 0.05 }}                      <!-- 17.5 (VAT amount) -->
{{ product.images | size }}                  <!-- 5 -->
{{ product.tags | join: ", " }}              <!-- desert, vip, evening -->
{{ "Hello" | append: " World" }}             <!-- Hello World -->
{{ product.title | json }}                   <!-- "Desert Safari" (escaped) -->
{{ product.title | url_encode }}             <!-- Desert%20Safari -->
{{ product.featured_image | image_url: width: 600, height: 400, crop: 'center' }}
```

---

## Webhook Topics

### Orders
```
orders/create          # Новый заказ
orders/updated         # Заказ обновлён
orders/paid            # Заказ оплачен
orders/cancelled       # Заказ отменён
orders/fulfilled       # Заказ выполнен
orders/partially_fulfilled
```

### Products
```
products/create        # Продукт создан
products/update        # Продукт обновлён
products/delete        # Продукт удалён
```

### Customers
```
customers/create       # Клиент создан
customers/update       # Клиент обновлён
customers/delete       # Клиент удалён
```

### Other
```
carts/create           # Корзина создана
carts/update           # Корзина обновлена
checkouts/create       # Checkout начат
refunds/create         # Возврат создан
app/uninstalled        # App удалён
themes/update          # Тема обновлена
inventory_levels/update # Инвентарь изменён
```

---

## Тарифы и лимиты (Quick Reference)

### Планы
```
Starter:   $5/мес    -- ссылки, соцсети
Basic:     $39/мес   -- полный магазин, 2 staff
Grow:      $105/мес  -- Flow, reports, 5 staff
Advanced:  $399/мес  -- advanced reports, 15 staff
Plus:      $2,300+   -- enterprise
Retail:    $89/мес   -- POS-терминал
```

### API Rate Limits
```
REST API:
  Basic/Grow:   40 req/мин, 2 req/сек recovery
  Advanced:     40 req/мин, 4 req/сек recovery
  Plus:         400 req/мин, 20 req/сек recovery

GraphQL API:
  All plans:    1,000 cost points bucket
  Recovery:     50 points/сек
  Plus:         2,000 points, 100/сек recovery
```

### Store Limits
```
Products:       unlimited
Variants:       до 2,000 per product (GraphQL)
                до 100 per product (REST legacy)
Collections:    5,000 automated, unlimited manual
Images:         до 250 per product
Staff:          Basic 2, Grow 5, Advanced 15
Languages:      до 20
Markets:        до 50
Metafields:     unlimited (200 per resource REST call)
Files:          unlimited storage
Bandwidth:      unlimited
```

### Webhooks
```
Max subscriptions:  unlimited
Timeout:            5 seconds (respond fast!)
Retries:            19 times over 48 hours
Format:             JSON or XML
Signature:          HMAC-SHA256 (X-Shopify-Hmac-Sha256)
```

---

## Shopify Flow -- Common Triggers

```
Order created              # Новый заказ
Order paid                 # Оплачен
Order fulfilled            # Выполнен
Order cancelled            # Отменён
Customer created           # Новый клиент
Product added to store     # Новый продукт
Inventory quantity changed # Инвентарь изменился
Draft order created        # Черновик заказа
```

## Common Actions
```
Add order tag              # Тег на заказ
Add customer tag           # Тег на клиента
Send HTTP request          # API вызов (Telegram, CRM)
Send internal email        # Email уведомление
Create draft order         # Черновик заказа
Cancel order               # Отмена
Hide product               # Скрыть продукт
Add order note             # Примечание
Wait                       # Задержка (часы/дни)
```

---

## Полезные URL

```
Admin:           https://{shop}.myshopify.com/admin
GraphiQL:        https://{shop}.myshopify.com/admin/api/2025-01/graphql.json
Docs:            https://shopify.dev
Liquid Ref:      https://shopify.dev/docs/api/liquid
Theme Check:     https://shopify.dev/docs/themes/tools/theme-check
App Store:       https://apps.shopify.com
Community:       https://community.shopify.com
Partners:        https://partners.shopify.com
Hydrogen:        https://hydrogen.shopify.dev
Status:          https://status.shopify.com
```
