import Foundation
import Combine

class FirebaseManager: ObservableObject {
    static let shared = FirebaseManager()
    
    let dbURL = "https://test2-mdr-default-rtdb.europe-west1.firebasedatabase.app/"
    
    private func makeRequest(path: String, method: String, body: Data? = nil) -> URLRequest {
        let url = URL(string: "\(dbURL)\(path).json")!
        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 10
        if let body = body {
            request.httpBody = body
        }
        return request
    }
    
    // MARK: - Products
    func fetchProducts() async throws -> [Product] {
        let request = makeRequest(path: "products", method: "GET")
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 401, userInfo: [NSLocalizedDescriptionKey: "Erreur HTTP : Non autorisé ou inaccessible. Vérifie tes règles Firebase !"])
        }
        
        if data.isEmpty || String(data: data, encoding: .utf8) == "null" {
            return []
        }
        
        // Firebase returns a dictionary: [barcode: Product]
        let dict = try JSONDecoder().decode([String: Product].self, from: data)
        return dict.values.sorted(by: { $0.name < $1.name })
    }
    
    func saveProduct(_ product: Product) async throws {
        let body = try JSONEncoder().encode(product)
        let request = makeRequest(path: "products/\(product.barcode)", method: "PUT", body: body)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 500, userInfo: [NSLocalizedDescriptionKey: "Échec de l'enregistrement du produit sur Firebase."])
        }
    }
    
    func deleteProduct(barcode: String) async throws {
        let request = makeRequest(path: "products/\(barcode)", method: "DELETE")
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 500, userInfo: [NSLocalizedDescriptionKey: "Échec de la suppression du produit."])
        }
    }
    
    // MARK: - Users
    func fetchUsers() async throws -> [User] {
        let request = makeRequest(path: "users", method: "GET")
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 401, userInfo: [NSLocalizedDescriptionKey: "Erreur d'accès aux utilisateurs."])
        }
        
        if data.isEmpty || String(data: data, encoding: .utf8) == "null" {
            return []
        }
        
        let dict = try JSONDecoder().decode([String: User].self, from: data)
        return dict.values.sorted(by: { $0.username < $1.username })
    }
    
    func fetchUsersCounter() async throws -> Int {
        let request = makeRequest(path: "users_counter", method: "GET")
        let (data, _) = try await URLSession.shared.data(for: request)
        
        if data.isEmpty || String(data: data, encoding: .utf8) == "null" {
            return 2 // Default starting counter
        }
        return try JSONDecoder().decode(Int.self, from: data)
    }
    
    func saveUser(_ user: User) async throws {
        let body = try JSONEncoder().encode(user)
        let request = makeRequest(path: "users/\(user.id)", method: "PUT", body: body)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 500, userInfo: [NSLocalizedDescriptionKey: "Échec de l'enregistrement de l'utilisateur."])
        }
    }
    
    func saveUsersCounter(_ counter: Int) async throws {
        let body = try JSONEncoder().encode(counter)
        let request = makeRequest(path: "users_counter", method: "PUT", body: body)
        let _ = try await URLSession.shared.data(for: request)
    }
    
    func deleteUser(id: Int) async throws {
        let request = makeRequest(path: "users/\(id)", method: "DELETE")
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 500, userInfo: [NSLocalizedDescriptionKey: "Échec de la suppression de l'utilisateur."])
        }
    }
    
    // MARK: - Sales
    func fetchSales() async throws -> [Sale] {
        let request = makeRequest(path: "sales", method: "GET")
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 401, userInfo: [NSLocalizedDescriptionKey: "Erreur d'accès aux ventes."])
        }
        
        if data.isEmpty || String(data: data, encoding: .utf8) == "null" {
            return []
        }
        
        let dict = try JSONDecoder().decode([String: Sale].self, from: data)
        return dict.values.sorted(by: { $0.sale_date > $1.sale_date })
    }
    
    func fetchSalesCounter() async throws -> Int {
        let request = makeRequest(path: "sales_counter", method: "GET")
        let (data, _) = try await URLSession.shared.data(for: request)
        
        if data.isEmpty || String(data: data, encoding: .utf8) == "null" {
            return 0
        }
        return try JSONDecoder().decode(Int.self, from: data)
    }
    
    func recordSale(sale: Sale, cartItems: [Product: Int]) async throws -> Int {
        // 1. Get and increment sales counter
        var nextId = try await fetchSalesCounter()
        nextId += 1
        
        // 2. Prepare sale object
        var preparedSale = sale
        preparedSale.id = nextId
        
        var itemsList: [SaleItem] = []
        for (product, qty) in cartItems {
            itemsList.append(SaleItem(name: product.name, quantity: qty, price: product.price))
            
            // 3. Update stock of products
            var updatedProduct = product
            updatedProduct.stock = max(0, product.stock - qty)
            try await saveProduct(updatedProduct)
        }
        preparedSale.items = itemsList
        
        // 4. Save sale record
        let body = try JSONEncoder().encode(preparedSale)
        let request = makeRequest(path: "sales/\(nextId)", method: "PUT", body: body)
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw NSError(domain: "FirebaseManager", code: 500, userInfo: [NSLocalizedDescriptionKey: "Échec de l'enregistrement de la vente."])
        }
        
        // 5. Update sales counter
        let counterBody = try JSONEncoder().encode(nextId)
        let counterRequest = makeRequest(path: "sales_counter", method: "PUT", body: counterBody)
        let _ = try await URLSession.shared.data(for: counterRequest)
        
        return nextId
    }
    
    // MARK: - Dashboard Stats
    func getDashboardStats(sales: [Sale], products: [Product]) -> DashboardStats {
        var stats = DashboardStats()
        stats.totalSalesCount = sales.count
        stats.totalProductsCount = products.count
        stats.lowStockCount = products.filter({ $0.stock < 5 }).count
        
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let todayStr = formatter.string(from: Date())
        
        for sale in sales {
            stats.totalRevenue += sale.total
            if sale.sale_date.hasPrefix(todayStr) {
                stats.todayRevenue += sale.total
            }
        }
        
        return stats
    }
}
