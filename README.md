# OHMEALS - Traiteur Marocain 🇲🇦

Application web pour un traiteur marocain, construite avec **Flask MVC** et **Bootstrap 5**.

---

## 🚀 Démarrage Rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Initialiser la base de données
python scripts/init_db.py

# 3. Lancer l'application
python run.py

# 4. Accéder à http://127.0.0.1:5000
```

### 🔐 Identifiants Admin
| Champ | Valeur |
|-------|--------|
| Username | `anes` |
| Password | `anes123` |

---

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+, Flask 2.x, SQLAlchemy |
| Frontend Public | Bootstrap 5, Jinja2, JavaScript |
| Dashboard Admin | React 18 (embedded) |
| Base de données | SQLite |

---

## 📁 Architecture du Projet (MVC)

```
OHMEALS/
├── app/                          # 📦 Package Flask principal
│   ├── __init__.py               # Application Factory
│   ├── config.py                 # Configurations (Dev/Prod)
│   ├── extensions.py             # SQLAlchemy, LoginManager
│   ├── models/                   # 🗃️ Model (M)
│   │   ├── admin.py              # Modèle Admin/User
│   │   ├── product.py            # Modèle Product + Variants
│   │   └── order.py              # Modèles Order + OrderItem
│   └── controllers/              # 🎮 Controller (C)
│       ├── page_controller.py    # Routes: /, /about
│       ├── auth_controller.py    # Routes: /login, /logout
│       ├── menu_controller.py    # Routes: /menu, /book, /order
│       └── api_controller.py     # API REST: /api/*
│
├── templates/                    # 🎨 View (V) - Jinja2 + Bootstrap
│   ├── index.html                # Page d'accueil
│   ├── about.html                # À propos
│   ├── menu.html                 # Menu dynamique
│   ├── book.html                 # 🛒 Panier + Checkout
│   ├── login.html                # Connexion admin
│   └── dashboard/
│       └── dashboard.html        # Dashboard React
│
├── static/                       # 📂 Assets
│   ├── css/
│   ├── js/
│   │   ├── cart.js               # 🛒 Gestion panier (localStorage)
│   │   ├── menu.js               # Logique menu + modal
│   │   └── custom.js
│   └── images/
│
├── instance/                     # 🗄️ Base de données
│   └── ohmeals.db
│
├── docs/                         # 📚 Documentation
│   └── projet.md
│
├── run.py                        # 🚀 Point d'entrée
└── README.md
```

---

## ✅ Fonctionnalités

### 🌍 Partie Client (Site Public)
- [x] Menu dynamique avec filtrage par catégorie (Snacks, Plats, Salades)
- [x] Tri par prix et par goût (Salé/Sucré)
- [x] Modal produit avec sélection de variantes
- [x] **Panier (localStorage)** - Icône avec badge dynamique
- [x] **Checkout** - Sélection ville (Tunis, Ariana, Ben Arous) & Validation zone
- [x] Soumission de commande vers le backend

### ⚙️ Partie Admin (Dashboard)
- [x] Authentification admin
- [x] Gestion produits (CRUD avec variantes)
- [x] Gestion commandes (Vue détaillée produits)
- [x] **Facturation** - Génération PDF/Impression factures
- [x] **Sécurité** - Modification restreinte (Statut uniquement)
- [x] Statistiques de vente (Revenu total réel)

---

## 🔌 API REST

| Endpoint | Méthodes | Description |
|----------|----------|-------------|
| `/api/products` | GET, POST | Liste/Créer produits |
| `/api/products/<id>` | PUT, DELETE | Modifier/Supprimer |
| `/api/orders` | GET, POST | Liste/Créer commandes |
| `/api/orders/<id>` | PUT, DELETE | Modifier/Supprimer |
| `/api/stats` | GET | Statistiques dashboard |
| `/order` | POST | Création commande (public) |

---

## 📊 Logique Métier

### Unités de vente

| Type | Unité | Exemple | Calcul |
|------|-------|---------|--------|
| Snack | kilo | 20 DT/kg | Prix × kg |
| Snack | pièce | 2 DT/pièce | Prix × quantité |
| Plat | personne | 30 DT/pers | Prix × personnes |

---

## 🧠 Modèles de Données

### Product
```
id, name, description, category, taste, image, is_active
```

### ProductVariant
```
id, product_id, variant_name, unit, price, is_default, is_available, position
```

### Order
```
id, customer_name, customer_phone, customer_email, delivery_address, total_price, status, created_at
```

### OrderItem
```
id, order_id, product_id, quantity, unit, price
```

---

## 📞 Contact

- **Contribuer** : créer une pull request
- **Bug** : ouvrir une issue

---

*Built with ❤️ by ANES*
