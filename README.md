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

## 📁 Structure du projet

```
OHMEALS/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── dashboard/
│   │   └── login.html (seul fait)
│   ├── index.html
│   ├── about.html
│   ├── menu.html (statique)
│   ├── book.html (statique)
│   ├── forgot_password.html
│   └── password_changed.html
├── app.py
├── models.py (à compléter)
└── requirements.txt
```

---

## ✅ Fonctionnalités déjà faites

- Template Bootstrap 5 adapté ✓
- Pages frontend prêtes (index, about, menu statique, book statique, login client/admin) ✓
- Login pour le dashboard admin ✓
- Backend Flask basique avec routes et auth ✓

---

## ⏳ Fonctionnalités à venir (prioritaires)

1. **Créer la base de données**

   - Définir les modèles : Produits (nom, description, prix, unité, type), Commandes, Utilisateurs.
   - Créer les relations nécessaires pour CRUD et calcul des prix.

2. **Adapter le menu (`menu.html`)**

   - Séparer snacks (kilo/pièce) et plats (personne).
   - Afficher clairement les unités et prix.
   - Préparer le menu pour qu’il soit dynamique via Flask/Jinja2.

3. **Adapter le formulaire de réservation (`book.html`)**

   - Formulaire dynamique selon produit et unité.
   - Calcul automatique du prix total côté frontend et backend.

4. **Créer le dashboard admin complet avec React**

   - Pages : products, orders, users, stats, settings.
   - CRUD complet pour produits et commandes.
   - Affichage dynamique et filtres.

5. **Sécurisation des routes et sessions**

---

## Module 1 : Frontend - Pages publiques

### Étape 1.1 : Intégration du template Bootstrap 5

**Explication :** Template téléchargé et adapté aux couleurs marocaines. Préparé pour injecter des données dynamiques via Flask.
**Backend :** Prévoir `id`/`class` clairs pour Jinja2.
**Tips :** Commenter blocs réutilisables et garder composants modulaires.

### Étape 1.2 : Pages index, about, menu, book, login

**Explication :** Pages créées, menu et book statiques pour l’instant.
**Backend :** Préparer placeholders pour produits et prix dynamiques.
**Tips :** Tester dans navigateur et inclure header/footer via `{% include %}`.

---

## Module 2 : Backend - Structure Flask

### Étape 2.1 : Mise en place de app.py

**Explication :** Routes principales créées, login et auth basique implémentés.
**Backend :** Prévoir routes dynamiques pour menu, book et dashboard.
**Tips :** Séparer routes publiques et admin, utiliser `url_for`.

### Étape 2.2 : Base de données (à faire)

**Explication :** SQLite + SQLAlchemy à créer.
**Backend :** Définir modèles Produits, Commandes, Utilisateurs avec unités et relations.
**Tips :** Penser contraintes métier : plat → personne, snack → kilo/pièce.

---

## Module 3 : Dashboard Admin

### Étape 3.1 : Login admin

**Explication :** Login fonctionnel pour accéder au dashboard.
**Backend :** Routes sécurisées pour login avec hash de mot de passe.
**Tips :** Utiliser Flask-Login pour sessions et sécurité.

### Étape 3.2 : Création du dashboard complet avec React (à faire)

**Explication :** Pages : products, orders, users, stats, settings à créer.
**Backend :** CRUD complet pour produits et commandes avec React.
**Tips :** Commencer avec données tests, ensuite connecter DB réelle.

---

## Module 4 : Logique métier - Produits et commandes

### Étape 4.1 : Définition unités de vente

**Explication :** Snacks au kilo/pièce, plats par personne.
**Backend :** Stocker unité et quantité en DB. Formulaire dynamique book.html à venir.
**Tips :** Vérifier calcul `prix_total = prix_unitaire × quantité`, valider côté backend et frontend.

---

## Module 5 : Mise en production et sécurité

### Étape 5.1 : Authentification et sessions

**Explication :** Login admin fonctionnel.
**Backend :** Prévoir sécurisation de toutes les routes admin.
**Tips :** Ne jamais stocker mots de passe en clair, utiliser `Flask-Login`.

### Étape 5.2 : Tests et validation

**Explication :** Tester pages client/admin, affichage prix et unités, dashboard dynamique à compléter.
**Tips :** Commencer avec données fictives, ajouter logs backend pour suivre erreurs.

---

## Module 6 : Conseils généraux pour le projet

- Avancer **module par module**, ne pas tout faire d’un coup.
- Réfléchir à la **logique métier** avant de coder.
- Tester après chaque étape côté client et côté admin.
- Documenter toutes les décisions importantes.
- Préparer CSS/JS réutilisables.
- Anticiper erreurs avec validations frontend et backend.

---

## 💰 Logique métier - Unités de vente

| Type produit | Unité    | Exemple affichage | Prix calculé         |
| ------------ | -------- | ----------------- | -------------------- |
| Snack        | kilo     | 20 DT / kilo      | Prix × quantité (kg) |
| Snack        | pièce    | 2 DT / pièce      | Prix × nombre pièces |
| Plat         | personne | 30 DT / personne  | Prix × nombre pers.  |

---

## 📞 Contact

- Contribuer : créer une pull request
- Signaler un bug : ouvrir une issue

---

💡 **Conseil pour Anes :**
Priorité actuelle :
1️⃣ Créer la base de données.
2️⃣ Adapter le menu et le formulaire dynamique.
3️⃣ Créer le dashboard complet avec React.

Une fois ces étapes faites, le reste (calcul des prix, sécurisation, tests) sera beaucoup plus simple.
