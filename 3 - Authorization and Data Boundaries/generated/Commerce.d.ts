
export interface Customer {
	customerId: number
	customerName: string
	orders: Order[] | undefined
}

export interface Order {
	orderId: number
	customer: Customer
	orderedAt: Instant
	orderStatus: string
	orderItems: OrderItem[] | undefined
}

export interface OrderItem {
	orderItemId: number
	order: Order
	lineNo: number
	product: Product
	quantity: number
	unitPriceCents: number
}

export interface Product {
	sku: string
	productName: string
	category: string
	orderItems: OrderItem[] | undefined
}

