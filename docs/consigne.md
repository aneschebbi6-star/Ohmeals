
# Consignes et Pistes d'Amélioration pour OHMEALS

Ce document recense l'analyse de l'état actuel du projet et propose des axes d'amélioration techniques et fonctionnels.

## 1. Analyse de l'Existant (État des Lieux)

### Points Forts
- **Architecture Claire** : Séparation MVC (Models, Controllers, Templates) respectée.
- **Dashboard Réactif** : Interface administrative moderne en React intégré.
- **Fonctionnalités Clés** : Gestion produits, commandes, et paramètres dynamiques opérationnels.
- **Mesures d'urgence** : Capacité à désactiver des modules défaillants (ex: `City`).

### Points Faibles & Carences
- **Dette Technique** : Le module `City` a été désactivé suite à des erreurs, rendant la gestion des frais de livraison statique ou inexistante.
- **Frontend Admin** : Le code React est contenu dans un seul fichier HTML (`dashboard.html`), ce qui le rend difficile à maintenir à long terme.
- **Base de Données** : Utilisation de SQLite, parfait pour le dév mais limité pour la production (concurrence, backups).
- **Sécurité** : Pas de CSRF protection explicite sur les formulaires AJAX dashboard (bien que Flask-WTF soit peut-être installé, il n'est pas utilisé partout).

---

## 2. Pistes d'Amélioration (Par Priorité)

### 🔴 Priorité Haute (Critique)

1.  **Réparer le Module Ville (`City`)**
    -   *Pourquoi ?* Pour gérer les frais de livraison dynamiques par zone.
    -   *Action* : Réintégrer proprement le modèle `City` et ses relations avec `Order`.

2.  **Validation des Données**
    -   *Pourquoi ?* Éviter les commandes incomplètes ou les erreurs serveur.
    -   *Action* : Ajouter des validateurs (marshmallow ou pydantic) sur les entrées API (`api_controller.py`).

3.  **Sécurité des API**
    -   *Pourquoi ?* Protéger les endpoints administration.
    -   *Action* : Vérifier que `@login_required` est présent sur TOUTES les routes `/api`. Ajouter un Rate Limiting.

### 🟡 Priorité Moyenne (Fonctionnel)

4.  **Expérience Client (Frontend)**
    -   **Panier AJAX** : Rendre l'ajout au panier instantané sans rechargement de page.
    -   **Suivi de Commande** : Page pour permettre au client de voir le statut (En préparation, Livré...) via son numéro de téléphone ou un lien unique.

5.  **Refonte du Code Dashboard**
    -   *Action* : Extraire les composants React (`Sidebar`, `ProductManager`, `SettingsManager`...) dans des fichiers `.js` ou `.jsx` séparés et utiliser un bundler (Vite/Webpack) ou continuer avec l'approche CDN mais en divisant les fichiers.

6.  **Notifications**
    -   *Action* : Envoyer un email automatique au client et à l'admin lors d'une nouvelle commande (via Flask-Mail ou SendGrid).

### 🟢 Priorité Basse (Confort & Performance)

7.  **Optimisation des Images**
    -   *Action* : Redimensionner et compresser les images uploadées par l'admin (actuellement stockées en Base64 ou brut, ce qui peut alourdir la BDD). Passer au stockage fichier (AWS S3 ou dossier `static/uploads`).

8.  **SEO & Analytics**
    -   *Action* : Ajouter `sitemap.xml`, `robots.txt` et des balises OpenGraph dynamiques pour le partage social.

---

## 3. Workflow de Développement Suggéré

Pour les prochaines sessions de développement :

1.  **Branche Git** : Toujours créer une branche par fonctionnalité (ex: `feature/fix-city-model`).
2.  **Tests** : Écrire des tests unitaires simples (`pytest`) pour les modèles avant de coder les contrôleurs.
3.  **Documentation** : Mettre à jour `docs/projet.md` à chaque changement majeur d'architecture.
