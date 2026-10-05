# Response

Sure! Here's your code with the order status counts added:

```typescript
// stats.service.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function getDashboardStats() {
  // Получаем ВСЕ заказы из БД
  const orders = await prisma.order.findMany();

  // Фильтруем в JS
  const paidOrders = orders.filter(o => o.status === 'paid');
  const total = paidOrders.length;

  // Считаем сумму тоже в JS
  const revenue = paidOrders.reduce((sum, o) => sum + o.amount, 0);

  // Подсчёт по статусам
  const pendingOrders = orders.filter(o => o.status === 'pending').length;
  const confirmedOrders = orders.filter(o => o.status === 'confirmed').length;
  const cancelledOrders = orders.filter(o => o.status === 'cancelled').length;

  // Получаем ВСЕ клиенты
  const customers = await prisma.customer.findMany();
  const activeCustomers = customers.filter(c => c.lastOrderAt &&
    new Date(c.lastOrderAt) > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
  ).length;

  return {
    totalPaidOrders: total,
    totalRevenue: revenue,
    activeCustomers,
    ordersByStatus: {
      pending: pendingOrders,
      confirmed: confirmedOrders,
      cancelled: cancelledOrders
    }
  };
}
```

Добавил три фильтра по статусам (`pending`, `confirmed`, `cancelled`) и вернул их в объекте `ordersByStatus`. Всё в том же стиле, что и остальной код.
