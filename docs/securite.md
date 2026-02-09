
# Audit de Sécurité et Recommandations - OHMEALS

Ce document présente l'analyse de sécurité effectuée sur l'application OHMEALS et propose des mesures correctives classées par criticité.

## 🚨 1. Failles Critiques (À CORRIGER IMMÉDIATEMENT)

### 1.1. Identifiants Hardcodés
- **Problème** : Le fichier `app/__init__.py` contient la création automatique d'un admin avec `username='anes'` et une réponse de mail hardcodée.
- **Risque** : Si le code est partagé ou accessible, n'importe qui peut se connecter.
- **Solution** :
    - Utiliser des variables d'environnement (`os.environ.get`) pour le mot de passe admin initial.
    - Ne créer l'admin par défaut que si la table est vide, et forcer le changement de mot de passe à la première connexion.

### 1.2. Mots de passe en clair dans `config.py`
- **Problème** : `MAIL_PASSWORD` est écrit en clair dans le code source.
- **Risque** : Compromission du compte Gmail utilisé pour l'envoi des mails.
- **Solution** :
    - Déplacer ces secrets dans un fichier `.env` qui n'est **jamais** commité sur Git.
    - Utiliser `python-dotenv` pour charger ces variables.

### 1.3. Secret Key par défaut
- **Problème** : `SECRET_KEY` a une valeur par défaut publique.
- **Risque** : Un attaquant peut signer ses propres cookies de session et devenir admin.
- **Solution** : Générer une clé aléatoire forte en production (`openssl rand -hex 32`).

---

## ⚠️ 2. Risques Élevés (Priorité Haute)

### 2.1. Protection CSRF (Cross-Site Request Forgery)
- **Problème** : Les endpoints API (`/api/*`) utilisent l'authentification par session (cookies) mais ne semblent pas vérifier de token CSRF ou d'en-tête spécifique (comme `X-Requested-With`).
- **Risque** : Un attaquant peut inciter un admin connecté à visiter une page malveillante qui modifie les paramètres ou supprime des produits à son insu.
- **Solution** :
    - Utiliser `Flask-WTF` avec `CSRFProtect`.
    - Pour les appels AJAX (Dashboard), inclure le token CSRF dans les headers (`X-CSRFToken`).

### 2.2. Absence de Rate Limiting (Limitation de débit)
- **Problème** : L'endpoint public `/order` (création de commande) n'a aucune limite.
- **Risque** : Spam de fausses commandes qui remplissent la base de données.
- **Solution** : Installer `Flask-Limiter` et limiter `/order` à (par exemple) 5 requêtes par minute par IP.

---

## 🔸 3. Risques Moyens (Améliorations)

### 3.1. Énumération des Utilisateurs
- **Problème** : La page "Mot de passe oublié" renvoie "EMAIL_NOT_FOUND".
- **Risque** : Permet à un attaquant de savoir si une adresse email est inscrite ou non.
- **Solution** : Toujours répondre "Si cet email existe, un code a été envoyé", que l'email soit trouvé ou non.

### 3.2. Validation des Entrées (XSS)
- **Problème** : Bien que Jinja2 échappe le HTML par défaut, le Dashboard React affiche des données. Si un attaquant parvient à injecter du script dans un nom de produit (Stored XSS), cela pourrait s'exécuter dans le navigateur de l'admin.
- **Solution** :
    - S'assurer que React échappe tout (c'est le comportement par défaut, sauf usage de `dangerouslySetInnerHTML`).
    - Valider les entrées API côté serveur (interdire les caractères spéciaux `< >` dans les noms).

---

## ✅ 4. Bonnes Pratiques Déjà en Place

- **Hachage des Mots de Passe** : Utilisation de `werkzeug.security.generate_password_hash` (PBKDF2/SHA256).
- **Validation Prix** : Le backend recalcule le prix total des commandes en se basant sur la BDD, empêchant la manipulation des prix côté client.
- **Protection des Routes** : L'accès aux API d'administration est correctement protégé par `@login_required`.

---

## 5. Plan d'Action Suggéré

1.  **Immédiat** : Créer un fichier `.env` pour stocker `MAIL_PASSWORD`, `SECRET_KEY`, et les crédentials admin initiaux. Modifier `config.py` pour lire ce fichier.
2.  **Court Terme** : Installer `Flask-Limiter` pour protéger le formulaire de commande.
3.  **Moyen Terme** : Mettre en place la protection CSRF globale sur l'application.
