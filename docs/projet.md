# Documentation du Projet OHMEALS

## 1. Introduction
OHMEALS est une application web pour un traiteur marocain. Elle combine une interface vitrine pour les clients et un tableau de bord d'administration pour la gestion des commandes et produits.

**État Actuel** : Prototype Fonctionnel (MVP).
**Dernière mise à jour de l'analyse** : 07 Février 2026.

---

## 2. Analyse de l'État Actuel

### ✅ Ce qui est fait et fonctionnel
*   **Architecture Backend** : Flask structuré avec Blueprints (MVC), SQLAlchemy configuré.
*   **Modèles de Données** : `Product` (avec variantes), `Order`, `Admin`, `OrderItem` sont définis.
*   **API REST** : Endpoints clés pour le dashboard (`/api/products`, `/api/orders`, `/api/stats`) sécurisés avec authentification.
*   **Frontend Public (Vitrine)** : Pages `Home`, `Menu` (dynamique), `About` implémentées.

### ⚠️ Problèmes Identifiés & Points d'Attention
1.  **Système de Commande (EN COURS DE REFONTE)** :
    *   La page `book.html` actuelle (Réservation de table) est obsolète.
    *   **Nouveau besoin** : Transformer cette page en **Panier (Cart)** avec un popup de commande finale.
2.  **Dashboard** : Prototype fonctionnel en un seul fichier (à optimiser plus tard).

---

## 3. Feuille de Route (Roadmap)

### Étape 1 : Implémentation du Panier (Priorité Haute) �
*   **Menu** : Ajouter les boutons "Ajouter au panier" en JavaScript.
*   **Page Panier (`book.html`)** :
    *   Supprimer l'ancien formulaire de réservation.
    *   Afficher le tableau des articles choisis (via `localStorage`).
*   **Checkout** : Créer un **Popup** (Modale) au clic sur "Commander" pour saisir Nom, Tel, Adresse.
*   **Backend** : Créer l'endpoint de réception de commande JSON.

### Étape 2 : Optimisation Dashboard
*   Séparer le code React pour une meilleure maintenabilité.

### Étape 4 : Déploiement
*   Profiter de la légèreté de SQLite pour un déploiement, ou migrer vers PostgreSQL pour plus de robustesse.
*   Configurer Gunicorn (serveur de prod) au lieu de `run.py`.

---

## 4. Architecture Technique

### Backend (Flask)
*   `app/models` : Données (SQLAlchemy).
*   `app/controllers` : Logique.
    *   `api_controller.py` : Sert le JSON pour le Dashboard (Admin).
    *   `menu_controller.py` : Sert le HTML pour le Site Public (Client).
*   `app/templates` : Vues Jinja2.

### Frontend
*   **Public** : HTML5 + Bootstrap 5 + jQuery (Formulaires, Modales).
*   **Admin** : React 18 (Embedded) + API Fetch.

## 5. Comment Lancer le Projet

1.  **Installation** :
    ```bash
    pip install -r requirements.txt
    ```
2.  **Base de données** :
    ```bash
    python scripts/init_db.py
    ```
3.  **Lancement** :
    ```bash
    python run.py
    ```
    Accès : `http://127.0.0.1:5000`

---
*Ce document sert de référence unique pour le développement futur.*
