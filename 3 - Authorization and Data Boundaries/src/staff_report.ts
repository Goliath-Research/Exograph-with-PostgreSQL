import { ExographPriv } from "../generated/exograph.d.ts";

interface OrderLineRow {
  quantity: number;
  unitPriceCents: number;
  product: {
    category: string;
  };
}

interface OrderRow {
  orderedAt: string;
  orderStatus: string;
  orderItems?: OrderLineRow[];
}

export async function staffSalesReport(
  startDate: string,
  endDate: string,
  limit: number,
  exograph: ExographPriv,
): Promise<{ category: string; revenueCents: number }[]> {
  if (!Number.isInteger(limit) || limit < 1 || limit > 100) {
    throw new ExographError("limit must be an integer between 1 and 100");
  }
  const startMs = Date.parse(
    startDate.includes("T") ? startDate : `${startDate}T00:00:00Z`,
  );
  const endMs = Date.parse(
    endDate.includes("T") ? endDate : `${endDate}T00:00:00Z`,
  );
  if (Number.isNaN(startMs) || Number.isNaN(endMs) || startMs >= endMs) {
    throw new ExographError("Provide a valid [startDate, endDate) range");
  }

  const data = await exograph.executeQueryPriv<
    { orders: OrderRow[] },
    Record<string, never>,
    { AuthContext: { role: string } }
  >(
    `query {
      orders {
        orderedAt
        orderStatus
        orderItems {
          quantity
          unitPriceCents
          product {
            category
          }
        }
      }
    }`,
    {},
    { AuthContext: { role: "internal_staff_report" } },
  );

  const totals = new Map<string, number>();
  for (const order of data.orders ?? []) {
    if (order.orderStatus !== "PAID" && order.orderStatus !== "SHIPPED") {
      continue;
    }
    const orderedMs = Date.parse(order.orderedAt);
    if (Number.isNaN(orderedMs) || orderedMs < startMs || orderedMs >= endMs) {
      continue;
    }
    for (const item of order.orderItems ?? []) {
      const category = item.product.category;
      const lineCents = item.quantity * item.unitPriceCents;
      totals.set(category, (totals.get(category) ?? 0) + lineCents);
    }
  }

  return Array.from(totals.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(0, limit)
    .map(([category, revenueCents]) => ({ category, revenueCents }));
}
