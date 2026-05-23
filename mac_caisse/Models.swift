import Foundation

struct User: Codable, Identifiable, Hashable {
    var id: Int
    var username: String
    var password: String
    var role: String
}

struct Product: Codable, Identifiable, Hashable {
    var id: Int
    var barcode: String
    var name: String
    var price: Double
    var category: String
    var stock: Int
}

struct SaleItem: Codable, Hashable {
    var name: String
    var quantity: Int
    var price: Double
}

struct Sale: Codable, Identifiable, Hashable {
    var id: Int
    var sale_date: String
    var cashier_id: Int
    var cashier_name: String
    var total: Double
    var payment_method: String
    var amount_received: Double
    var change_returned: Double
    var items: [SaleItem]?
}

struct DashboardStats: Hashable {
    var totalRevenue: Double = 0.0
    var totalSalesCount: Int = 0
    var totalProductsCount: Int = 0
    var lowStockCount: Int = 0
    var todayRevenue: Double = 0.0
}
