import SwiftUI
import AppKit

struct ContentView: View {
    @StateObject private var db = FirebaseManager.shared
    
    @State private var loggedInUser: User? = nil
    @State private var currentTab: String = "sales" // "sales" or "admin"
    
    var body: some View {
        ZStack {
            Theme.bgMain.ignoresSafeArea()
            
            if let user = loggedInUser {
                MainAppView(user: user, loggedInUser: $loggedInUser, currentTab: $currentTab)
            } else {
                LoginView(loggedInUser: $loggedInUser)
            }
        }
        .foregroundColor(Theme.fgText)
        .font(.system(size: 13, design: .sansSerif))
    }
}

// MARK: - LOGIN VIEW
struct LoginView: View {
    @Binding var loggedInUser: User?
    @State private var username = ""
    @State private var password = ""
    @State private var failedAttempts: [String: Int] = [:]
    @State private var errorMessage = ""
    @State private var isLoading = false
    
    var body: some View {
        VStack(spacing: 20) {
            VStack(spacing: 10) {
                Text("🐾")
                    .font(.system(size: 60))
                Text("Miaou POS")
                    .font(.system(size: 26, weight: .bold))
                Text("Connectez-vous pour commencer la session")
                    .foregroundColor(Theme.fgMuted)
                    .font(.subheadline)
            }
            .padding(.bottom, 20)
            
            VStack(alignment: .leading, spacing: 15) {
                VStack(alignment: .leading, spacing: 5) {
                    Text("Identifiant")
                        .font(.system(size: 11, weight: .bold))
                    TextField("", text: $username)
                        .textFieldStyle(PlainTextFieldStyle())
                        .padding(10)
                        .background(Theme.bgInput)
                        .cornerRadius(6)
                        .overlay(RoundedRectangle(cornerRadius: 6).stroke(Theme.accent.opacity(0.3), lineWidth: 1))
                }
                
                VStack(alignment: .leading, spacing: 5) {
                    Text("Mot de passe")
                        .font(.system(size: 11, weight: .bold))
                    SecureField("", text: $password)
                        .textFieldStyle(PlainTextFieldStyle())
                        .padding(10)
                        .background(Theme.bgInput)
                        .cornerRadius(6)
                        .overlay(RoundedRectangle(cornerRadius: 6).stroke(Theme.accent.opacity(0.3), lineWidth: 1))
                }
            }
            .frame(width: 320)
            
            if !errorMessage.isEmpty {
                Text(errorMessage)
                    .foregroundColor(Theme.red)
                    .font(.caption)
                    .multilineTextAlignment(.center)
                    .frame(width: 320)
            }
            
            Button(action: attemptLogin) {
                HStack {
                    Spacer()
                    if isLoading {
                        ProgressView().controlSize(.small)
                    } else {
                        Text("Se connecter")
                            .font(.system(size: 14, weight: .bold))
                    }
                    Spacer()
                }
                .padding(.vertical, 12)
                .background(Theme.accent)
                .foregroundColor(.white)
                .cornerRadius(6)
            }
            .buttonStyle(PlainButtonStyle())
            .frame(width: 320)
            .disabled(isLoading)
            
            Text("Admin : admin / admin123  |  Caissier : caissier / caissier123")
                .foregroundColor(Theme.fgMuted)
                .font(.system(size: 9))
                .padding(.top, 15)
        }
        .padding(40)
        .background(Theme.bgCard)
        .cornerRadius(12)
        .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.white.opacity(0.1), lineWidth: 1))
    }
    
    func attemptLogin() {
        let userStr = username.trimmingCharacters(in: .whitespacesAndNewlines)
        let passStr = password.trimmingCharacters(in: .whitespacesAndNewlines)
        
        if userStr.isEmpty || passStr.isEmpty {
            errorMessage = "Veuillez remplir tous les champs !"
            return
        }
        
        if failedAttempts[userStr, default: 0] >= 5 {
            errorMessage = "Ce compte est verrouillé ! 🔒"
            NSSound.beep()
            return
        }
        
        isLoading = true
        errorMessage = ""
        
        Task {
            do {
                let users = try await FirebaseManager.shared.fetchUsers()
                isLoading = false
                
                if let foundUser = users.first(where: { $0.username == userStr && $0.password == passStr }) {
                    failedAttempts[userStr] = 0
                    loggedInUser = foundUser
                } else {
                    failedAttempts[userStr, default: 0] += 1
                    let count = failedAttempts[userStr, default: 0]
                    if count >= 5 {
                        errorMessage = "Compte verrouillé suite à 5 échecs ! 🔒"
                        triggerMacGlitch(username: userStr)
                    } else {
                        errorMessage = "Identifiant ou mot de passe incorrect.\nIl reste \(5 - count) tentative(s)."
                    }
                }
            } catch {
                isLoading = false
                errorMessage = "Erreur de connexion : \(error.localizedDescription)"
            }
        }
    }
    
    func triggerMacGlitch(username: String) {
        let screen = NSScreen.main
        let screenWidth = screen?.frame.width ?? 1280
        let screenHeight = screen?.frame.height ?? 800
        
        // Obtenir la quantité de RAM pour dimensionner le glitch
        let ramGb = ProcessInfo.processInfo.physicalMemory / (1024 * 1024 * 1024)
        let numWindows = ramGb <= 4 ? 50 : (ramGb >= 32 ? 100 : Int(50 + (ramGb - 4) * 2))
        
        for i in 0..<numWindows {
            DispatchQueue.main.asyncAfter(deadline: .now() + Double(i) * 0.08) {
                let window = NSWindow(
                    contentRect: NSRect(
                        x: CGFloat.random(in: 100...(screenWidth - 400)),
                        y: CGFloat.random(in: 100...(screenHeight - 200)),
                        width: 350,
                        height: 150
                    ),
                    styleMask: [.titled, .closable],
                    backing: .buffered,
                    defer: false
                )
                window.title = "⚠️ ERREUR CRITIQUE ⚠️"
                window.isReleasedWhenClosed = false
                window.level = .floating
                
                let hosting = NSHostingView(rootView: GlitchWindowView(index: i, numWindows: numWindows, username: username, ram: Int(ramGb)))
                window.contentView = hosting
                window.makeKeyAndOrderFront(nil)
                
                NSSound(named: "Basso")?.play()
                
                // Physics bounce simulation
                var x = window.frame.origin.x
                var y = window.frame.origin.y
                var dx = CGFloat.random(in: 4...8) * (Bool.random() ? 1 : -1)
                var dy = CGFloat.random(in: 4...8) * (Bool.random() ? 1 : -1)
                
                Timer.scheduledTimer(withTimeInterval: 0.03, repeats: true) { timer in
                    if !window.isVisible {
                        timer.invalidate()
                        return
                    }
                    x += dx
                    y += dy
                    
                    if x <= 0 { x = 0; dx = -dx }
                    if x + 350 >= screenWidth { x = screenWidth - 350; dx = -dx }
                    if y <= 0 { y = 0; dy = -dy }
                    if y + 150 >= screenHeight { y = screenHeight - 150; dy = -dy }
                    
                    window.setFrameOrigin(NSPoint(x: x, y: y))
                }
            }
        }
    }
}

struct GlitchWindowView: View {
    let index: Int
    let numWindows: Int
    let username: String
    let ram: Int
    
    var body: some View {
        HStack(spacing: 15) {
            Text("❌")
                .font(.system(size: 40))
            VStack(alignment: .leading, spacing: 5) {
                Text("COMPTE VERROUILLÉ")
                    .font(.system(size: 14, weight: .bold))
                    .foregroundColor(Theme.red)
                Text("Tentatives épuisées pour : \(username)\nAccès bloqué temporairement ! 🔒\n[Alerte \(index+1)/\(numWindows) - \(ram) Go RAM]")
                    .font(.system(size: 10))
                    .foregroundColor(Theme.fgText)
                    .lineLimit(3)
            }
            Spacer()
        }
        .padding()
        .frame(width: 350, height: 150)
        .background(Color(hex: "#2d1c1c"))
    }
}

// MARK: - MAIN APP VIEW
struct MainAppView: View {
    let user: User
    @Binding var loggedInUser: User?
    @Binding var currentTab: String
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack(spacing: 15) {
                Text("👤 Connecté : \(user.username) (\(user.role))")
                    .font(.system(size: 12, weight: .bold))
                
                Spacer()
                
                Text("🐾 Miaou POS")
                    .font(.system(size: 16, weight: .bold))
                    .foregroundColor(Theme.accent)
                
                Spacer()
                
                if user.role == "Admin" {
                    Button(action: {
                        currentTab = currentTab == "sales" ? "admin" : "sales"
                    }) {
                        Text(currentTab == "sales" ? "⚙️ Administration" : "🛒 Passer à la Caisse")
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(currentTab == "sales" ? Theme.amber : Theme.green)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                
                Button(action: { loggedInUser = nil }) {
                    Text("🚪 Déconnexion")
                        .foregroundColor(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Theme.red)
                        .cornerRadius(5)
                }
                .buttonStyle(PlainButtonStyle())
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 12)
            .background(Theme.bgCard)
            .overlay(Rectangle().stroke(Color.white.opacity(0.05), lineWidth: 1).frame(height: 1), alignment: .bottom)
            
            // Body
            if currentTab == "sales" {
                SalesView(user: user)
            } else {
                AdminView()
            }
        }
    }
}

// MARK: - SALES VIEW
struct SalesView: View {
    let user: User
    
    @State private var products: [Product] = []
    @State private var cart: [Product: Int] = [:]
    @State private var searchQuery = ""
    @State private var selectedCategory: String? = nil
    
    @State private var showPaymentModal = false
    @State private var activeTicketPath: String? = nil
    @State private var showTicketPreview = false
    @State private var ticketContent = ""
    
    var body: some View {
        HStack(spacing: 10) {
            // Left Catalog Column
            VStack(spacing: 10) {
                // Search Bar
                HStack {
                    Text("🔍 Nom ou Code :")
                        .font(.system(size: 12, weight: .bold))
                    TextField("Entrez le code ou nom (ex: 5*1001)...", text: $searchQuery, onCommit: handleSearchEnter)
                        .textFieldStyle(PlainTextFieldStyle())
                        .padding(8)
                        .background(Theme.bgInput)
                        .cornerRadius(6)
                }
                .padding(.horizontal, 15)
                .padding(.vertical, 10)
                .background(Theme.bgCard)
                .cornerRadius(8)
                
                // Category tabs
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        Button(action: { selectedCategory = nil }) {
                            Text("Tous les articles 🛍️")
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                                .background(selectedCategory == nil ? Theme.accent : Theme.bgCard)
                                .cornerRadius(5)
                        }
                        .buttonStyle(PlainButtonStyle())
                        
                        let categories = Array(Set(products.map({ $0.category }))).sorted()
                        ForEach(categories, id: \.self) { cat in
                            Button(action: { selectedCategory = cat }) {
                                Text(cat)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(selectedCategory == cat ? Theme.accent : Theme.bgCard)
                                    .cornerRadius(5)
                            }
                            .buttonStyle(PlainButtonStyle())
                        }
                    }
                    .padding(.horizontal, 2)
                }
                
                // Grid scroll
                ScrollView {
                    let filtered = products.filter { prod in
                        (selectedCategory == nil || prod.category == selectedCategory) &&
                        (searchQuery.isEmpty || prod.name.lowercased().contains(searchQuery.lowercased()) || prod.barcode.contains(searchQuery))
                    }
                    
                    LazyVGrid(columns: [GridItem(.adaptive(minimum: 160), spacing: 10)], spacing: 10) {
                        ForEach(filtered) { prod in
                            ProductGridCard(product: prod, addToCart: { qty in
                                addToCart(prod: prod, qty: qty)
                            })
                        }
                    }
                }
            }
            .padding(10)
            
            // Right Cart Column
            VStack(spacing: 0) {
                Text("🛒 Panier d'Achat")
                    .font(.system(size: 14, weight: .bold))
                    .padding(10)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.opacity(0.02))
                
                // Cart Items Table
                ScrollView {
                    VStack(spacing: 5) {
                        if cart.isEmpty {
                            Text("Panier vide")
                                .foregroundColor(Theme.fgMuted)
                                .padding(.top, 50)
                        } else {
                            ForEach(Array(cart.keys).sorted(by: { $0.name < $1.name }), id: \.self) { prod in
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(prod.name)
                                            .font(.system(size: 12, weight: .bold))
                                        Text("\(prod.price, specifier: "%.2f") €")
                                            .foregroundColor(Theme.accent)
                                            .font(.caption)
                                    }
                                    Spacer()
                                    
                                    HStack {
                                        Button(action: { decCart(prod: prod) }) {
                                            Text("➖")
                                        }
                                        .buttonStyle(PlainButtonStyle())
                                        
                                        Text("\(cart[prod, default: 1])")
                                            .font(.system(size: 12, weight: .bold))
                                            .frame(width: 25, alignment: .center)
                                        
                                        Button(action: { incCart(prod: prod) }) {
                                            Text("➕")
                                        }
                                        .buttonStyle(PlainButtonStyle())
                                    }
                                    
                                    Text("\(prod.price * Double(cart[prod, default: 1]), specifier: "%.2f") €")
                                        .frame(width: 65, alignment: .trailing)
                                        .font(.system(size: 12, weight: .bold))
                                }
                                .padding(8)
                                .background(Theme.bgInput)
                                .cornerRadius(6)
                            }
                        }
                    }
                    .padding(10)
                }
                
                // Totals Panel
                VStack(spacing: 8) {
                    let total = cart.reduce(0.0, { $0 + ($1.key.price * Double($1.value)) })
                    let ht = total / 1.20
                    let tva = total - ht
                    
                    HStack {
                        Text("Total HT :")
                        Spacer()
                        Text("\(ht, specifier: "%.2f") €")
                    }
                    .foregroundColor(Theme.fgMuted)
                    
                    HStack {
                        Text("TVA (20%) :")
                        Spacer()
                        Text("\(tva, specifier: "%.2f") €")
                    }
                    .foregroundColor(Theme.fgMuted)
                    
                    HStack {
                        Text("TOTAL :")
                            .font(.system(size: 18, weight: .bold))
                        Spacer()
                        Text("\(total, specifier: "%.2f") €")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(Theme.accent)
                    }
                    .padding(.top, 5)
                    
                    Button(action: { showPaymentModal = true }) {
                        Text("💵 ENCAISSER")
                            .font(.system(size: 14, weight: .bold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(Theme.green)
                            .cornerRadius(6)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .disabled(cart.isEmpty)
                    .padding(.top, 10)
                }
                .padding(15)
                .background(Color.black.opacity(0.2))
                .overlay(Rectangle().stroke(Color.white.opacity(0.05), lineWidth: 1).frame(height: 1), alignment: .top)
            }
            .frame(width: 320)
            .background(Theme.bgCard)
            .cornerRadius(8)
            .padding(10)
        }
        .onAppear(perform: loadProducts)
        .sheet(isPresented: $showPaymentModal) {
            PaymentSheet(
                total: cart.reduce(0.0, { $0 + ($1.key.price * Double($1.value)) }),
                onCancel: { showPaymentModal = false },
                onFinalize: finalizeSale
            )
        }
        .sheet(isPresented: $showTicketPreview) {
            TicketPreviewSheet(content: ticketContent, onClose: { showTicketPreview = false })
        }
    }
    
    func loadProducts() {
        Task {
            do {
                self.products = try await FirebaseManager.shared.fetchProducts()
            } catch {
                print("Error loading products: \(error)")
            }
        }
    }
    
    func addToCart(prod: Product, qty: Int) {
        if prod.stock < qty + cart[prod, default: 0] {
            return // Not enough stock
        }
        cart[prod, default: 0] += qty
    }
    
    func incCart(prod: Product) {
        if prod.stock > cart[prod, default: 0] {
            cart[prod, default: 0] += 1
        }
    }
    
    func decCart(prod: Product) {
        if cart[prod, default: 0] > 1 {
            cart[prod, default: 0] -= 1
        } else {
            cart.removeValue(forKey: prod)
        }
    }
    
    func handleSearchEnter() {
        let input = searchQuery.trimmingCharacters(in: .whitespacesAndNewlines)
        if input.isEmpty { return }
        
        var qty = 1
        var barcode = input
        
        if input.contains("*") {
            let parts = input.components(separatedBy: "*")
            if parts.count == 2 {
                let p1 = parts[0].trimmingCharacters(in: .whitespaces)
                let p2 = parts[1].trimmingCharacters(in: .whitespaces)
                
                if let q = Int(p1), Int(p2) == nil {
                    qty = q
                    barcode = p2
                } else if let q = Int(p2), Int(p1) == nil {
                    qty = q
                    barcode = p1
                } else if let q1 = Int(p1), let q2 = Int(p2) {
                    if p1.count < p2.count {
                        qty = q1
                        barcode = p2
                    } else {
                        qty = q2
                        barcode = p1
                    }
                }
            }
        }
        
        if let found = products.first(where: { $0.barcode == barcode || $0.name.lowercased().contains(barcode.lowercased()) }) {
            addToCart(prod: found, qty: qty)
            searchQuery = ""
        }
    }
    
    func finalizeSale(method: String, received: Double, change: Double) {
        showPaymentModal = false
        
        let total = cart.reduce(0.0, { $0 + ($1.key.price * Double($1.value)) })
        
        let sale = Sale(
            id: 0,
            sale_date: "",
            cashier_id: user.id,
            cashier_name: user.username,
            total: total,
            payment_method: method,
            amount_received: received,
            change_returned: change,
            items: nil
        )
        
        Task {
            do {
                let saleId = try await FirebaseManager.shared.recordSale(sale: sale, cartItems: cart)
                
                // Generate ticket preview text
                generateTicketText(saleId: saleId, method: method, received: received, change: change)
                showTicketPreview = true
                
                // Clear cart and reload
                cart.removeAll()
                loadProducts()
            } catch {
                print("Error recording sale: \(error)")
            }
        }
    }
    
    func generateTicketText(saleId: Int, method: String, received: Double, change: Double) {
        let total = cart.reduce(0.0, { $0 + ($1.key.price * Double($1.value)) })
        let ht = total / 1.20
        let tva = total - ht
        
        let formatter = DateFormatter()
        formatter.dateFormat = "dd/MM/yyyy HH:mm:ss"
        let dateStr = formatter.string(from: Date())
        
        var txt = "========================================\n"
        txt += "               MIAOU SHOP 🐾            \n"
        txt += "      Des articles fun pour vous !      \n"
        txt += "========================================\n"
        txt += String(format: " Ticket N° : %06d\n", saleId)
        txt += " Date      : \(dateStr)\n"
        txt += " Caissier  : \(user.username)\n"
        txt += "----------------------------------------\n"
        txt += " Nom Produit               P.U    Total \n"
        txt += "----------------------------------------\n"
        
        for (prod, qty) in cart {
            let truncName = String(prod.name.prefix(18)).padding(toLength: 18, withPad: " ", startingAt: 0)
            for _ in 0..<qty {
                txt += String(format: " %@      %6.2f  %6.2f€\n", truncName, prod.price, prod.price)
            }
        }
        
        txt += "----------------------------------------\n"
        txt += String(format: " TOTAL TTC :                 %7.2f €\n", total)
        txt += String(format: "   Dont HT :                 %7.2f €\n", ht)
        txt += String(format: "   TVA 20% :                 %7.2f €\n", tva)
        txt += "----------------------------------------\n"
        txt += " Mode Paiement : \(method)\n"
        if method == "Espèces" {
            txt += String(format: " Recu          :             %7.2f €\n", received)
            txt += String(format: " Rendu         :             %7.2f €\n", change)
        }
        txt += "========================================\n"
        txt += "   Merci de votre visite ! Miaou 🐱   \n"
        txt += "========================================\n"
        
        self.ticketContent = txt
    }
}

// MARK: - PRODUCT GRID CARD
struct ProductGridCard: View {
    let product: Product
    let addToCart: (Int) -> Void
    @State private var qtyString = "1"
    
    var body: some View {
        VStack(spacing: 8) {
            Text(product.name)
                .font(.system(size: 12, weight: .bold))
                .lineLimit(2)
                .multilineTextAlignment(.center)
                .frame(height: 35)
            
            Text("\(product.price, specifier: "%.2f") €")
                .foregroundColor(Theme.accent)
                .font(.system(size: 14, weight: .bold))
            
            let stockColor = product.stock > 10 ? Theme.green : (product.stock > 0 ? Theme.amber : Theme.red)
            Text("Stock : \(product.stock)")
                .font(.caption)
                .foregroundColor(stockColor)
            
            if product.stock > 0 {
                HStack(spacing: 4) {
                    TextField("", text: $qtyString)
                        .textFieldStyle(PlainTextFieldStyle())
                        .frame(width: 30)
                        .multilineTextAlignment(.center)
                        .padding(.vertical, 4)
                        .background(Theme.bgInput)
                        .cornerRadius(4)
                    
                    Button(action: {
                        if let q = Int(qtyString), q > 0 {
                            addToCart(q)
                        }
                    }) {
                        Text("🛒 Ajouter")
                            .font(.system(size: 11, weight: .bold))
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 4)
                            .background(Color.white.opacity(0.1))
                            .cornerRadius(4)
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            } else {
                Text("Rupture")
                    .foregroundColor(Theme.fgMuted)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 4)
                    .background(Color.black.opacity(0.1))
                    .cornerRadius(4)
            }
        }
        .padding(10)
        .background(Theme.bgCard)
        .cornerRadius(8)
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.white.opacity(0.05), lineWidth: 1))
    }
}

// MARK: - PAYMENT SHEET
struct PaymentSheet: View {
    let total: Double
    var onCancel: () -> Void
    var onFinalize: (String, Double, Double) -> Void
    
    @State private var method = "Carte"
    @State private var amountReceivedStr = ""
    @State private var changeReturned = 0.0
    
    var body: some View {
        VStack(spacing: 20) {
            Text("💰 ENCAISSEMENT CLIENT")
                .font(.system(size: 16, weight: .bold))
                .foregroundColor(Theme.accent)
            
            VStack {
                Text("Montant à payer :")
                    .foregroundColor(Theme.fgMuted)
                Text("\(total, specifier: "%.2f") €")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(Theme.green)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(Color.black.opacity(0.2))
            .cornerRadius(8)
            
            Picker("", selection: $method) {
                Text("💳 Carte").tag("Carte")
                Text("💵 Espèces").tag("Espèces")
                Text("✍️ Chèque").tag("Chèque")
            }
            .pickerStyle(SegmentedPickerStyle())
            
            if method == "Espèces" {
                VStack(spacing: 10) {
                    HStack {
                        Text("Montant reçu client (€) :")
                        TextField("", text: $amountReceivedStr)
                            .textFieldStyle(PlainTextFieldStyle())
                            .padding(8)
                            .background(Theme.bgInput)
                            .cornerRadius(5)
                            .frame(width: 100)
                            .onChange(of: amountReceivedStr) { _ in calcChange() }
                    }
                    
                    let isShort = (Double(amountReceivedStr.replacingOccurrences(of: ",", with: ".")) ?? 0.0) < total
                    HStack {
                        Text(isShort ? "Manque :" : "Rendu :")
                        Spacer()
                        Text("\(abs(changeReturned), specifier: "%.2f") €")
                            .font(.headline)
                            .foregroundColor(isShort ? Theme.red : Theme.green)
                    }
                }
                .padding()
                .background(Theme.bgCard)
                .cornerRadius(8)
            }
            
            HStack(spacing: 15) {
                Button("Annuler", action: onCancel)
                    .buttonStyle(BorderedButtonStyle())
                
                Button(action: confirmPayment) {
                    Text("Valider la Vente")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 20)
                        .padding(.vertical, 8)
                        .background(Theme.green)
                        .cornerRadius(6)
                }
                .buttonStyle(PlainButtonStyle())
                .disabled(method == "Espèces" && (Double(amountReceivedStr.replacingOccurrences(of: ",", with: ".")) ?? 0.0) < total)
            }
        }
        .padding(30)
        .frame(width: 400)
        .background(Theme.bgCard)
    }
    
    func calcChange() {
        if let rec = Double(amountReceivedStr.replacingOccurrences(of: ",", with: ".")) {
            changeReturned = rec - total
        } else {
            changeReturned = -total
        }
    }
    
    func confirmPayment() {
        let rec = method == "Espèces" ? (Double(amountReceivedStr.replacingOccurrences(of: ",", with: ".")) ?? total) : total
        let chg = method == "Espèces" ? max(0.0, rec - total) : 0.0
        onFinalize(method, rec, chg)
    }
}

// MARK: - TICKET PREVIEW SHEET
struct TicketPreviewSheet: View {
    let content: String
    var onClose: () -> Void
    
    var body: some View {
        VStack(spacing: 15) {
            Text("📜 Aperçu du Ticket de Caisse")
                .font(.headline)
            
            ScrollView {
                Text(content)
                    .font(.system(.body, design: .monospaced))
                    .padding()
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white)
                    .foregroundColor(.black)
            }
            .frame(height: 400)
            .cornerRadius(6)
            
            Button("Fermer", action: onClose)
                .buttonStyle(KeyEquivalentButtonStyle(key: .escape))
                .padding(.vertical, 8)
                .padding(.horizontal, 25)
                .background(Theme.accent)
                .foregroundColor(.white)
                .cornerRadius(6)
        }
        .padding()
        .frame(width: 380)
        .background(Theme.bgCard)
    }
}

// Custom Helper Button modifier for ESC key support in SwiftUI
struct KeyEquivalentButtonStyle: ButtonStyle {
    let key: KeyEquivalent
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .keyboardShortcut(key)
    }
}

// MARK: - ADMIN VIEW
struct AdminView: View {
    @State private var section = "stats"
    
    var body: some View {
        HStack(spacing: 0) {
            // Sidebar
            VStack(spacing: 8) {
                Text("MENU GENERAL")
                    .font(.caption)
                    .foregroundColor(Theme.fgMuted)
                    .padding(.top, 15)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                AdminSidebarButton(title: "📊 Tableau de bord", isSelected: section == "stats", action: { section = "stats" })
                AdminSidebarButton(title: "📦 Catalogue", isSelected: section == "catalog", action: { section = "catalog" })
                AdminSidebarButton(title: "👥 Utilisateurs", isSelected: section == "users", action: { section = "users" })
                AdminSidebarButton(title: "📜 Ventes / Tickets", isSelected: section == "history", action: { section = "history" })
                
                Spacer()
            }
            .padding(.horizontal, 12)
            .frame(width: 180)
            .background(Theme.bgCard)
            
            // Content
            ZStack {
                Theme.bgMain.ignoresSafeArea()
                
                if section == "stats" {
                    AdminStatsView()
                } else if section == "catalog" {
                    AdminCatalogView()
                } else if section == "users" {
                    AdminUsersView()
                } else if section == "history" {
                    AdminHistoryView()
                }
            }
        }
    }
}

struct AdminSidebarButton: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 12)
                .padding(.vertical, 8)
                .background(isSelected ? Theme.accent : Color.clear)
                .cornerRadius(6)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - ADMIN SUBVIEWS (Placeholder / Simple implementations of views)
struct AdminStatsView: View {
    @State private var stats = DashboardStats()
    @State private var lowStock: [Product] = []
    
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("📊 TABLEAU DE BORD")
                    .font(.title2)
                    .bold()
                
                HStack(spacing: 15) {
                    StatCard(title: "CA Global", value: String(format: "%.2f €", stats.totalRevenue), color: Theme.green)
                    StatCard(title: "CA Aujourd'hui", value: String(format: "%.2f €", stats.todayRevenue), color: Theme.accent)
                    StatCard(title: "Tickets Emis", value: "\(stats.totalSalesCount)", color: Theme.amber)
                }
                
                Text("⚠️ ALERTES DE STOCK")
                    .font(.headline)
                    .padding(.top, 10)
                
                if lowStock.isEmpty {
                    Text("✅ Tout est en ordre, aucun produit en rupture de stock !")
                        .foregroundColor(Theme.green)
                        .padding()
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Theme.green.opacity(0.1))
                        .cornerRadius(6)
                } else {
                    VStack(alignment: .leading) {
                        ForEach(lowStock) { prod in
                            HStack {
                                Text(prod.name)
                                Spacer()
                                Text("Stock : \(prod.stock)")
                                    .bold()
                                    .foregroundColor(Theme.red)
                            }
                            .padding(.vertical, 5)
                            Divider()
                        }
                    }
                    .padding()
                    .background(Theme.bgCard)
                    .cornerRadius(8)
                }
            }
            .padding(20)
        }
        .onAppear(perform: loadStats)
    }
    
    func loadStats() {
        Task {
            do {
                let sales = try await FirebaseManager.shared.fetchSales()
                let products = try await FirebaseManager.shared.fetchProducts()
                self.stats = FirebaseManager.shared.getDashboardStats(sales: sales, products: products)
                self.lowStock = products.filter({ $0.stock < 5 })
            } catch {}
        }
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text(title)
                .font(.caption)
                .foregroundColor(Theme.fgMuted)
            Text(value)
                .font(.title)
                .bold()
                .foregroundColor(color)
        }
        .padding()
        .frame(maxWidth: .infinity)
        .background(Theme.bgCard)
        .cornerRadius(8)
        .overlay(RoundedRectangle(cornerRadius: 8).stroke(Color.white.opacity(0.05), lineWidth: 1))
    }
}

// MARK: - ADMIN CATALOG VIEW
struct AdminCatalogView: View {
    @State private var products: [Product] = []
    @State private var selectedProduct: Product? = nil
    
    @State private var barcode = ""
    @State private var name = ""
    @State private var priceStr = ""
    @State private var category = ""
    @State private var stockStr = ""
    
    var body: some View {
        HStack(spacing: 15) {
            // Table
            VStack {
                Text("📦 Catalogue de Produits")
                    .font(.headline)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                List(products, selection: $selectedProduct) { prod in
                    HStack {
                        Text(prod.barcode)
                            .frame(width: 80, alignment: .leading)
                        Text(prod.name)
                        Spacer()
                        Text("\(prod.price, specifier: "%.2f") €")
                            .frame(width: 80, alignment: .trailing)
                        Text("Stock : \(prod.stock)")
                            .foregroundColor(prod.stock < 5 ? Theme.red : Theme.fgMuted)
                            .frame(width: 80, alignment: .trailing)
                    }
                    .tag(prod)
                }
                .cornerRadius(6)
            }
            .padding(15)
            
            // Form
            VStack(alignment: .leading, spacing: 10) {
                Text("📝 FORMULAIRE PRODUIT")
                    .font(.headline)
                    .foregroundColor(Theme.accent)
                
                FormGroup(label: "Code-barres :", val: $barcode)
                FormGroup(label: "Nom de l'article :", val: $name)
                FormGroup(label: "Prix (€) :", val: $priceStr)
                FormGroup(label: "Catégorie :", val: $category)
                FormGroup(label: "Stock :", val: $stockStr)
                
                VStack(spacing: 8) {
                    Button(action: saveProduct) {
                        Text("💾 Enregistrer / Modifier")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.accent)
                            .foregroundColor(.white)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    Button(action: { clearForm(); selectedProduct = nil }) {
                        Text("🧹 Vider formulaire")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.bgInput)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    Button(action: deleteProduct) {
                        Text("🗑️ Supprimer")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.red)
                            .foregroundColor(.white)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .disabled(selectedProduct == nil)
                }
                .padding(.top, 15)
                
                Spacer()
            }
            .frame(width: 250)
            .padding(15)
            .background(Theme.bgCard)
        }
        .onAppear(perform: loadProducts)
        .onChange(of: selectedProduct) { newVal in
            if let prod = newVal {
                barcode = prod.barcode
                name = prod.name
                priceStr = String(format: "%.2f", prod.price)
                category = prod.category
                stockStr = "\(prod.stock)"
            }
        }
    }
    
    func loadProducts() {
        Task {
            do {
                products = try await FirebaseManager.shared.fetchProducts()
            } catch {}
        }
    }
    
    func clearForm() {
        barcode = ""
        name = ""
        priceStr = ""
        category = ""
        stockStr = ""
    }
    
    func saveProduct() {
        guard let price = Double(priceStr.replacingOccurrences(of: ",", with: ".")),
              let stock = Int(stockStr),
              !barcode.isEmpty, !name.isEmpty else { return }
              
        let prod = Product(id: Int(barcode) ?? Int.random(in: 10000...99999), barcode: barcode, name: name, price: price, category: category, stock: stock)
        
        Task {
            do {
                try await FirebaseManager.shared.saveProduct(prod)
                clearForm()
                loadProducts()
            } catch {}
        }
    }
    
    func deleteProduct() {
        guard let prod = selectedProduct else { return }
        Task {
            do {
                try await FirebaseManager.shared.deleteProduct(barcode: prod.barcode)
                clearForm()
                selectedProduct = nil
                loadProducts()
            } catch {}
        }
    }
}

// MARK: - ADMIN USERS VIEW
struct AdminUsersView: View {
    @State private var users: [User] = []
    @State private var selectedUser: User? = nil
    
    @State private var username = ""
    @State private var password = ""
    @State private var role = "Caissier"
    
    var body: some View {
        HStack(spacing: 15) {
            // Table
            VStack {
                Text("👥 Gestion des Utilisateurs")
                    .font(.headline)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                List(users, selection: $selectedUser) { u in
                    HStack {
                        Text("\(u.id)")
                            .frame(width: 40, alignment: .leading)
                        Text(u.username)
                        Spacer()
                        Text(u.role)
                            .foregroundColor(Theme.accent)
                    }
                    .tag(u)
                }
                .cornerRadius(6)
            }
            .padding(15)
            
            // Form
            VStack(alignment: .leading, spacing: 10) {
                Text("📝 FICHE UTILISATEUR")
                    .font(.headline)
                    .foregroundColor(Theme.accent)
                
                FormGroup(label: "Pseudo :", val: $username)
                FormGroup(label: "Mot de passe :", val: $password)
                
                VStack(alignment: .leading, spacing: 5) {
                    Text("Rôle :")
                        .font(.caption)
                    Picker("", selection: $role) {
                        Text("Caissier").tag("Caissier")
                        Text("Admin").tag("Admin")
                    }
                    .pickerStyle(PopUpButtonPickerStyle())
                }
                
                VStack(spacing: 8) {
                    Button(action: saveUser) {
                        Text("💾 Enregistrer")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.accent)
                            .foregroundColor(.white)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    Button(action: { clearForm(); selectedUser = nil }) {
                        Text("🧹 Vider")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.bgInput)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    Button(action: deleteUser) {
                        Text("🗑️ Supprimer")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 6)
                            .background(Theme.red)
                            .foregroundColor(.white)
                            .cornerRadius(5)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .disabled(selectedUser == nil)
                }
                .padding(.top, 15)
                
                Spacer()
            }
            .frame(width: 250)
            .padding(15)
            .background(Theme.bgCard)
        }
        .onAppear(perform: loadUsers)
        .onChange(of: selectedUser) { newVal in
            if let u = newVal {
                username = u.username
                password = u.password
                role = u.role
            }
        }
    }
    
    func loadUsers() {
        Task {
            do {
                users = try await FirebaseManager.shared.fetchUsers()
            } catch {}
        }
    }
    
    func clearForm() {
        username = ""
        password = ""
        role = "Caissier"
    }
    
    func saveUser() {
        guard !username.isEmpty, !password.isEmpty else { return }
        
        Task {
            do {
                let currentCounter = try await FirebaseManager.shared.fetchUsersCounter()
                let nextId = selectedUser?.id ?? (currentCounter + 1)
                
                let u = User(id: nextId, username: username, password: password, role: role)
                try await FirebaseManager.shared.saveUser(u)
                
                if selectedUser == nil {
                    try await FirebaseManager.shared.saveUsersCounter(nextId)
                }
                
                clearForm()
                loadUsers()
            } catch {}
        }
    }
    
    func deleteUser() {
        guard let u = selectedUser else { return }
        Task {
            do {
                try await FirebaseManager.shared.deleteUser(id: u.id)
                clearForm()
                selectedUser = nil
                loadUsers()
            } catch {}
        }
    }
}

// MARK: - ADMIN HISTORY VIEW
struct AdminHistoryView: View {
    @State private var sales: [Sale] = []
    @State private var selectedSale: Sale? = nil
    @State private var ticketPreviewText = "Sélectionnez une vente pour afficher son ticket."
    
    var body: some View {
        HStack(spacing: 15) {
            // Table
            VStack {
                Text("📜 Historique des Tickets émis")
                    .font(.headline)
                    .frame(maxWidth: .infinity, alignment: .leading)
                
                List(sales, selection: $selectedSale) { sale in
                    HStack {
                        Text(String(format: "%06d", sale.id))
                            .frame(width: 60, alignment: .leading)
                        Text(sale.sale_date)
                        Spacer()
                        Text(sale.cashier_name)
                        Text("\(sale.total, specifier: "%.2f") €")
                            .frame(width: 80, alignment: .trailing)
                            .bold()
                            .foregroundColor(Theme.accent)
                    }
                    .tag(sale)
                }
                .cornerRadius(6)
            }
            .padding(15)
            
            // Detail Ticket Preview
            VStack(alignment: .leading) {
                Text("📜 DETAIL DU TICKET")
                    .font(.headline)
                    .foregroundColor(Theme.accent)
                
                ScrollView {
                    Text(ticketPreviewText)
                        .font(.system(.body, design: .monospaced))
                        .padding(10)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(Color.white)
                        .foregroundColor(.black)
                }
                .cornerRadius(6)
            }
            .frame(width: 320)
            .padding(15)
            .background(Theme.bgCard)
        }
        .onAppear(perform: loadSales)
        .onChange(of: selectedSale) { newVal in
            if let sale = newVal {
                buildTicketPreview(sale: sale)
            } else {
                ticketPreviewText = "Sélectionnez une vente pour afficher son ticket."
            }
        }
    }
    
    func loadSales() {
        Task {
            do {
                sales = try await FirebaseManager.shared.fetchSales()
            } catch {}
        }
    }
    
    func buildTicketPreview(sale: Sale) {
        let total = sale.total
        let ht = total / 1.20
        let tva = total - ht
        
        var txt = "========================================\n"
        txt += "               MIAOU SHOP 🐾            \n"
        txt += "========================================\n"
        txt += String(format: " Ticket N° : %06d\n", sale.id)
        txt += " Date      : \(sale.sale_date)\n"
        txt += " Caissier  : \(sale.cashier_name)\n"
        txt += "----------------------------------------\n"
        txt += " Nom Produit               P.U    Total \n"
        txt += "----------------------------------------\n"
        
        if let items = sale.items {
            for item in items {
                let truncName = String(item.name.prefix(18)).padding(toLength: 18, withPad: " ", startingAt: 0)
                for _ in 0..<item.quantity {
                    txt += String(format: " %@      %6.2f  %6.2f€\n", truncName, item.price, item.price)
                }
            }
        }
        
        txt += "----------------------------------------\n"
        txt += String(format: " TOTAL TTC :                 %7.2f €\n", total)
        txt += String(format: "   Dont HT :                 %7.2f €\n", ht)
        txt += String(format: "   TVA 20% :                 %7.2f €\n", tva)
        txt += "----------------------------------------\n"
        txt += " Mode Paiement : \(sale.payment_method)\n"
        if sale.payment_method == "Espèces" {
            txt += String(format: " Recu          :             %7.2f €\n", sale.amount_received)
            txt += String(format: " Rendu         :             %7.2f €\n", sale.change_returned)
        }
        txt += "========================================\n"
        txt += "       Historique Archivé / Miaou 🐱    \n"
        txt += "========================================\n"
        
        self.ticketPreviewText = txt
    }
}

// MARK: - FORM GROUP HELPER
struct FormGroup: View {
    let label: String
    @Binding var val: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(label)
                .font(.caption)
            TextField("", text: $val)
                .textFieldStyle(PlainTextFieldStyle())
                .padding(6)
                .background(Theme.bgInput)
                .cornerRadius(4)
        }
    }
}
