# Documentation du Projet OHMEALS

## 1. Introduction
OHMEALS est une application web complète pour un traiteur marocain ("**ohmeals*"). Elle offre une interface client intuitive pour découvrir les menus et passer commande, ainsi qu'une interface d'administration puissante pour la gestion quotidienne de l'activité.

## 2. Architecture du Projet
Le projet repose sur une architecture **MVC (Modèle-Vue-Contrôleur)**, garantissant une séparation claire entre les données, l'interface utilisateur et la logique métier.

### Structure des Dossiers
*   **`app/`** : Cœur de l'application Flask.
    *   **`models/`** : Définition des schémas de base de données (Produits, Commandes, Utilisateurs) avec SQLAlchemy.
    *   **`controllers/`** : Gère les requêtes HTTP, la logique métier et les API REST.
    *   **`__init__.py`** : Configuration de l'application (Factory Pattern).
*   **`templates/`** : Vues HTML générées par Jinja2 pour le frontend public.
*   **`static/`** : Ressources statiques (Feuilles de style CSS, Scripts JavaScript, Images).
*   **`react-dashboard/`** : Code source du tableau de bord administrateur (Single Page Application en React).
*   **`instance/`** : Contient la base de données SQLite (`ohmeals.db`).
*   **`docs/`** : Documentation du projet.

## 3. Technologies Utilisées

### Backend (Serveur)
*   **Python 3.11+** : Langage principal.
*   **Flask 2.x** : Framework web léger et flexible.
*   **SQLAlchemy** : ORM pour l'interaction avec la base de données.
*   **SQLite** : Base de données relationnelle légère (fichier local).

### Frontend (Client Public)
*   **HTML5 / CSS3** : Structure et mise en page.
*   **Bootstrap 5** : Framework CSS pour un design responsive et moderne.
*   **Jinja2** : Moteur de templates pour l'affichage dynamique des données.
*   **JavaScript (Vanilla + jQuery)** : Interactivité (filtres, modales, animations).

### Frontend (Admin Dashboard)
*   **React 18+** : Bibliothèque JS pour l'interface d'administration.
*   **API REST** : Communication avec le backend Flask pour les données (CRUD).

## 4. Fonctionnalités Clés

### 🌍 Partie Client (Site Web Public)
1.  **Catalogue & Menu** :
    *   Affichage dynamique des produits.
    *   Filtrage instantané par catégorie (Snacks, Plats, Salades).
    *   Tri des produits par prix et par profil gustatif (Salé/Sucré).
2.  **Expérience Utilisateur** :
    *   Design responsive (mobile-first).
    *   Fenêtre modale (Pop-up) pour les détails produits.
3.  **Système de Commande** :
    *   Gestion des variantes de produits (Vente au Kilo, à la Pièce, par Personne).
    *   Sélection des quantités avec calcul de prix en temps réel.
4.  **Réservation** :
    *   Module de réservation de table en ligne.

### ⚙️ Partie Administrateur (Privée)
1.  **Gestion des Produits** : Ajouter, modifier, supprimer des articles du menu. Gestion des images et des stocks.
2.  **Gestion des Commandes** : Visualiser les nouvelles commandes, traiter les statuts (En préparation, Livré).
3.  **Utilisateurs** : Gestion des comptes administrateurs.
4.  **Statistiques** : Suivi des performances de vente.

## 5. Modèles de Données Principaux

*   **Product (Produit)** : Représente un article du menu (Nom, Description, Prix, Unité, Image, Catégorie).
*   **Order (Commande)** : Contient les infos client et la liste des produits commandés.
*   **User (Admin)** : Comptes pour l'accès au tableau de bord.

## 6. Installation et Lancement

Pour lancer le projet localement :

1.  **Installation des dépendances** :
    ```bash
    pip install -r requirements.txt
    ```

2.  **Initialisation de la Base de Données** :
    ```bash
    python scripts/init_db.py
    ```

3.  **Démarrage du Serveur** :
    ```bash
    python run.py
    ```
    L'application sera accessible sur `http://127.0.0.1:5000`.
