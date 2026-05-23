# -*- coding: utf-8 -*-
"""
Caisse Enregistreuse Moderne 🐾
Développé pour Miaou 🐱 - Projet complet avec GUI Tkinter et SQLite.
"""

import os
import urllib.request
import urllib.parse
import json
import datetime
from tkinter import messagebox, ttk
import tkinter as tk

# Configuration des couleurs - Thème Dark Premium 🎨
BG_MAIN = "#121214"       # Fond principal ultra-sombre
BG_CARD = "#1c1c21"       # Fond des cartes/panneaux
BG_INPUT = "#282830"      # Fond des champs de saisie
FG_TEXT = "#f1f1f4"       # Texte principal blanc-gris
FG_MUTED = "#8c8c9a"      # Texte secondaire estompé
ACCENT = "#00adb5"        # Bleu/Cyan électrique
ACCENT_HOVER = "#00c2cb"  # Bleu/Cyan survolé
GREEN = "#2ecc71"         # Vert succès (Paiement)
GREEN_HOVER = "#27ae60"
RED = "#e74c3c"           # Rouge alerte (Suppression/Annulation)
RED_HOVER = "#c0392b"
AMBER = "#f39c12"         # Orange/Ambre
AMBER_HOVER = "#d35400"

FONT_FAMILY = "Segoe UI"

# =====================================================================
# CONFIGURATION FIREBASE & BASE DE DONNÉES CLOUD ☁️
# =====================================================================
FIREBASE_URL = "https://test2-mdr-default-rtdb.europe-west1.firebasedatabase.app/"

class CaisseDB:
    def __init__(self, db_url=FIREBASE_URL):
        self.db_url = db_url.rstrip('/') + '/'
        import ssl
        self.ssl_context = ssl._create_unverified_context()
        # Tester la connexion et initialiser
        try:
            self.seed_data()
        except Exception as e:
            import tkinter.messagebox as mb
            mb.showwarning(
                "Connexion Firebase ⚠️",
                f"Impossible de se connecter à Firebase Realtime Database.\n\n"
                f"Détail de l'erreur : {e}\n\n"
                f"L'application risque de ne pas fonctionner correctement.\n"
                f"Vérifie que les règles de ta base de données Firebase sont bien sur '.read': true et '.write': true, et que ta connexion Internet fonctionne !"
            )

    def _request(self, path, method="GET", data=None):
        url = f"{self.db_url}{path}.json"
        req = urllib.request.Request(url, method=method)
        req.add_header('Content-Type', 'application/json')
        
        encoded_data = None
        if data is not None:
            encoded_data = json.dumps(data).encode('utf-8')
            
        try:
            with urllib.request.urlopen(req, data=encoded_data, timeout=5, context=self.ssl_context) as response:
                res_content = response.read().decode('utf-8')
                if not res_content or res_content == "null":
                    return None
                return json.loads(res_content)
        except Exception as e:
            print(f"Erreur HTTP Firebase ({method} {path}) : {e}")
            raise e

    def seed_data(self):
        # Vérifier si la table des utilisateurs existe
        users = self._request("users")
        if users is None:
            # Créer les utilisateurs par défaut
            default_users = {
                "1": {"id": 1, "username": "admin", "password": "admin123", "role": "Admin"},
                "2": {"id": 2, "username": "caissier", "password": "caissier123", "role": "Caissier"}
            }
            self._request("users", method="PUT", data=default_users)
            self._request("users_counter", method="PUT", data=2)
            
        # Produits par défaut
        products = self._request("products")
        if products is None:
            default_products = {
                # Roblox 🎮
                "1001": {"id": 1001, "barcode": "1001", "name": "1000 Robux 🎮", "price": 12.50, "category": "Roblox", "stock": 100},
                "1002": {"id": 1002, "barcode": "1002", "name": "Chat Géant Pet Sim 🐱", "price": 49.99, "category": "Roblox", "stock": 15},
                "1003": {"id": 1003, "barcode": "1003", "name": "Carte Cadeau Roblox 20€ 💳", "price": 20.00, "category": "Roblox", "stock": 50},
                # Chats 🐱
                "2001": {"id": 2001, "barcode": "2001", "name": "Croquettes Premium Chat 🐱", "price": 18.90, "category": "Chats", "stock": 40},
                "2002": {"id": 2002, "barcode": "2002", "name": "Souris Laser Amusante 🐭", "price": 5.50, "category": "Chats", "stock": 150},
                "2003": {"id": 2003, "barcode": "2003", "name": "Herbe à chat Bio 🌱", "price": 3.20, "category": "Chats", "stock": 60},
                # Tramway 🚊
                "3001": {"id": 3001, "barcode": "3001", "name": "Ticket Tram Unitaire 🎫", "price": 1.70, "category": "Tramway", "stock": 1000},
                "3002": {"id": 3002, "barcode": "3002", "name": "Abonnement Mensuel Tram 🎫", "price": 45.00, "category": "Tramway", "stock": 200},
                # Tesla ⚡
                "4001": {"id": 4001, "barcode": "4001", "name": "Miniature Tesla Model 3 🚗", "price": 35.00, "category": "Tesla", "stock": 20},
                "4002": {"id": 4002, "barcode": "4002", "name": "Chargeur Mural Tesla 🔌", "price": 499.00, "category": "Tesla", "stock": 8},
                # Boissons 🥤
                "5001": {"id": 5001, "barcode": "5001", "name": "Canette de Soda Frais 🥤", "price": 1.50, "category": "Boissons", "stock": 300},
                "5002": {"id": 5002, "barcode": "5002", "name": "Eau Minérale 50cl 💧", "price": 1.00, "category": "Boissons", "stock": 500}
            }
            self._request("products", method="PUT", data=default_products)

    # Opérations Utilisateurs
    def get_user(self, username, password):
        users = self._request("users")
        if not users:
            return None
        for u in users.values():
            if u and u.get('username') == username and u.get('password') == password:
                return u
        return None

    def get_all_users(self):
        users = self._request("users")
        if not users:
            return []
        user_list = [u for u in users.values() if u]
        return sorted(user_list, key=lambda x: x.get('username', ''))

    def add_user(self, username, password, role):
        users = self._request("users")
        if users:
            for u in users.values():
                if u and u.get('username') == username:
                    return False
                    
        counter = self._request("users_counter")
        if counter is None:
            counter = 1
        else:
            counter += 1
            
        new_user = {
            "id": counter,
            "username": username,
            "password": password,
            "role": role
        }
        self._request(f"users/{counter}", method="PUT", data=new_user)
        self._request("users_counter", method="PUT", data=counter)
        return True

    def update_user(self, user_id, username, password, role):
        users = self._request("users")
        if users:
            for uid, u in users.items():
                if u and u.get('username') == username and int(uid) != int(user_id):
                    return False
                    
        updated_user = {
            "id": int(user_id),
            "username": username,
            "password": password,
            "role": role
        }
        self._request(f"users/{user_id}", method="PUT", data=updated_user)
        return True

    def delete_user(self, user_id):
        self._request(f"users/{user_id}", method="DELETE")

    # Opérations Produits
    def get_all_products(self):
        products = self._request("products")
        if not products:
            return []
        prod_list = [p for p in products.values() if p]
        return sorted(prod_list, key=lambda x: x.get('name', ''))

    def get_products_by_category(self, category):
        products = self.get_all_products()
        return [p for p in products if p.get('category') == category]

    def get_categories(self):
        products = self.get_all_products()
        categories = set(p.get('category') for p in products if p.get('category'))
        return sorted(list(categories))

    def get_product_by_barcode(self, barcode):
        return self._request(f"products/{barcode}")

    def add_product(self, barcode, name, price, category, stock):
        existing = self._request(f"products/{barcode}")
        if existing:
            return False
            
        new_prod = {
            "id": int(barcode) if barcode.isdigit() else barcode,
            "barcode": barcode,
            "name": name,
            "price": price,
            "category": category,
            "stock": stock
        }
        self._request(f"products/{barcode}", method="PUT", data=new_prod)
        return True

    def update_product(self, prod_id, barcode, name, price, category, stock):
        if str(prod_id) != str(barcode):
            existing = self._request(f"products/{barcode}")
            if existing:
                return False
            self._request(f"products/{prod_id}", method="DELETE")
            
        updated_prod = {
            "id": int(barcode) if barcode.isdigit() else barcode,
            "barcode": barcode,
            "name": name,
            "price": price,
            "category": category,
            "stock": stock
        }
        self._request(f"products/{barcode}", method="PUT", data=updated_prod)
        return True

    def delete_product(self, prod_id):
        self._request(f"products/{prod_id}", method="DELETE")

    def update_stock(self, product_id, quantity_change):
        prod = self._request(f"products/{product_id}")
        if prod:
            new_stock = max(0, prod.get('stock', 0) + quantity_change)
            self._request(f"products/{product_id}", method="PATCH", data={"stock": new_stock})

    # Opérations Ventes
    def record_sale(self, cashier_id, total, payment_method, amount_received, change_returned, cart_items):
        try:
            sale_id = self._request("sales_counter")
            if sale_id is None:
                sale_id = 1
            else:
                sale_id += 1
                
            cashier_name = "Inconnu"
            users = self._request("users")
            if users:
                user = users.get(str(cashier_id))
                if user:
                    cashier_name = user.get('username', 'Inconnu')
                    
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            items_details = []
            for item in cart_items:
                prod_id, qty, price = item
                prod = self._request(f"products/{prod_id}")
                prod_name = prod.get('name', 'Produit Inconnu') if prod else 'Produit Inconnu'
                
                items_details.append({
                    "name": prod_name,
                    "quantity": int(qty),
                    "price": float(price)
                })
                
                if prod:
                    new_stock = max(0, prod.get('stock', 0) - int(qty))
                    self._request(f"products/{prod_id}", method="PATCH", data={"stock": new_stock})
            
            sale_record = {
                "id": sale_id,
                "sale_date": now_str,
                "cashier_id": int(cashier_id),
                "cashier_name": cashier_name,
                "total": float(total),
                "payment_method": payment_method,
                "amount_received": float(amount_received) if amount_received is not None else 0.0,
                "change_returned": float(change_returned) if change_returned is not None else 0.0,
                "items": items_details
            }
            
            self._request(f"sales/{sale_id}", method="PUT", data=sale_record)
            self._request("sales_counter", method="PUT", data=sale_id)
            return sale_id
        except Exception as e:
            print(f"Erreur d'enregistrement de la vente : {e}")
            raise e

    def get_sales_history(self):
        sales = self._request("sales")
        if not sales:
            return []
        sales_list = [s for s in sales.values() if s]
        return sorted(sales_list, key=lambda x: x.get('sale_date', ''), reverse=True)

    def get_sale_details(self, sale_id):
        sale = self._request(f"sales/{sale_id}")
        if not sale:
            return None, []
        items = sale.get('items', [])
        return sale, items

    def get_dashboard_stats(self):
        stats = {
            'total_revenue': 0.0,
            'total_sales_count': 0,
            'total_products': 0,
            'low_stock_count': 0,
            'today_revenue': 0.0
        }
        
        sales = self._request("sales")
        products = self._request("products")
        
        if sales:
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            for s in sales.values():
                if s:
                    total = float(s.get('total', 0.0))
                    stats['total_revenue'] += total
                    stats['total_sales_count'] += 1
                    
                    sale_date = s.get('sale_date', '')
                    if sale_date.startswith(today_str):
                        stats['today_revenue'] += total
                        
        if products:
            for p in products.values():
                if p:
                    stats['total_products'] += 1
                    if int(p.get('stock', 0)) < 5:
                        stats['low_stock_count'] += 1
                        
        return stats

    def close(self):
        pass


# =====================================================================
# WIDGETS PERSONNALISÉS POUR L'ESTHÉTIQUE PREMIUM 🎨
# =====================================================================
class HoverButton(tk.Button):
    """Bouton Tkinter avec effet de survol dynamique et style plat moderne."""
    def __init__(self, master, bg_color=ACCENT, hover_color=ACCENT_HOVER, fg_color=FG_TEXT, *args, **kwargs):
        btn_font = kwargs.pop("font", (FONT_FAMILY, 10, "bold"))
        super().__init__(
            master, 
            bg=bg_color, 
            fg=fg_color, 
            activebackground=hover_color, 
            activeforeground=fg_color, 
            relief="flat", 
            bd=0, 
            cursor="hand2", 
            font=btn_font,
            *args, 
            **kwargs
        )
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self["bg"] = self.hover_color

    def on_leave(self, e):
        self["bg"] = self.bg_color

    def set_bg_color(self, color):
        self.bg_color = color
        self["bg"] = color


class CardFrame(tk.Frame):
    """Panneau de contenu avec fond surélevé et bordures fines."""
    def __init__(self, master, *args, **kwargs):
        super().__init__(
            master, 
            bg=BG_CARD, 
            highlightbackground="#2c2c35", 
            highlightthickness=1, 
            *args, 
            **kwargs
        )


# =====================================================================
# APPLICATION PRINCIPALE 🐾
# =====================================================================
class CaisseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Miaou POS 🐾 - Caisse Enregistreuse")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        self.configure(bg=BG_MAIN)
        
        # Initialisation Base de Données
        self.db = CaisseDB()
        
        # Session utilisateur
        self.current_user = None
        self.locked_users = set()  # Ensemble des utilisateurs bloqués
        
        # Style pour les éléments TTK (Treeview, Scrollbar, Notebook)
        self.setup_ttk_styles()
        
        # Conteneur principal de frames (SPA pattern)
        self.container = tk.Frame(self, bg=BG_MAIN)
        self.container.pack(fill="both", expand=True)
        
        # Initialisation des écrans
        self.frames = {}
        self.show_login_screen()

    def setup_ttk_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Style global Treeview (Tableaux)
        style.configure(
            "Treeview", 
            background=BG_CARD, 
            foreground=FG_TEXT, 
            fieldbackground=BG_CARD, 
            rowheight=30,
            font=(FONT_FAMILY, 10),
            borderwidth=0
        )
        style.configure(
            "Treeview.Heading", 
            background="#282830", 
            foreground=FG_TEXT, 
            font=(FONT_FAMILY, 10, "bold"),
            borderwidth=0,
            relief="flat"
        )
        style.map("Treeview", background=[("selected", ACCENT)], foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading", background=[("active", ACCENT)])
        
        # Scrollbar moderne
        style.configure(
            "Vertical.TScrollbar", 
            gripcount=0, 
            background="#2c2c35", 
            darkcolor="#121214", 
            lightcolor="#2c2c35", 
            troughcolor=BG_MAIN, 
            bordercolor=BG_MAIN, 
            arrowsize=12
        )

    def show_frame(self, frame_class):
        # Détruire l'ancienne frame si elle existe
        for f in self.container.winfo_children():
            f.destroy()
        
        # Créer et afficher la nouvelle frame
        frame = frame_class(self.container, self)
        frame.pack(fill="both", expand=True)

    def show_login_screen(self):
        self.current_user = None
        self.show_frame(LoginFrame)

    def show_sales_screen(self):
        self.show_frame(SalesFrame)

    def show_admin_screen(self):
        self.show_frame(AdminFrame)

    def on_closing(self):
        self.db.close()
        self.destroy()


# =====================================================================
# ÉCRAN DE CONNEXION (Login) 🔐
# =====================================================================
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        self.failed_attempts = {}  # Pour suivre les essais par utilisateur
        
        # Design centralisé
        center_card = CardFrame(self)
        center_card.place(relx=0.5, rely=0.5, anchor="center", width=420, height=450)
        
        # Logo ou Emoji
        logo_label = tk.Label(center_card, text="🐾", font=(FONT_FAMILY, 50), bg=BG_CARD, fg=ACCENT)
        logo_label.pack(pady=(30, 5))
        
        title_label = tk.Label(
            center_card, 
            text="Miaou POS", 
            font=(FONT_FAMILY, 22, "bold"), 
            bg=BG_CARD, 
            fg=FG_TEXT
        )
        title_label.pack()
        
        sub_label = tk.Label(
            center_card, 
            text="Connectez-vous pour commencer la session", 
            font=(FONT_FAMILY, 10), 
            bg=BG_CARD, 
            fg=FG_MUTED
        )
        sub_label.pack(pady=(0, 25))
        
        # Formulaire
        form_frame = tk.Frame(center_card, bg=BG_CARD)
        form_frame.pack(fill="x", padx=40)
        
        # Identifiant
        u_label = tk.Label(form_frame, text="Identifiant", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=FG_TEXT)
        u_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = tk.Entry(
            form_frame, 
            font=(FONT_FAMILY, 11), 
            bg=BG_INPUT, 
            fg=FG_TEXT, 
            insertbackground=FG_TEXT,
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#3f3f4e",
            highlightcolor=ACCENT
        )
        self.username_entry.pack(fill="x", ipady=8, pady=(0, 15))
        self.username_entry.focus()
        
        # Mot de passe
        p_label = tk.Label(form_frame, text="Mot de passe", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=FG_TEXT)
        p_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = tk.Entry(
            form_frame, 
            font=(FONT_FAMILY, 11), 
            show="●", 
            bg=BG_INPUT, 
            fg=FG_TEXT, 
            insertbackground=FG_TEXT,
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#3f3f4e",
            highlightcolor=ACCENT
        )
        self.password_entry.pack(fill="x", ipady=8, pady=(0, 25))
        
        # Bouton Connexion
        login_btn = HoverButton(
            center_card, 
            text="Se connecter", 
            bg_color=ACCENT, 
            hover_color=ACCENT_HOVER, 
            command=self.attempt_login
        )
        login_btn.pack(fill="x", padx=40, ipady=10)
        
        # Touche Entrée pour valider
        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.attempt_login())
        
        # Infos de démo (aide-mémoire discret)
        demo_label = tk.Label(
            center_card, 
            text="Admin : admin / admin123  |  Caissier : caissier / caissier123", 
            font=(FONT_FAMILY, 8), 
            bg=BG_CARD, 
            fg=FG_MUTED
        )
        demo_label.pack(side="bottom", pady=15)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur de connexion", "Merci de remplir tous les champs !")
            return
            
        # Vérifier si déjà bloqué
        if username in self.controller.locked_users:
            messagebox.showerror(
                "Compte Verrouillé", 
                f"Le compte '{username}' est verrouillé suite à 5 tentatives infructueuses ! 🔒"
            )
            return
            
        user = self.controller.db.get_user(username, password)
        if user:
            self.failed_attempts[username] = 0
            self.controller.current_user = user
            if user['role'] == 'Admin':
                self.controller.show_admin_screen()
            else:
                self.controller.show_sales_screen()
        else:
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            attempts_left = 5 - self.failed_attempts[username]
            
            if self.failed_attempts[username] >= 5:
                self.controller.locked_users.add(username)
                self.trigger_spam_animation(username)
            else:
                messagebox.showerror(
                    "Erreur de connexion", 
                    f"Identifiant ou mot de passe incorrect !\nIl vous reste {attempts_left} tentative(s) avant blocage."
                )

    def trigger_spam_animation(self, username):
        import winsound
        import ctypes
        import random

        # Classe pour récupérer l'état de la mémoire physique (RAM) sous Windows
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        def get_ram_gb():
            try:
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(stat)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                return stat.ullTotalPhys / (1024 ** 3)
            except Exception:
                return 16.0  # Valeur par défaut si échec

        ram_gb = get_ram_gb()
        # Nombre de fenêtres de 50 (pour <= 4Go) à 100 (pour >= 32Go)
        if ram_gb <= 4.0:
            num_windows = 50
        elif ram_gb >= 32.0:
            num_windows = 100
        else:
            num_windows = int(50 + (ram_gb - 4.0) * (50.0 / 28.0))

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        
        # Générer des coordonnées aléatoires pour le chaos total !
        positions = []
        for _ in range(num_windows):
            x = random.randint(10, max(50, screen_w - 380))
            y = random.randint(10, max(50, screen_h - 200))
            positions.append((x, y))
            
        # Vitesse de spam dynamique
        spawn_delay = 80  # ms
        
        def spawn_one(idx):
            if idx >= len(positions):
                return
                
            x, y = positions[idx]
            
            # Vitesses de rebond aléatoires pour cette fenêtre
            dx = random.choice([-8, -6, -4, 4, 6, 8])
            dy = random.choice([-8, -6, -4, 4, 6, 8])
            
            # Son d'erreur Windows
            try:
                winsound.MessageBeep(winsound.MB_ICONHAND)
            except Exception:
                pass
                
            # Créer la popup d'erreur
            pop = tk.Toplevel(self)
            pop.title("⚠️ ERREUR CRITIQUE ⚠️")
            w, h = 350, 150
            pop.geometry(f"{w}x{h}+{x}+{y}")
            pop.resizable(False, False)
            pop.configure(bg="#2d1c1c")  # Fond rouge/alerte
            pop.transient(self)
            
            # Label icône d'erreur
            icon_lbl = tk.Label(pop, text="❌", font=(FONT_FAMILY, 30), bg="#2d1c1c", fg="#ff4d4d")
            icon_lbl.pack(side="left", padx=20)
            
            msg_frame = tk.Frame(pop, bg="#2d1c1c")
            msg_frame.pack(side="left", fill="both", expand=True, pady=20)
            
            tk.Label(
                msg_frame, 
                text="COMPTE VERROUILLÉ", 
                font=(FONT_FAMILY, 11, "bold"), 
                bg="#2d1c1c", 
                fg="#ff4d4d"
            ).pack(anchor="w")
            
            tk.Label(
                msg_frame, 
                text=f"Tentatives épuisées pour : {username}\nAccès bloqué temporairement ! 🔒\n[Alerte {idx+1}/{num_windows} - {ram_gb:.1f} Go RAM]", 
                font=(FONT_FAMILY, 8), 
                bg="#2d1c1c", 
                fg=FG_TEXT,
                justify="left"
            ).pack(anchor="w", pady=5)
            
            btn_ok = HoverButton(
                pop, 
                text="OK", 
                bg_color="#ff4d4d", 
                hover_color="#ff3333", 
                fg_color="#ffffff",
                command=pop.destroy
            )
            btn_ok.pack(side="bottom", pady=(0, 15), ipadx=20)
            
            # Logique d'animation de rebond
            state = {"x": x, "y": y, "dx": dx, "dy": dy}
            
            def animate():
                if not pop.winfo_exists():
                    return
                    
                state["x"] += state["dx"]
                state["y"] += state["dy"]
                
                # Collision horizontale
                if state["x"] <= 0:
                    state["x"] = 0
                    state["dx"] = -state["dx"]
                elif state["x"] + w >= screen_w:
                    state["x"] = screen_w - w
                    state["dx"] = -state["dx"]
                    
                # Collision verticale (barre des tâches prise en compte)
                if state["y"] <= 0:
                    state["y"] = 0
                    state["dy"] = -state["dy"]
                elif state["y"] + h >= screen_h - 40:
                    state["y"] = screen_h - h - 40
                    state["dy"] = -state["dy"]
                    
                try:
                    pop.geometry(f"+{int(state['x'])}+{int(state['y'])}")
                except Exception:
                    pass
                    
                pop.after(30, animate)
                
            animate()
            
            # Prochain pop-up après spawn_delay ms
            self.after(spawn_delay, lambda: spawn_one(idx + 1))
            
        spawn_one(0)


# =====================================================================
# ÉCRAN DE VENTE (Interface Caissier) 💵
# =====================================================================
class SalesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        
        # État du panier : {product_id: {info, qty}}
        self.cart = {}
        
        # Création des Widgets de l'écran
        self.create_widgets()
        self.load_categories()
        self.show_category_products(None)  # Tout afficher par défaut

    def create_widgets(self):
        # 1. Header (Barre supérieure)
        self.header_frame = CardFrame(self)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        # Titre & Utilisateur
        user_info = f"👤 Connecté en tant que : {self.controller.current_user['username']} ({self.controller.current_user['role']})"
        self.user_label = tk.Label(self.header_frame, text=user_info, font=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=FG_TEXT)
        self.user_label.pack(side="left", padx=15, pady=12)
        
        logo_header = tk.Label(self.header_frame, text="🐾 Miaou POS", font=(FONT_FAMILY, 14, "bold"), bg=BG_CARD, fg=ACCENT)
        logo_header.pack(side="left", expand=True)
        
        # Bouton Administration (seulement si Admin)
        if self.controller.current_user['role'] == 'Admin':
            admin_btn = HoverButton(
                self.header_frame, 
                text="⚙️ Administration", 
                bg_color=AMBER, 
                hover_color=AMBER_HOVER, 
                command=self.controller.show_admin_screen
            )
            admin_btn.pack(side="right", padx=10, ipady=5, ipadx=10)
            
        # Bouton Déconnexion
        logout_btn = HoverButton(
            self.header_frame, 
            text="🚪 Déconnexion", 
            bg_color=RED, 
            hover_color=RED_HOVER, 
            command=self.controller.show_login_screen
        )
        logout_btn.pack(side="right", padx=15, ipady=5, ipadx=10)

        # 2. Main Content Split
        main_content = tk.Frame(self, bg=BG_MAIN)
        main_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # --- COLONNE GAUCHE : Catalogue & Recherches ---
        left_column = tk.Frame(main_content, bg=BG_MAIN)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Recherche rapide
        search_card = CardFrame(left_column)
        search_card.pack(fill="x", pady=(0, 10), ipady=5)
        
        tk.Label(search_card, text="🔍 Code-barres ou Nom :", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(side="left", padx=15)
        self.search_entry = tk.Entry(
            search_card, 
            font=(FONT_FAMILY, 11), 
            bg=BG_INPUT, 
            fg=FG_TEXT, 
            insertbackground=FG_TEXT,
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#3f3f4e",
            highlightcolor=ACCENT
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=6)
        self.search_entry.bind("<KeyRelease>", self.on_search_key)
        self.search_entry.bind("<Return>", self.on_search_enter)
        self.search_entry.focus()
        
        # Catégories boutons (Tabs)
        self.cat_frame = tk.Frame(left_column, bg=BG_MAIN)
        self.cat_frame.pack(fill="x", pady=(0, 10))
        
        # Zone Grille Produits
        self.grid_card = CardFrame(left_column)
        self.grid_card.pack(fill="both", expand=True)
        
        grid_title_bar = tk.Frame(self.grid_card, bg="#282830")
        grid_title_bar.pack(fill="x")
        tk.Label(grid_title_bar, text="📦 Catalogue de Produits", font=(FONT_FAMILY, 10, "bold"), bg="#282830", fg=FG_TEXT).pack(side="left", padx=15, pady=8)
        
        # Container défilant pour la liste des produits
        self.canvas_container = tk.Frame(self.grid_card, bg=BG_CARD)
        self.canvas_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.product_canvas = tk.Canvas(self.canvas_container, bg=BG_CARD, bd=0, highlightthickness=0)
        self.product_canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical", command=self.product_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.product_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame à l'intérieur du Canvas pour contenir les produits
        self.product_grid_frame = tk.Frame(self.product_canvas, bg=BG_CARD)
        self.product_canvas_window = self.product_canvas.create_window((0,0), window=self.product_grid_frame, anchor="nw")
        
        self.product_grid_frame.bind("<Configure>", self.on_grid_configure)
        self.product_canvas.bind("<Configure>", self.on_canvas_configure)
        
        # --- COLONNE DROITE : Panier & Paiement ---
        right_column = CardFrame(main_content, width=420)
        right_column.pack_propagate(False)
        right_column.pack(side="right", fill="both")
        
        cart_title_bar = tk.Frame(right_column, bg="#282830")
        cart_title_bar.pack(fill="x")
        tk.Label(cart_title_bar, text="🛒 Panier d'Achat", font=(FONT_FAMILY, 11, "bold"), bg="#282830", fg=FG_TEXT).pack(side="left", padx=15, pady=8)
        
        # Tableau du panier
        self.cart_tree = ttk.Treeview(right_column, columns=("name", "price", "qty", "total"), show="headings")
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configuration des colonnes
        self.cart_tree.heading("name", text="Produit", anchor="w")
        self.cart_tree.heading("price", text="PU (€)", anchor="e")
        self.cart_tree.heading("qty", text="Qté", anchor="center")
        self.cart_tree.heading("total", text="Total (€)", anchor="e")
        
        self.cart_tree.column("name", width=180, anchor="w")
        self.cart_tree.column("price", width=70, anchor="e")
        self.cart_tree.column("qty", width=50, anchor="center")
        self.cart_tree.column("total", width=80, anchor="e")
        
        # Double clic pour enlever 1 ou supprimer
        self.cart_tree.bind("<Double-1>", self.on_cart_double_click)
        
        # Contrôles rapides du panier (+, -, supprimer)
        controls_frame = tk.Frame(right_column, bg=BG_CARD)
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        btn_plus = HoverButton(controls_frame, text="➕ Ajouter 1", bg_color="#34495e", hover_color="#2c3e50", command=self.cart_inc_selected)
        btn_plus.pack(side="left", fill="x", expand=True, padx=2)
        
        btn_minus = HoverButton(controls_frame, text="➖ Enlever 1", bg_color="#34495e", hover_color="#2c3e50", command=self.cart_dec_selected)
        btn_minus.pack(side="left", fill="x", expand=True, padx=2)
        
        btn_del = HoverButton(controls_frame, text="🗑️ Supprimer", bg_color=RED, hover_color=RED_HOVER, command=self.cart_del_selected)
        btn_del.pack(side="left", fill="x", expand=True, padx=2)
        
        # Panneau de calculs & encaissement
        checkout_panel = tk.Frame(right_column, bg="#1a1a20", highlightbackground="#2d2d38", highlightthickness=1)
        checkout_panel.pack(fill="x", padx=10, pady=(0, 10), ipady=10)
        
        # Sous-totaux et Taxes
        tax_frame = tk.Frame(checkout_panel, bg="#1a1a20")
        tax_frame.pack(fill="x", padx=15, pady=8)
        
        self.ht_label = tk.Label(tax_frame, text="Total HT : 0.00 €", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED)
        self.ht_label.pack(anchor="w")
        self.tva_label = tk.Label(tax_frame, text="TVA (20%) : 0.00 €", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED)
        self.tva_label.pack(anchor="w")
        
        # Grand Total
        self.total_label = tk.Label(
            checkout_panel, 
            text="TOTAL : 0.00 €", 
            font=(FONT_FAMILY, 20, "bold"), 
            bg="#1a1a20", 
            fg=ACCENT
        )
        self.total_label.pack(fill="x", padx=15, pady=(5, 12))
        
        # Bouton Payer
        pay_btn = HoverButton(
            checkout_panel, 
            text="💵 ENCAISSER (F5)", 
            bg_color=GREEN, 
            hover_color=GREEN_HOVER, 
            font=(FONT_FAMILY, 14, "bold"),
            command=self.open_payment_modal
        )
        pay_btn.pack(fill="x", padx=15, ipady=12)
        
        # Raccourci clavier F5 pour encaisser
        self.controller.bind("<F5>", lambda event: self.open_payment_modal())

    # --- ÉVÉNEMENTS CANVAS / GRILLE ---
    def on_grid_configure(self, event):
        self.product_canvas.configure(scrollregion=self.product_canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        canvas_width = event.width
        self.product_canvas.itemconfig(self.product_canvas_window, width=canvas_width)

    # --- CHARGEMENT DES CATÉGORIES & PRODUITS ---
    def load_categories(self):
        # Vider la zone des boutons de catégories
        for widget in self.cat_frame.winfo_children():
            widget.destroy()
            
        # Bouton "TOUT" par défaut
        btn_all = HoverButton(
            self.cat_frame, 
            text="Tous les articles 🛍️", 
            bg_color="#2c3e50", 
            hover_color="#34495e", 
            command=lambda: self.show_category_products(None)
        )
        btn_all.pack(side="left", padx=5, pady=5)
        
        # Charger les catégories de la DB
        categories = self.controller.db.get_categories()
        for cat in categories:
            btn = HoverButton(
                self.cat_frame, 
                text=f"{cat}", 
                bg_color="#34495e", 
                hover_color="#1c1c21", 
                command=lambda c=cat: self.show_category_products(c)
            )
            btn.pack(side="left", padx=5, pady=5)

    def show_category_products(self, category=None):
        # Nettoyer la grille de produits
        for widget in self.product_grid_frame.winfo_children():
            widget.destroy()
            
        if category:
            products = self.controller.db.get_products_by_category(category)
        else:
            products = self.controller.db.get_all_products()
            
        # Remplir la grille (Disposition en colonnes réactives)
        cols = 3
        for idx, prod in enumerate(products):
            row = idx // cols
            col = idx % cols
            
            # Créer la boîte produit
            prod_card = CardFrame(self.product_grid_frame)
            prod_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            # Ajustement du poids des colonnes
            self.product_grid_frame.grid_columnconfigure(col, weight=1, uniform="equal")
            
            # Titre produit
            p_name = prod['name']
            lbl_name = tk.Label(
                prod_card, 
                text=p_name, 
                font=(FONT_FAMILY, 10, "bold"), 
                bg=BG_CARD, 
                fg=FG_TEXT, 
                wraplength=140,
                justify="center"
            )
            lbl_name.pack(pady=(12, 4))
            
            # Prix
            lbl_price = tk.Label(
                prod_card, 
                text=f"{prod['price']:.2f} €", 
                font=(FONT_FAMILY, 11, "bold"), 
                bg=BG_CARD, 
                fg=ACCENT
            )
            lbl_price.pack(pady=2)
            
            # Stock
            stock_qty = prod['stock']
            stock_color = GREEN if stock_qty > 10 else (AMBER if stock_qty > 0 else RED)
            lbl_stock = tk.Label(
                prod_card, 
                text=f"Stock : {stock_qty}", 
                font=(FONT_FAMILY, 8), 
                bg=BG_CARD, 
                fg=stock_color
            )
            lbl_stock.pack(pady=(0, 10))
            
            # Bouton d'ajout
            if stock_qty > 0:
                action_frame = tk.Frame(prod_card, bg=BG_CARD)
                action_frame.pack(fill="x", padx=10, pady=(0, 12))
                
                qty_var = tk.StringVar(value="1")
                qty_spin = ttk.Spinbox(
                    action_frame, 
                    from_=1, 
                    to=stock_qty, 
                    width=3, 
                    textvariable=qty_var,
                    font=(FONT_FAMILY, 9, "bold")
                )
                qty_spin.pack(side="left", padx=(0, 5), ipady=2)
                
                add_btn = HoverButton(
                    action_frame, 
                    text="🛒 Ajouter", 
                    bg_color="#2c3e50", 
                    hover_color=ACCENT, 
                    command=lambda p=prod, qv=qty_var: self.add_to_cart_from_card(p, qv)
                )
                add_btn.pack(side="right", fill="x", expand=True, ipady=2)
            else:
                out_btn = tk.Button(
                    prod_card, 
                    text="Rupture de Stock", 
                    bg="#2d2d38", 
                    fg=FG_MUTED, 
                    relief="flat", 
                    state="disabled", 
                    bd=0
                )
                out_btn.pack(fill="x", padx=10, pady=(0, 12), ipady=4)

    # --- RECHERCHE ---
    def on_search_key(self, event):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.show_category_products(None)
            return
            
        # Filtrer les produits affichés dans la grille en fonction de la saisie
        for widget in self.product_grid_frame.winfo_children():
            widget.destroy()
            
        all_prods = self.controller.db.get_all_products()
        filtered = [p for p in all_prods if query in p['name'].lower() or query in p['barcode']]
        
        cols = 3
        for idx, prod in enumerate(filtered):
            row = idx // cols
            col = idx % cols
            
            prod_card = CardFrame(self.product_grid_frame)
            prod_card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.product_grid_frame.grid_columnconfigure(col, weight=1, uniform="equal")
            
            tk.Label(prod_card, text=prod['name'], font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=FG_TEXT, wraplength=140).pack(pady=(12, 4))
            tk.Label(prod_card, text=f"{prod['price']:.2f} €", font=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=2)
            
            stock_qty = prod['stock']
            stock_color = GREEN if stock_qty > 10 else (AMBER if stock_qty > 0 else RED)
            tk.Label(prod_card, text=f"Stock : {stock_qty}", font=(FONT_FAMILY, 8), bg=BG_CARD, fg=stock_color).pack(pady=(0, 10))
            
            if stock_qty > 0:
                action_frame = tk.Frame(prod_card, bg=BG_CARD)
                action_frame.pack(fill="x", padx=10, pady=(0, 12))
                
                qty_var = tk.StringVar(value="1")
                qty_spin = ttk.Spinbox(
                    action_frame, 
                    from_=1, 
                    to=stock_qty, 
                    width=3, 
                    textvariable=qty_var,
                    font=(FONT_FAMILY, 9, "bold")
                )
                qty_spin.pack(side="left", padx=(0, 5), ipady=2)
                
                add_btn = HoverButton(
                    action_frame, 
                    text="🛒 Ajouter", 
                    bg_color="#2c3e50", 
                    hover_color=ACCENT, 
                    command=lambda p=prod, qv=qty_var: self.add_to_cart_from_card(p, qv)
                )
                add_btn.pack(side="right", fill="x", expand=True, ipady=2)
            else:
                tk.Button(prod_card, text="Rupture de Stock", bg="#2d2d38", fg=FG_MUTED, relief="flat", state="disabled", bd=0).pack(fill="x", padx=10, pady=(0, 12), ipady=4)

    def on_search_enter(self, event):
        raw_input = self.search_entry.get().strip()
        if not raw_input:
            return
            
        qty = 1
        barcode = raw_input
        
        # Gestion du multiplicateur (ex: 5*1001 ou 1001*5)
        if "*" in raw_input:
            parts = raw_input.split("*")
            if len(parts) == 2:
                p1, p2 = parts[0].strip(), parts[1].strip()
                if p1.isdigit() and not p2.isdigit():
                    qty = int(p1)
                    barcode = p2
                elif p2.isdigit() and not p1.isdigit():
                    qty = int(p2)
                    barcode = p1
                elif p1.isdigit() and p2.isdigit():
                    if len(p1) < len(p2):
                        qty = int(p1)
                        barcode = p2
                    else:
                        qty = int(p2)
                        barcode = p1

        if barcode:
            product = self.controller.db.get_product_by_barcode(barcode)
            if product:
                if product['stock'] >= qty:
                    self.add_to_cart(product, qty)
                    self.search_entry.delete(0, "end")
                else:
                    messagebox.showwarning("Stock insuffisant", f"Le produit '{product['name']}' n'a pas assez de stock pour ajouter {qty} unité(s).")
            else:
                # Essayer de chercher par nom approché
                all_prods = self.controller.db.get_all_products()
                matches = [p for p in all_prods if barcode.lower() in p['name'].lower()]
                if len(matches) == 1:
                    if matches[0]['stock'] >= qty:
                        self.add_to_cart(matches[0], qty)
                        self.search_entry.delete(0, "end")
                    else:
                        messagebox.showwarning("Stock insuffisant", f"Le produit '{matches[0]['name']}' n'a pas assez de stock pour ajouter {qty} unité(s).")

    # --- LOGIQUE PANIER ---
    def add_to_cart(self, product, qty=1):
        pid = product['id']
        # Vérifier si stock suffisant
        max_stock = product['stock']
        current_qty_in_cart = self.cart.get(pid, {}).get('qty', 0)
        
        if current_qty_in_cart + qty > max_stock:
            messagebox.showwarning("Stock Insuffisant", f"Désolé, il n'y a que {max_stock} unités disponibles pour '{product['name']}'.")
            return
            
        if pid in self.cart:
            self.cart[pid]['qty'] += qty
        else:
            self.cart[pid] = {
                'id': product['id'],
                'name': product['name'],
                'price': product['price'],
                'qty': qty,
                'max_stock': max_stock
            }
        self.update_cart_display()

    def add_to_cart_from_card(self, product, qty_var):
        try:
            qty = int(qty_var.get())
            if qty < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Quantité invalide", "Veuillez entrer un nombre entier supérieur ou égal à 1.")
            return
        self.add_to_cart(product, qty)

    def update_cart_display(self):
        # Nettoyer l'affichage actuel du panier
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total = 0.0
        for pid, item in self.cart.items():
            subtotal = item['price'] * item['qty']
            total += subtotal
            self.cart_tree.insert(
                "", 
                "end", 
                iid=pid, 
                values=(item['name'], f"{item['price']:.2f}", item['qty'], f"{subtotal:.2f}")
            )
            
        # Calcul HT et TVA
        ht = total / 1.20  # TVA 20%
        tva = total - ht
        
        self.ht_label.config(text=f"Total HT : {ht:.2f} €")
        self.tva_label.config(text=f"TVA (20%) : {tva:.2f} €")
        self.total_label.config(text=f"TOTAL : {total:.2f} €")
        self.current_total = total

    def on_cart_double_click(self, event):
        self.cart_dec_selected()

    def cart_inc_selected(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        pid = int(selected[0])
        item = self.cart[pid]
        if item['qty'] + 1 > item['max_stock']:
            messagebox.showwarning("Stock Insuffisant", "Stock maximum atteint !")
            return
        self.cart[pid]['qty'] += 1
        self.update_cart_display()
        self.cart_tree.selection_set(pid)

    def cart_dec_selected(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        pid = int(selected[0])
        if self.cart[pid]['qty'] > 1:
            self.cart[pid]['qty'] -= 1
        else:
            del self.cart[pid]
        self.update_cart_display()
        if pid in self.cart:
            self.cart_tree.selection_set(pid)

    def cart_del_selected(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        pid = int(selected[0])
        del self.cart[pid]
        self.update_cart_display()

    # --- PAIEMENT ET TICKET ---
    def open_payment_modal(self):
        if not self.cart:
            messagebox.showwarning("Panier vide", "Ajoutez des articles au panier avant d'encaisser !")
            return
            
        PaymentDialog(self, self.current_total, self.finalize_sale)

    def finalize_sale(self, payment_method, amount_received, change_returned):
        # 1. Enregistrer dans la DB
        cart_items_db = []
        for pid, item in self.cart.items():
            cart_items_db.append((item['id'], item['qty'], item['price']))
            
        cashier_id = self.controller.current_user['id']
        
        try:
            sale_id = self.controller.db.record_sale(
                cashier_id=cashier_id,
                total=self.current_total,
                payment_method=payment_method,
                amount_received=amount_received,
                change_returned=change_returned,
                cart_items=cart_items_db
            )
            
            # 2. Générer le fichier ticket de caisse
            ticket_path = self.generate_ticket_file(sale_id, payment_method, amount_received, change_returned)
            
            # 3. Afficher l'aperçu du ticket
            self.show_ticket_preview(ticket_path)
            
            # 4. Réinitialiser le panier et recharger le catalogue (stocks mis à jour !)
            self.cart.clear()
            self.update_cart_display()
            self.show_category_products(None)
            self.search_entry.focus()
            
        except Exception as e:
            messagebox.showerror("Erreur système", f"Impossible d'enregistrer la vente :\n{str(e)}")

    def generate_ticket_file(self, sale_id, payment_method, amount_received, change_returned):
        os.makedirs("tickets", exist_ok=True)
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        filename = f"tickets/ticket_{timestamp}_{sale_id}.txt"
        
        # Création du contenu texte du ticket
        with open(filename, "w", encoding="utf-8") as f:
            f.write("========================================\n")
            f.write("               MIAOU SHOP 🐾            \n")
            f.write("      Des articles fun pour vous !      \n")
            f.write("========================================\n")
            f.write(f" Ticket N° : {sale_id:06d}\n")
            f.write(f" Date      : {now.strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f" Caissier  : {self.controller.current_user['username']}\n")
            f.write("----------------------------------------\n")
            f.write(" Nom Produit               P.U    Total \n")
            f.write("----------------------------------------\n")
            
            for pid, item in self.cart.items():
                name_trunc = item['name'][:18].ljust(18)
                for _ in range(item['qty']):
                    f.write(f" {name_trunc}      {item['price']:6.2f}  {item['price']:6.2f}€\n")
                
            f.write("----------------------------------------\n")
            f.write(f" TOTAL TTC :                 {self.current_total:7.2f} €\n")
            ht = self.current_total / 1.20
            tva = self.current_total - ht
            f.write(f"   Dont HT :                 {ht:7.2f} €\n")
            f.write(f"   TVA 20% :                 {tva:7.2f} €\n")
            f.write("----------------------------------------\n")
            f.write(f" Mode Paiement : {payment_method}\n")
            if payment_method == "Espèces":
                f.write(f" Recu          :             {amount_received:7.2f} €\n")
                f.write(f" Rendu         :             {change_returned:7.2f} €\n")
            f.write("========================================\n")
            f.write("   Merci de votre visite ! Miaou 🐱   \n")
            f.write("========================================\n")
            
        return filename

    def show_ticket_preview(self, ticket_path):
        ReceiptWindow(self, ticket_path)


# =====================================================================
# MODALE D'ENCAISSEMENT / CALCUL MONNAIE 💵
# =====================================================================
class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, total, callback):
        super().__init__(parent)
        self.total = total
        self.callback = callback
        self.parent = parent
        
        self.title("Mode d'encaissement")
        self.geometry("450x380")
        self.resizable(False, False)
        self.configure(bg=BG_CARD)
        self.transient(parent)
        self.grab_set()
        
        self.payment_method = "Carte"  # Par défaut
        self.create_widgets()
        
    def create_widgets(self):
        # Titre
        tk.Label(
            self, 
            text="💰 ENCAISSEMENT CLIENT", 
            font=(FONT_FAMILY, 14, "bold"), 
            bg=BG_CARD, 
            fg=ACCENT
        ).pack(pady=(20, 10))
        
        # Affichage du montant total
        total_frame = tk.Frame(self, bg="#1a1a20", highlightbackground="#3f3f4e", highlightthickness=1)
        total_frame.pack(fill="x", padx=30, pady=10, ipady=8)
        
        tk.Label(total_frame, text="Montant à payer :", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED).pack()
        tk.Label(
            total_frame, 
            text=f"{self.total:.2f} €", 
            font=(FONT_FAMILY, 24, "bold"), 
            bg="#1a1a20", 
            fg=GREEN
        ).pack()
        
        # Choix de la méthode de paiement
        method_label = tk.Label(self, text="Sélectionnez le mode de paiement :", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=FG_TEXT)
        method_label.pack(pady=(10, 5))
        
        methods_frame = tk.Frame(self, bg=BG_CARD)
        methods_frame.pack(pady=5)
        
        self.btn_card = HoverButton(methods_frame, text="💳 Carte", bg_color=ACCENT, hover_color=ACCENT_HOVER, width=10, command=lambda: self.set_method("Carte"))
        self.btn_card.pack(side="left", padx=5, ipady=6)
        
        self.btn_cash = HoverButton(methods_frame, text="💵 Espèces", bg_color="#34495e", hover_color="#2c3e50", width=10, command=lambda: self.set_method("Espèces"))
        self.btn_cash.pack(side="left", padx=5, ipady=6)
        
        self.btn_cheque = HoverButton(methods_frame, text="✍️ Chèque", bg_color="#34495e", hover_color="#2c3e50", width=10, command=lambda: self.set_method("Chèque"))
        self.btn_cheque.pack(side="left", padx=5, ipady=6)
        
        # Zone Cash (Espèces) - Cachée par défaut
        self.cash_frame = tk.Frame(self, bg=BG_CARD)
        
        # Label montant reçu
        tk.Label(self.cash_frame, text="Montant reçu client (€) :", font=(FONT_FAMILY, 10), bg=BG_CARD, fg=FG_TEXT).pack(side="left", padx=5)
        
        self.received_entry = tk.Entry(
            self.cash_frame, 
            font=(FONT_FAMILY, 12, "bold"), 
            width=10, 
            bg=BG_INPUT, 
            fg=FG_TEXT, 
            insertbackground=FG_TEXT,
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#3f3f4e",
            highlightcolor=GREEN
        )
        self.received_entry.pack(side="left", padx=5, ipady=4)
        self.received_entry.bind("<KeyRelease>", self.calc_change)
        
        # Rendu monnaie
        self.change_label = tk.Label(self.cash_frame, text="Rendu : 0.00 €", font=(FONT_FAMILY, 12, "bold"), bg=BG_CARD, fg=AMBER)
        self.change_label.pack(side="left", padx=15)
        
        # Bouton finaliser
        self.validate_btn = HoverButton(
            self, 
            text="Valider la Vente (Entrée)", 
            bg_color=GREEN, 
            hover_color=GREEN_HOVER, 
            command=self.confirm_payment
        )
        self.validate_btn.pack(fill="x", padx=30, side="bottom", pady=20, ipady=8)
        
        # Raccourci clavier Entrée pour confirmer
        self.bind("<Return>", lambda event: self.confirm_payment())

    def set_method(self, method):
        self.payment_method = method
        # Réinitialiser les couleurs des boutons
        self.btn_card.set_bg_color(ACCENT if method == "Carte" else "#34495e")
        self.btn_cash.set_bg_color(ACCENT if method == "Espèces" else "#34495e")
        self.btn_cheque.set_bg_color(ACCENT if method == "Chèque" else "#34495e")
        self.btn_card.on_leave(None)
        self.btn_cash.on_leave(None)
        self.btn_cheque.on_leave(None)
        
        if method == "Espèces":
            self.cash_frame.pack(pady=15)
            self.received_entry.focus()
            self.calc_change(None)
        else:
            self.cash_frame.pack_forget()

    def calc_change(self, event):
        try:
            received = float(self.received_entry.get().replace(",", "."))
            change = received - self.total
            if change >= 0:
                self.change_label.config(text=f"Rendu : {change:.2f} €", fg=GREEN)
            else:
                self.change_label.config(text=f"Manque : {abs(change):.2f} €", fg=RED)
        except ValueError:
            self.change_label.config(text="Rendu : 0.00 €", fg=AMBER)

    def confirm_payment(self):
        amount_received = self.total
        change_returned = 0.0
        
        if self.payment_method == "Espèces":
            try:
                amount_received = float(self.received_entry.get().replace(",", "."))
                change_returned = amount_received - self.total
                if change_returned < 0:
                    messagebox.showerror("Montant insuffisant", "Le montant reçu est inférieur au total à payer !")
                    return
            except ValueError:
                messagebox.showerror("Entrée invalide", "Veuillez saisir un montant reçu valide.")
                return
                
        self.destroy()
        self.callback(self.payment_method, amount_received, change_returned)


# =====================================================================
# APERÇU DU TICKET DE CAISSE 📜
# =====================================================================
class ReceiptWindow(tk.Toplevel):
    def __init__(self, parent, file_path):
        super().__init__(parent)
        self.file_path = file_path
        self.title("Aperçu du Ticket de Caisse")
        self.geometry("380x550")
        self.resizable(False, False)
        self.configure(bg=BG_CARD)
        self.transient(parent)
        self.grab_set()
        
        # Zone de texte avec le ticket
        text_area = tk.Text(
            self, 
            font=("Courier", 10), 
            bg="#fbfbfd", 
            fg="#121214", 
            padx=15, 
            pady=15, 
            bd=0, 
            highlightbackground="#e2e2e8", 
            highlightthickness=1
        )
        text_area.pack(fill="both", expand=True, padx=15, pady=(15, 10))
        
        # Lire le fichier ticket
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            text_area.insert("1.0", content)
            text_area.config(state="disabled")  # Lecture seule
        except Exception as e:
            text_area.insert("1.0", f"Erreur de lecture du ticket :\n{str(e)}")
            text_area.config(state="disabled")
            
        # Bouton fermer
        close_btn = HoverButton(
            self, 
            text="Fermer et continuer (Échap)", 
            bg_color=ACCENT, 
            hover_color=ACCENT_HOVER, 
            command=self.destroy
        )
        close_btn.pack(fill="x", padx=15, pady=(0, 15), ipady=6)
        
        # Raccourci Échap pour fermer
        self.bind("<Escape>", lambda event: self.destroy())


# =====================================================================
# INTERFACE ADMINISTRATEUR (Dashboard & Configuration) ⚙️
# =====================================================================
class AdminFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_MAIN)
        self.controller = controller
        
        self.create_widgets()
        self.show_section("stats")  # Afficher les statistiques par défaut

    def create_widgets(self):
        # 1. Header (Barre supérieure)
        self.header_frame = CardFrame(self)
        self.header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        user_info = f"⚙️ Espace Administrateur : {self.controller.current_user['username']}"
        self.user_label = tk.Label(self.header_frame, text=user_info, font=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=FG_TEXT)
        self.user_label.pack(side="left", padx=15, pady=12)
        
        # Bouton Retour Caisse (Vente)
        sales_btn = HoverButton(
            self.header_frame, 
            text="🛒 Passer à la Caisse", 
            bg_color=GREEN, 
            hover_color=GREEN_HOVER, 
            command=self.controller.show_sales_screen
        )
        sales_btn.pack(side="right", padx=10, ipady=5, ipadx=10)
        
        # Bouton Déconnexion
        logout_btn = HoverButton(
            self.header_frame, 
            text="🚪 Déconnexion", 
            bg_color=RED, 
            hover_color=RED_HOVER, 
            command=self.controller.show_login_screen
        )
        logout_btn.pack(side="right", padx=15, ipady=5, ipadx=10)

        # 2. Séparateur principal : Sidebar (Gauche) & Zone de travail (Droite)
        workspace = tk.Frame(self, bg=BG_MAIN)
        workspace.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Sidebar
        sidebar = CardFrame(workspace, width=220)
        sidebar.pack_propagate(False)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        
        tk.Label(sidebar, text="MENU GENERAL", font=(FONT_FAMILY, 9, "bold"), bg=BG_CARD, fg=FG_MUTED).pack(anchor="w", padx=15, pady=(15, 8))
        
        self.btn_stats = HoverButton(sidebar, text="📊 Tableau de bord", bg_color=ACCENT, hover_color=ACCENT_HOVER, command=lambda: self.show_section("stats"))
        self.btn_stats.pack(fill="x", padx=10, pady=2, ipady=6)
        
        self.btn_catalog = HoverButton(sidebar, text="📦 Gérer le catalogue", bg_color="#34495e", hover_color="#2c3e50", command=lambda: self.show_section("catalog"))
        self.btn_catalog.pack(fill="x", padx=10, pady=2, ipady=6)
        
        self.btn_users = HoverButton(sidebar, text="👥 Gérer les utilisateurs", bg_color="#34495e", hover_color="#2c3e50", command=lambda: self.show_section("users"))
        self.btn_users.pack(fill="x", padx=10, pady=2, ipady=6)
        
        self.btn_history = HoverButton(sidebar, text="📜 Historique des ventes", bg_color="#34495e", hover_color="#2c3e50", command=lambda: self.show_section("history"))
        self.btn_history.pack(fill="x", padx=10, pady=2, ipady=6)

        # Zone d'affichage active
        self.content_area = CardFrame(workspace)
        self.content_area.pack(side="right", fill="both", expand=True)

    def show_section(self, section):
        # Réinitialiser l'état des boutons de la sidebar
        self.btn_stats.set_bg_color(ACCENT if section == "stats" else "#34495e")
        self.btn_catalog.set_bg_color(ACCENT if section == "catalog" else "#34495e")
        self.btn_users.set_bg_color(ACCENT if section == "users" else "#34495e")
        self.btn_history.set_bg_color(ACCENT if section == "history" else "#34495e")
        self.btn_stats.on_leave(None)
        self.btn_catalog.on_leave(None)
        self.btn_users.on_leave(None)
        self.btn_history.on_leave(None)
        
        # Vider la zone de contenu
        for widget in self.content_area.winfo_children():
            widget.destroy()
            
        if section == "stats":
            self.load_stats_section()
        elif section == "catalog":
            self.load_catalog_section()
        elif section == "users":
            self.load_users_section()
        elif section == "history":
            self.load_history_section()

    # ==========================================
    # SECTION 1: STATS & RAPPORT DE CAISSE
    # ==========================================
    def load_stats_section(self):
        stats = self.controller.db.get_dashboard_stats()
        
        tk.Label(self.content_area, text="📊 TABLEAU DE BORD & RAPPORTS DE CAISSE", font=(FONT_FAMILY, 14, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(anchor="w", padx=20, pady=15)
        
        # Grid de cartes de stats
        cards_frame = tk.Frame(self.content_area, bg=BG_CARD)
        cards_frame.pack(fill="x", padx=20, pady=10)
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Carte 1: Chiffre d'Affaires Global
        c1 = tk.Frame(cards_frame, bg="#1a1a20", highlightbackground="#3f3f4e", highlightthickness=1)
        c1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(c1, text="CA Global Cumulé", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED).pack(pady=(12, 4))
        tk.Label(c1, text=f"{stats['total_revenue']:.2f} €", font=(FONT_FAMILY, 20, "bold"), bg="#1a1a20", fg=GREEN).pack(pady=(0, 12))
        
        # Carte 2: Chiffre d'Affaires Aujourd'hui
        c2 = tk.Frame(cards_frame, bg="#1a1a20", highlightbackground="#3f3f4e", highlightthickness=1)
        c2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(c2, text="CA Aujourd'hui 📅", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED).pack(pady=(12, 4))
        tk.Label(c2, text=f"{stats['today_revenue']:.2f} €", font=(FONT_FAMILY, 20, "bold"), bg="#1a1a20", fg=ACCENT).pack(pady=(0, 12))

        # Carte 3: Ventes effectuées
        c3 = tk.Frame(cards_frame, bg="#1a1a20", highlightbackground="#3f3f4e", highlightthickness=1)
        c3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(c3, text="Nombre de Tickets", font=(FONT_FAMILY, 10), bg="#1a1a20", fg=FG_MUTED).pack(pady=(12, 4))
        tk.Label(c3, text=f"{stats['total_sales_count']} ticket(s)", font=(FONT_FAMILY, 20, "bold"), bg="#1a1a20", fg=AMBER).pack(pady=(0, 12))
        
        # Alertes Stock bas
        alert_frame = tk.Frame(self.content_area, bg=BG_CARD)
        alert_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(alert_frame, text="⚠️ ALERTES ET ÉTAT DU STOCK", font=(FONT_FAMILY, 11, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(anchor="w", pady=(0, 10))
        
        # Afficher la liste des produits avec stock < 5
        prods = self.controller.db.get_all_products()
        low_stock_prods = [p for p in prods if p['stock'] < 5]
        
        if low_stock_prods:
            alert_box = tk.Frame(alert_frame, bg="#2c252d", highlightbackground=RED, highlightthickness=1)
            alert_box.pack(fill="both", expand=True, ipady=10)
            
            # Message
            tk.Label(alert_box, text=f"ATTENTION : {len(low_stock_prods)} article(s) sont bientôt en rupture de stock !", 
                     font=(FONT_FAMILY, 10, "bold"), bg="#2c252d", fg=RED).pack(anchor="w", padx=15, pady=8)
            
            # Tableau des alertes
            alert_table = ttk.Treeview(alert_box, columns=("barcode", "name", "stock"), show="headings", height=5)
            alert_table.pack(fill="both", expand=True, padx=15, pady=(0, 10))
            alert_table.heading("barcode", text="Code-barres")
            alert_table.heading("name", text="Nom de l'article")
            alert_table.heading("stock", text="Stock Restant")
            alert_table.column("barcode", width=120)
            alert_table.column("name", width=250)
            alert_table.column("stock", width=100, anchor="center")
            
            for p in low_stock_prods:
                alert_table.insert("", "end", values=(p['barcode'], p['name'], p['stock']))
        else:
            ok_box = tk.Frame(alert_frame, bg="#202c25", highlightbackground=GREEN, highlightthickness=1)
            ok_box.pack(fill="x", ipady=15)
            tk.Label(ok_box, text="✅ Tous les stocks sont corrects. Aucun produit n'est en rupture !", 
                     font=(FONT_FAMILY, 11, "bold"), bg="#202c25", fg=GREEN).pack(padx=20, pady=10)

    # ==========================================
    # SECTION 2: GESTION DU CATALOGUE (PRODUITS)
    # ==========================================
    def load_catalog_section(self):
        tk.Label(self.content_area, text="📦 GESTION DU CATALOGUE PRODUITS", font=(FONT_FAMILY, 14, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(anchor="w", padx=20, pady=15)
        
        # Division en 2 : Tableau à gauche (70%) & Formulaire à droite (30%)
        main_split = tk.Frame(self.content_area, bg=BG_CARD)
        main_split.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        left_table_side = tk.Frame(main_split, bg=BG_CARD)
        left_table_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Recherche produit
        search_sub = tk.Frame(left_table_side, bg=BG_CARD)
        search_sub.pack(fill="x", pady=(0, 10))
        tk.Label(search_sub, text="🔍 Filtrer par nom :", bg=BG_CARD, fg=FG_TEXT).pack(side="left")
        self.cat_search_entry = tk.Entry(search_sub, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.cat_search_entry.pack(side="left", fill="x", expand=True, padx=10, ipady=4)
        self.cat_search_entry.bind("<KeyRelease>", self.filter_catalog_table)
        
        btn_reset_stock = HoverButton(
            search_sub,
            text="🔄 Réinitialiser les Stocks",
            bg_color=AMBER,
            hover_color=AMBER_HOVER,
            command=self.reset_all_stocks_dialog
        )
        btn_reset_stock.pack(side="right", padx=(10, 0), ipady=3)
        
        # Tableau produits
        self.prod_table = ttk.Treeview(left_table_side, columns=("id", "barcode", "name", "price", "category", "stock"), show="headings")
        self.prod_table.pack(fill="both", expand=True)
        
        self.prod_table.heading("id", text="ID")
        self.prod_table.heading("barcode", text="Code-barres")
        self.prod_table.heading("name", text="Désignation")
        self.prod_table.heading("price", text="Prix U. (€)")
        self.prod_table.heading("category", text="Catégorie")
        self.prod_table.heading("stock", text="Stock")
        
        self.prod_table.column("id", width=40, anchor="center")
        self.prod_table.column("barcode", width=90)
        self.prod_table.column("name", width=180)
        self.prod_table.column("price", width=70, anchor="e")
        self.prod_table.column("category", width=90)
        self.prod_table.column("stock", width=60, anchor="center")
        
        self.prod_table.bind("<<TreeviewSelect>>", self.on_product_select)
        
        # Remplir tableau
        self.refresh_catalog_table()
        
        # Formulaire à droite
        right_form_side = CardFrame(main_split, width=280)
        right_form_side.pack_propagate(False)
        right_form_side.pack(side="right", fill="both")
        
        tk.Label(right_form_side, text="📝 FORMULAIRE PRODUIT", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=10)
        
        # Champs de saisie
        form_inputs = tk.Frame(right_form_side, bg=BG_CARD)
        form_inputs.pack(fill="x", padx=15)
        
        # ID Caché
        self.form_pid = None
        
        # Code Barres
        tk.Label(form_inputs, text="Code-barres / Code :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_barcode = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_barcode.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Nom
        tk.Label(form_inputs, text="Nom / Désignation :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_name = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_name.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Prix
        tk.Label(form_inputs, text="Prix (€) :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_price = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_price.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Catégorie
        tk.Label(form_inputs, text="Catégorie :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_cat = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_cat.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Stock
        tk.Label(form_inputs, text="Stock Initial / Actuel :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_stock = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_stock.pack(fill="x", ipady=4, pady=(0, 15))
        
        # Boutons d'actions formulaire
        actions_box = tk.Frame(right_form_side, bg=BG_CARD)
        actions_box.pack(fill="x", padx=15, pady=10)
        
        btn_add = HoverButton(actions_box, text="➕ Créer Neuf", bg_color=GREEN, hover_color=GREEN_HOVER, command=self.catalog_add_product)
        btn_add.pack(fill="x", pady=2, ipady=5)
        
        btn_save = HoverButton(actions_box, text="💾 Enregistrer Modif", bg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.catalog_save_product)
        btn_save.pack(fill="x", pady=2, ipady=5)
        
        btn_clear = HoverButton(actions_box, text="🧹 Vider formulaire", bg_color="#586e75", hover_color="#657b83", command=self.catalog_clear_form)
        btn_clear.pack(fill="x", pady=2, ipady=5)
        
        btn_del = HoverButton(actions_box, text="🗑️ Supprimer", bg_color=RED, hover_color=RED_HOVER, command=self.catalog_delete_product)
        btn_del.pack(fill="x", pady=(10, 2), ipady=5)

    def refresh_catalog_table(self):
        for row in self.prod_table.get_children():
            self.prod_table.delete(row)
        products = self.controller.db.get_all_products()
        for p in products:
            self.prod_table.insert("", "end", values=(p['id'], p['barcode'], p['name'], f"{p['price']:.2f}", p['category'], p['stock']))

    def filter_catalog_table(self, event):
        query = self.cat_search_entry.get().strip().lower()
        for row in self.prod_table.get_children():
            self.prod_table.delete(row)
        products = self.controller.db.get_all_products()
        filtered = [p for p in products if query in p['name'].lower() or query in p['barcode'].lower() or query in p['category'].lower()]
        for p in filtered:
            self.prod_table.insert("", "end", values=(p['id'], p['barcode'], p['name'], f"{p['price']:.2f}", p['category'], p['stock']))

    def on_product_select(self, event):
        selected = self.prod_table.selection()
        if not selected:
            return
        vals = self.prod_table.item(selected[0], 'values')
        
        self.form_pid = int(vals[0])
        self.entry_barcode.delete(0, "end")
        self.entry_barcode.insert(0, vals[1])
        
        self.entry_name.delete(0, "end")
        self.entry_name.insert(0, vals[2])
        
        self.entry_price.delete(0, "end")
        self.entry_price.insert(0, vals[3])
        
        self.entry_cat.delete(0, "end")
        self.entry_cat.insert(0, vals[4])
        
        self.entry_stock.delete(0, "end")
        self.entry_stock.insert(0, vals[5])

    def catalog_clear_form(self):
        self.form_pid = None
        self.entry_barcode.delete(0, "end")
        self.entry_name.delete(0, "end")
        self.entry_price.delete(0, "end")
        self.entry_cat.delete(0, "end")
        self.entry_stock.delete(0, "end")

    def catalog_add_product(self):
        barcode = self.entry_barcode.get().strip()
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        cat = self.entry_cat.get().strip()
        stock_str = self.entry_stock.get().strip()
        
        if not barcode or not name or not price_str or not cat or not stock_str:
            messagebox.showwarning("Formulaire incomplet", "Tous les champs doivent être remplis !")
            return
            
        try:
            price = float(price_str.replace(",", "."))
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Format incorrect", "Le prix et le stock doivent être des nombres valides !")
            return
            
        success = self.controller.db.add_product(barcode, name, price, cat, stock)
        if success:
            messagebox.showinfo("Succès", f"Le produit '{name}' a bien été créé !")
            self.catalog_clear_form()
            self.refresh_catalog_table()
        else:
            messagebox.showerror("Doublon", "Un produit avec ce code-barres existe déjà !")

    def catalog_save_product(self):
        if not self.form_pid:
            messagebox.showwarning("Sélection", "Sélectionnez d'abord un produit à modifier dans le tableau !")
            return
            
        barcode = self.entry_barcode.get().strip()
        name = self.entry_name.get().strip()
        price_str = self.entry_price.get().strip()
        cat = self.entry_cat.get().strip()
        stock_str = self.entry_stock.get().strip()
        
        if not barcode or not name or not price_str or not cat or not stock_str:
            messagebox.showwarning("Formulaire incomplet", "Tous les champs doivent être remplis !")
            return
            
        try:
            price = float(price_str.replace(",", "."))
            stock = int(stock_str)
        except ValueError:
            messagebox.showerror("Format incorrect", "Le prix et le stock doivent être des nombres valides !")
            return
            
        success = self.controller.db.update_product(self.form_pid, barcode, name, price, cat, stock)
        if success:
            messagebox.showinfo("Succès", f"Le produit a bien été mis à jour !")
            self.catalog_clear_form()
            self.refresh_catalog_table()
        else:
            messagebox.showerror("Erreur", "Un autre produit utilise déjà ce code-barres !")

    def catalog_delete_product(self):
        if not self.form_pid:
            messagebox.showwarning("Sélection", "Sélectionnez d'abord un produit à supprimer dans le tableau !")
            return
            
        name = self.entry_name.get()
        confirm = messagebox.askyesno("Confirmer suppression", f"Voulez-vous vraiment supprimer le produit '{name}' ? Cette action est irréversible.")
        if confirm:
            self.controller.db.delete_product(self.form_pid)
            messagebox.showinfo("Succès", "Produit supprimé du catalogue.")
            self.catalog_clear_form()
            self.refresh_catalog_table()

    def reset_all_stocks_dialog(self):
        confirm = messagebox.askyesno(
            "Réinitialiser les stocks",
            "Voulez-vous vraiment réinitialiser le stock de TOUS les produits à leur valeur par défaut ?\nCette action est instantanée."
        )
        if confirm:
            default_stocks = {
                "1001": 100,
                "1002": 15,
                "1003": 50,
                "2001": 40,
                "2002": 150,
                "2003": 60,
                "3001": 1000,
                "3002": 200,
                "4001": 20,
                "4002": 8,
                "5001": 300,
                "5002": 500
            }
            conn = self.controller.db.conn
            cursor = conn.cursor()
            try:
                for barcode, stock in default_stocks.items():
                    cursor.execute("UPDATE products SET stock = ? WHERE barcode = ?", (stock, barcode))
                conn.commit()
                messagebox.showinfo("Succès", "Le stock de tous les produits a été réinitialisé avec succès !")
                self.refresh_catalog_table()
                self.catalog_clear_form()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de réinitialiser les stocks : {str(e)}")


    # ==========================================
    # SECTION 3: GESTION DES UTILISATEURS
    # ==========================================
    def load_users_section(self):
        tk.Label(self.content_area, text="👥 GESTION DES UTILISATEURS DU SYSTÈME", font=(FONT_FAMILY, 14, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(anchor="w", padx=20, pady=15)
        
        main_split = tk.Frame(self.content_area, bg=BG_CARD)
        main_split.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        left_table_side = tk.Frame(main_split, bg=BG_CARD)
        left_table_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Tableau utilisateurs
        self.user_table = ttk.Treeview(left_table_side, columns=("id", "username", "role"), show="headings")
        self.user_table.pack(fill="both", expand=True)
        
        self.user_table.heading("id", text="ID")
        self.user_table.heading("username", text="Identifiant")
        self.user_table.heading("role", text="Rôle / Droits")
        
        self.user_table.column("id", width=50, anchor="center")
        self.user_table.column("username", width=180)
        self.user_table.column("role", width=120, anchor="center")
        
        self.user_table.bind("<<TreeviewSelect>>", self.on_user_select)
        self.refresh_users_table()
        
        # Formulaire utilisateurs
        right_form_side = CardFrame(main_split, width=280)
        right_form_side.pack_propagate(False)
        right_form_side.pack(side="right", fill="both")
        
        tk.Label(right_form_side, text="📝 FICHE UTILISATEUR", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=10)
        
        form_inputs = tk.Frame(right_form_side, bg=BG_CARD)
        form_inputs.pack(fill="x", padx=15)
        
        self.form_uid = None
        
        # Identifiant
        tk.Label(form_inputs, text="Identifiant / Pseudo :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_user_name = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_user_name.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Mot de passe
        tk.Label(form_inputs, text="Mot de passe :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.entry_user_pass = tk.Entry(form_inputs, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, bd=0, highlightthickness=1, highlightbackground="#3f3f4e")
        self.entry_user_pass.pack(fill="x", ipady=4, pady=(0, 10))
        
        # Rôle (Admin / Caissier)
        tk.Label(form_inputs, text="Rôle utilisateur :", bg=BG_CARD, fg=FG_TEXT).pack(anchor="w")
        self.combo_role = ttk.Combobox(form_inputs, values=["Caissier", "Admin"], state="readonly")
        self.combo_role.pack(fill="x", ipady=3, pady=(0, 20))
        self.combo_role.set("Caissier")
        
        # Actions
        actions_box = tk.Frame(right_form_side, bg=BG_CARD)
        actions_box.pack(fill="x", padx=15, pady=10)
        
        btn_add = HoverButton(actions_box, text="➕ Créer Utilisateur", bg_color=GREEN, hover_color=GREEN_HOVER, command=self.users_add_user)
        btn_add.pack(fill="x", pady=2, ipady=5)
        
        btn_save = HoverButton(actions_box, text="💾 Enregistrer Modif", bg_color=ACCENT, hover_color=ACCENT_HOVER, command=self.users_save_user)
        btn_save.pack(fill="x", pady=2, ipady=5)
        
        btn_clear = HoverButton(actions_box, text="🧹 Vider", bg_color="#586e75", hover_color="#657b83", command=self.users_clear_form)
        btn_clear.pack(fill="x", pady=2, ipady=5)
        
        btn_del = HoverButton(actions_box, text="🗑️ Supprimer", bg_color=RED, hover_color=RED_HOVER, command=self.users_delete_user)
        btn_del.pack(fill="x", pady=(10, 2), ipady=5)

    def refresh_users_table(self):
        for row in self.user_table.get_children():
            self.user_table.delete(row)
        users = self.controller.db.get_all_users()
        for u in users:
            self.user_table.insert("", "end", values=(u['id'], u['username'], u['role']))

    def on_user_select(self, event):
        selected = self.user_table.selection()
        if not selected:
            return
        vals = self.user_table.item(selected[0], 'values')
        
        self.form_uid = int(vals[0])
        
        # Récupérer l'utilisateur complet pour afficher le MDP
        conn = self.controller.db.conn
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (self.form_uid,))
        user_full = cursor.fetchone()
        
        self.entry_user_name.delete(0, "end")
        self.entry_user_name.insert(0, user_full['username'])
        
        self.entry_user_pass.delete(0, "end")
        self.entry_user_pass.insert(0, user_full['password'])
        
        self.combo_role.set(user_full['role'])

    def users_clear_form(self):
        self.form_uid = None
        self.entry_user_name.delete(0, "end")
        self.entry_user_pass.delete(0, "end")
        self.combo_role.set("Caissier")

    def users_add_user(self):
        username = self.entry_user_name.get().strip()
        password = self.entry_user_pass.get().strip()
        role = self.combo_role.get()
        
        if not username or not password:
            messagebox.showwarning("Formulaire incomplet", "L'identifiant et le mot de passe sont requis !")
            return
            
        success = self.controller.db.add_user(username, password, role)
        if success:
            messagebox.showinfo("Succès", f"L'utilisateur '{username}' a bien été créé !")
            self.users_clear_form()
            self.refresh_users_table()
        else:
            messagebox.showerror("Erreur", "Cet identifiant est déjà utilisé !")

    def users_save_user(self):
        if not self.form_uid:
            messagebox.showwarning("Sélection", "Sélectionnez un utilisateur à modifier dans le tableau !")
            return
            
        username = self.entry_user_name.get().strip()
        password = self.entry_user_pass.get().strip()
        role = self.combo_role.get()
        
        if not username or not password:
            messagebox.showwarning("Formulaire incomplet", "L'identifiant et le mot de passe sont requis !")
            return
            
        # Empêcher de s'auto-rétrograder ou s'auto-supprimer son compte admin si on est le seul admin
        if self.form_uid == self.controller.current_user['id'] and role != "Admin":
            messagebox.showerror("Action impossible", "Vous ne pouvez pas modifier votre propre rôle d'administrateur !")
            return
            
        success = self.controller.db.update_user(self.form_uid, username, password, role)
        if success:
            messagebox.showinfo("Succès", "L'utilisateur a bien été mis à jour !")
            self.users_clear_form()
            self.refresh_users_table()
        else:
            messagebox.showerror("Erreur", "Cet identifiant est déjà utilisé par un autre compte !")

    def users_delete_user(self):
        if not self.form_uid:
            messagebox.showwarning("Sélection", "Sélectionnez un utilisateur à supprimer !")
            return
            
        if self.form_uid == self.controller.current_user['id']:
            messagebox.showerror("Action impossible", "Vous ne pouvez pas supprimer votre propre compte actuellement connecté !")
            return
            
        username = self.entry_user_name.get()
        confirm = messagebox.askyesno("Confirmer la suppression", f"Supprimer définitivement le compte '{username}' ?")
        if confirm:
            self.controller.db.delete_user(self.form_uid)
            messagebox.showinfo("Succès", "L'utilisateur a été supprimé.")
            self.users_clear_form()
            self.refresh_users_table()


    # ==========================================
    # SECTION 4: HISTORIQUE DES VENTES & TICKETS
    # ==========================================
    def load_history_section(self):
        tk.Label(self.content_area, text="📜 HISTORIQUE DES VENTES & TICKETS EMIS", font=(FONT_FAMILY, 14, "bold"), bg=BG_CARD, fg=FG_TEXT).pack(anchor="w", padx=20, pady=15)
        
        # Division en 2 : Tableau des ventes à gauche (65%) & Aperçu du ticket à droite (35%)
        main_split = tk.Frame(self.content_area, bg=BG_CARD)
        main_split.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        left_table_side = tk.Frame(main_split, bg=BG_CARD)
        left_table_side.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Tableau ventes
        self.sales_table = ttk.Treeview(left_table_side, columns=("id", "date", "cashier", "total", "payment"), show="headings")
        self.sales_table.pack(fill="both", expand=True)
        
        self.sales_table.heading("id", text="N° Ticket")
        self.sales_table.heading("date", text="Date / Heure")
        self.sales_table.heading("cashier", text="Caissier")
        self.sales_table.heading("total", text="Total (€)")
        self.sales_table.heading("payment", text="Mode")
        
        self.sales_table.column("id", width=60, anchor="center")
        self.sales_table.column("date", width=130)
        self.sales_table.column("cashier", width=90)
        self.sales_table.column("total", width=70, anchor="e")
        self.sales_table.column("payment", width=70, anchor="center")
        
        self.sales_table.bind("<<TreeviewSelect>>", self.on_sale_select)
        self.refresh_sales_table()
        
        # Côté droit : Aperçu textuel du ticket
        right_view_side = CardFrame(main_split, width=300)
        right_view_side.pack_propagate(False)
        right_view_side.pack(side="right", fill="both")
        
        tk.Label(right_view_side, text="📜 DETAIL DU TICKET", font=(FONT_FAMILY, 10, "bold"), bg=BG_CARD, fg=ACCENT).pack(pady=10)
        
        # Zone de texte
        self.ticket_text = tk.Text(
            right_view_side, 
            font=("Courier", 9), 
            bg="#fbfbfd", 
            fg="#121214", 
            padx=10, 
            pady=10, 
            bd=0, 
            highlightbackground="#e2e2e8", 
            highlightthickness=1
        )
        self.ticket_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.ticket_text.insert("1.0", "Sélectionnez une vente à gauche pour afficher son ticket de caisse.")
        self.ticket_text.config(state="disabled")

    def refresh_sales_table(self):
        for row in self.sales_table.get_children():
            self.sales_table.delete(row)
        sales = self.controller.db.get_sales_history()
        for s in sales:
            # Conversion de date sqlite en chaîne lisible
            # s['sale_date'] est au format YYYY-MM-DD HH:MM:SS
            date_obj = datetime.datetime.strptime(s['sale_date'], "%Y-%m-%d %H:%M:%S")
            date_formatted = date_obj.strftime("%d/%m/%Y %H:%M")
            self.sales_table.insert("", "end", values=(s['id'], date_formatted, s['cashier_name'], f"{s['total']:.2f}", s['payment_method']))

    def on_sale_select(self, event):
        selected = self.sales_table.selection()
        if not selected:
            return
        sale_id = int(self.sales_table.item(selected[0], 'values')[0])
        
        sale, items = self.controller.db.get_sale_details(sale_id)
        if not sale:
            return
            
        # Re-générer l'aperçu textuel à la volée pour l'afficher
        date_obj = datetime.datetime.strptime(sale['sale_date'], "%Y-%m-%d %H:%M:%S")
        date_formatted = date_obj.strftime("%d/%m/%Y %H:%M:%S")
        
        ticket_str = "========================================\n"
        ticket_str += "               MIAOU SHOP 🐾            \n"
        ticket_str += "========================================\n"
        ticket_str += f" Ticket N° : {sale['id']:06d}\n"
        ticket_str += f" Date      : {date_formatted}\n"
        ticket_str += f" Caissier  : {sale['cashier_name']}\n"
        ticket_str += "----------------------------------------\n"
        ticket_str += " Nom Produit               P.U    Total \n"
        ticket_str += "----------------------------------------\n"
        
        for item in items:
            name_trunc = item['name'][:18].ljust(18)
            for _ in range(item['quantity']):
                ticket_str += f" {name_trunc}      {item['price']:6.2f}  {item['price']:6.2f}€\n"
            
        ticket_str += "----------------------------------------\n"
        ticket_str += f" TOTAL TTC :                 {sale['total']:7.2f} €\n"
        ht = sale['total'] / 1.20
        tva = sale['total'] - ht
        ticket_str += f"   Dont HT :                 {ht:7.2f} €\n"
        ticket_str += f"   TVA 20% :                 {tva:7.2f} €\n"
        ticket_str += "----------------------------------------\n"
        ticket_str += f" Mode Paiement : {sale['payment_method']}\n"
        if sale['payment_method'] == "Espèces":
            ticket_str += f" Recu          :             {sale['amount_received']:7.2f} €\n"
            ticket_str += f" Rendu         :             {sale['change_returned']:7.2f} €\n"
        ticket_str += "========================================\n"
        ticket_str += "       Historique Archivé / Miaou 🐱    \n"
        ticket_str += "========================================\n"
        
        self.ticket_text.config(state="normal")
        self.ticket_text.delete("1.0", "end")
        self.ticket_text.insert("1.0", ticket_str)
        self.ticket_text.config(state="disabled")


# =====================================================================
# DÉMARRAGE DE L'APPLICATION 🚀
# =====================================================================
if __name__ == "__main__":
    app = CaisseApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
