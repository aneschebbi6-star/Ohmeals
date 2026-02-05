<<<<<<< HEAD
# OHMEALS - Traiteur Marocain

## Introduction

OHMEALS est un projet web pour un traiteur marocain, construit avec Flask et Bootstrap 5.
Le projet se concentre sur une expérience utilisateur claire pour les clients et une interface admin complète pour le traiteur.
Ce document combine le **business understanding**, les **objectifs**, les **modules de développement**, et des **conseils pratiques**.

---

## 📊 Business Understanding

**OHMEALS propose :**

- **Snacks** : vendus au kilo (briouates, pâtisseries) ou à la pièce (mini-sandwichs).
- **Plats** : vendus par personne (tajine, couscous, rfissa).

**Utilisateurs :**

- **Clients** : veulent commander facilement, comprendre les prix selon l’unité, et passer commande rapidement.
- **Admin** : veut gérer efficacement les produits, commandes et utilisateurs, et accéder à des statistiques claires.

**Workflow :**

1. Client consulte le menu → choisit produits → remplit formulaire → soumet.
2. Admin reçoit la commande → prépare → facture → archive.
3. Prix calculé automatiquement selon l’unité et la quantité.

**Règles métier :**

- Snacks → vendu **au kilo ou à la pièce**, jamais par personne.
- Plats → vendu **par personne**, jamais au kilo.
- Affichage et calcul des prix toujours clairs et transparents.
- Formulaire dynamique selon type de produit choisi.

---

## 🎯 Objectifs du projet

- Adapter le frontend aux unités de vente.
- Créer et connecter la base de données (SQLite + SQLAlchemy).
- Rendre le menu et le formulaire de réservation dynamiques.
- Créer le dashboard admin complet avec **React**.
- Calcul automatique des prix selon l’unité et quantité.
- Réservation et suivi des commandes complet.
- Sécurisation des routes et sessions.

---

## 🛠️ Technologies prévues

- Python 3.11+
- Flask 2.x
- SQLite + SQLAlchemy
- Bootstrap 5
- React 18+
- Jinja2 Templates
- HTML5, CSS3, JS (Vanilla)

---

# OHMEALS - Traiteur Marocain 🇲🇦

Application web pour un traiteur marocain, construite avec **Flask MVC** et **Bootstrap 5**.

---

## 🛠️ Technologies

| Composant | Technologie |
|-----------|-------------|
| Backend | Python 3.11+, Flask 2.x, SQLAlchemy |
| Frontend Public | Bootstrap 5, Jinja2 |
| Dashboard Admin | React 18+ |
| Base de données | SQLite |

---

## 📁 Architecture du Projet (MVC)

```
OHMEALS/
├── app/                          # 📦 Package Flask principal
│   ├── __init__.py               # Application Factory
│   ├── config.py                 # Configurations (Dev/Prod)
│   ├── extensions.py             # SQLAlchemy, LoginManager, Mail
│   ├── models/                   # 🗃️ Model (M)
│   │   ├── admin.py              # Modèle Admin/User
│   │   ├── product.py            # Modèle Product
│   │   └── order.py              # Modèles Order + OrderItem
│   └── controllers/              # 🎮 Controller (C)
│       ├── page_controller.py    # Routes: /, /about
│       ├── auth_controller.py    # Routes: /login, /logout
│       ├── menu_controller.py    # Routes: /menu, /book
│       └── api_controller.py     # API REST: /api/*
│
├── templates/                    # 🎨 View (V) - Jinja2 + Bootstrap
│   ├── index.html
│   ├── about.html
│   ├── menu.html
│   ├── book.html
│   ├── login.html
│   ├── forgot_password.html
│   └── dashboard/
│       └── dashboard.html        # Dashboard React
│
├── static/                       # 📂 Assets
│   ├── css/
│   ├── js/
│   ├── fonts/
│   └── images/
│
├── scripts/                      # 🔧 Scripts utilitaires
│   └── init_db.py
│
├── instance/                     # 🗄️ Base de données
│   └── ohmeals.db
│
├── run.py                        # 🚀 Point d'entrée
├── requirements.txt              # 📋 Dépendances
└── README.md
>>>>>>> 303c522 (Refactor complet OHMEALS : nouvelles pages, dossiers et JS mis à jour)
```

---


=======
## 🚀 Démarrage Rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Lancer l'application
python run.py

# 3. Accéder à http://127.0.0.1:5000
```

### 🔐 Identifiants Admin
| Champ | Valeur |
|-------|--------|
| Username | `anes` |
| Password | `anes123` |

---

## 📊 Logique Métier

### Unités de vente

| Type | Unité | Exemple | Calcul |
|------|-------|---------|--------|
| Snack | kilo | 20 DT/kg | Prix × kg |
| Snack | pièce | 2 DT/pièce | Prix × quantité |
| Plat | personne | 30 DT/pers | Prix × personnes |

---

## 🔌 API REST

| Endpoint | Méthodes | Description |
|----------|----------|-------------|
| `/api/products` | GET, POST | Liste/Créer produits |
| `/api/products/<id>` | PUT, DELETE | Modifier/Supprimer |
| `/api/orders` | GET, POST | Liste/Créer commandes |
| `/api/orders/<id>` | PUT, DELETE | Modifier/Supprimer |
| `/api/admins` | GET, POST | Liste/Créer admins |
| `/api/stats` | GET | Statistiques |

---

## 🧠 Modèles de Données

### Admin
```
id, username, email, password, reset_code
```

### Product
```
id, name, description, category, unit, price, image, is_active
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

## ✅ Fonctionnalités

- [x] Architecture MVC avec Blueprints
- [x] Application Factory pattern
- [x] API REST pour React Dashboard
- [x] Authentification admin
- [x] Templates Bootstrap 5 dynamiques
- [x] Dashboard React intégré
- [x] Gestion produits (CRUD)
- [x] Gestion commandes (CRUD)


---

## 📞 Contact

- **Contribuer** : créer une pull request
- **Bug** : ouvrir une issue

---

*Built with ❤️ by ANES*
