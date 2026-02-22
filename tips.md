# 🔍 Ohmeals — Audit de Failles & Tips d'Amélioration

> Analyse complète du site Ohmeals : failles de sécurité, vulnérabilités et recommandations.

---

## 🔴 Failles Critiques

### 1. Mot de passe email en clair dans le code source
**Fichier** : `app/config.py` (ligne 18)
```python
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'oicz kpzi ieak mulf')
```
**Risque** : Le mot de passe d'application Gmail est visible directement dans le code. Quiconque accède au dépôt Git peut compromettre le compte email.

**✅ Tip** : Ne **jamais** mettre de mots de passe en fallback. Utilisez uniquement les variables d'environnement :
```python
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Pas de fallback !
```

---

### 2. Clé secrète Flask faible et prévisible
**Fichier** : `app/config.py` (ligne 9)
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'ohmeals-secret-key-change-in-production')
```
**Risque** : Si la variable d'environnement n'est pas définie, la clé par défaut est devinable. Un attaquant peut **forger des sessions** et se connecter en tant qu'admin.

**✅ Tip** : Générez une clé aléatoire forte et ne mettez aucun fallback :
```python
SECRET_KEY = os.environ['SECRET_KEY']  # Crash si absente = sécurité intentionnelle
```
Générer une clé : `python -c "import secrets; print(secrets.token_hex(32))"`

---

### 3. Identifiants admin par défaut exposés
**Fichier** : `app/__init__.py` (lignes 75-77)
```python
admin_user = os.environ.get('ADMIN_USER', 'admin')
admin_email = os.environ.get('ADMIN_EMAIL', 'admin@ohmeals.com')
admin_pass = os.environ.get('ADMIN_PASSWORD', 'OhMeals2024!')
```
**Risque** : N'importe qui peut se connecter avec `admin / OhMeals2024!` si les variables d'environnement ne sont pas configurées.

**✅ Tip** : Supprimez les fallback et forcez la configuration via `.env`. Ajoutez un check au démarrage :
```python
if not os.environ.get('ADMIN_PASSWORD'):
    raise RuntimeError("ADMIN_PASSWORD non défini ! Configurez vos variables d'environnement.")
```

---

## 🟠 Failles Importantes

### 4. Aucune protection CSRF sur les formulaires
**Fichiers** : `login.html`, `forgot_password.html`, `book.html`

**Risque** : Sans token CSRF, un site malveillant peut forcer un utilisateur connecté à effectuer des actions (modifier son mot de passe, créer des commandes...).

**✅ Tip** : Intégrez **Flask-WTF** :
```bash
pip install flask-wtf
```
```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)
```
Ajoutez `{{ csrf_token() }}` dans chaque formulaire HTML.

---

### 5. Aucun rate limiting (login + mot de passe oublié)
**Fichiers** : `auth_controller.py` — routes `/login` et `/forgot-password`

**Risque** : Un attaquant peut tester des milliers de mots de passe par **brute force** sans être bloqué. Le seul rate limit existant (60s sur le code de reset) est insuffisant.

**✅ Tip** : Utilisez **Flask-Limiter** :
```python
from flask_limiter import Limiter
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login(): ...
```

---

### 6. Code de réinitialisation trop faible
**Fichier** : `auth_controller.py` (ligne 107)
```python
code_generated = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
```
**Risques** :
- Seulement **5 caractères** = facile à deviner par brute force
- Utilise `random` au lieu de `secrets` (pas cryptographiquement sûr)
- **Aucune expiration** du code (un code reste valide indéfiniment)

**✅ Tips** :
```python
import secrets
code_generated = secrets.token_urlsafe(16)  # Token sécurisé de 16 bytes
# + Ajouter un champ `reset_code_expires_at` dans le modèle Admin
# + Vérifier l'expiration (ex: 15 minutes max)
```

---

### 7. Endpoint `/order` public sans aucune protection
**Fichier** : `menu_controller.py` (ligne 80)

**Risques** :
- Pas d'authentification → n'importe qui peut créer des commandes
- Pas de **rate limiting** → un bot peut spammer des milliers de fausses commandes
- Pas de **validation du numéro de téléphone**
- Pas de **CAPTCHA** ou vérification humaine
- Le **prix est envoyé par le client** (ligne 105) → un client peut modifier le prix à 0 !

**✅ Tips** :
- Ajouter un rate limit (`5-10 commandes/heure/IP`)
- Valider le format du téléphone côté backend
- **Recalculer le prix côté serveur** à partir de la base de données, ne jamais faire confiance au prix envoyé par le client
- Ajouter un CAPTCHA (ex: reCAPTCHA v3)

---

### 8. Erreurs internes exposées au client
**Fichier** : `menu_controller.py` (ligne 153)
```python
return jsonify({'error': f'Erreur lors de la création: {str(e)}'}), 500
```
**Risque** : Les messages d'erreur Python sont envoyés directement au client, ce qui peut révéler des détails sur la structure de la base de données, les chemins de fichiers, etc.

**✅ Tip** : Loguez l'erreur en interne, renvoyez un message générique :
```python
import logging
logging.error(f"Order creation failed: {str(e)}")
return jsonify({'error': 'Une erreur est survenue. Veuillez réessayer.'}), 500
```

---

### 9. XSS potentiel dans le panier (innerHTML)
**Fichier** : `static/js/cart.js` (lignes 126-143)
```javascript
row.innerHTML = `<strong>${item.name}</strong>...`;
```
**Risque** : Si un nom de produit contient du JavaScript malveillant injecté en base, il sera exécuté dans le navigateur de tous les visiteurs (**Stored XSS**).

**✅ Tip** : Utilisez `textContent` au lieu de `innerHTML` pour les données dynamiques, ou échappez le HTML :
```javascript
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

---

## 🟡 Failles Modérées

### 10. Pas de headers de sécurité HTTP
**Risque** : Le site ne définit aucun header de sécurité, ce qui le rend vulnérable au clickjacking, au sniffing MIME, etc.

**✅ Tip** : Ajoutez ces headers via un `@app.after_request` :
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
```

---

### 11. Pas de verrouillage de compte après échecs de connexion
**Fichier** : `auth_controller.py`

**Risque** : Un attaquant peut tester des combinaisons infiniment sans être bloqué.

**✅ Tip** : Ajoutez un compteur `failed_login_attempts` dans le modèle `Admin`. Après 5 échecs, bloquez le compte pendant 15 minutes.

---

### 12. Session Flask sans durée de vie limitée
**Risque** : Une session volée (ex: via un réseau non sécurisé) peut être utilisée indéfiniment.

**✅ Tip** :
```python
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS uniquement
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

### 13. Pas de validation des images produit
**Fichier** : `api_controller.py` — Endpoint `POST /api/products`

**Risque** : Le champ `image` accepte n'importe quelle URL, ce qui permet de stocker des liens vers des contenus malveillants.

**✅ Tip** : Validez le format d'image (extensions autorisées), ou mieux, uploadez les images localement avec un système de validation MIME.

---

### 14. SQLite en production
**Fichier** : `config.py` (ligne 31)
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///traiteur.db')
```
**Risque** : SQLite ne gère pas bien les accès concurrents et n'est pas fait pour la production.

**✅ Tip** : Migrez vers **PostgreSQL** ou **MySQL** pour la production :
```
DATABASE_URL=postgresql://user:pass@localhost/ohmeals
```

---

### 15. API admin sans gestion de rôles
**Fichier** : `api_controller.py`

**Risque** : N'importe quel admin peut supprimer d'autres admins, y compris le super-admin. Il n'y a aucun système de permissions.

**✅ Tip** : Ajoutez un champ `role` (`superadmin`, `admin`, `editor`) dans le modèle `Admin` et vérifiez les permissions avant chaque action sensible.

---

## 🔵 Améliorations & Bonnes Pratiques

### 16. Ajouter du logging structuré
Aucun système de logs n'existe. En cas d'incident, il n'y a aucune trace.

**✅ Tip** : Configurez le logging Python :
```python
import logging
logging.basicConfig(
    filename='ohmeals.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
```

---

### 17. Ajouter des tests unitaires
Aucun test n'existe actuellement. Chaque modification risque de casser le site sans que personne ne s'en rende compte.

**✅ Tip** : Créez un dossier `tests/` avec `pytest` et testez au minimum :
- La connexion/déconnexion admin
- La création de commandes
- Les validations d'entrée

---

### 18. Le footer de `login.html` est statique (non-dynamique)
**Fichier** : `login.html` (lignes 142-197)

Le footer du login utilise des données statiques ("demo@gmail.com", "Feane") au lieu des `site_settings` dynamiques comme le reste du site.

**✅ Tip** : Remplacez par `{% include 'includes/footer.html' %}` comme sur les autres pages.

---

### 19. Pas de validation email côté frontend
**Fichier** : `book.html` — le champ email n'a pas d'attribut `type="email"` avec validation robuste.

**✅ Tip** : Ajoutez une validation JavaScript du format email avant soumission.

---

### 20. Le `remember_me` de login ne fait rien
**Fichier** : `login.html` (ligne 125) — la checkbox "Remember Me" est affichée mais jamais envoyée au backend.

**✅ Tip** :
```python
remember = request.form.get('remember_me') == 'on'
login_user(user, remember=remember)
```

---

## 📊 Résumé des Priorités

| Priorité | Faille | Impact |
|----------|--------|--------|
| 🔴 P0 | Mot de passe email en clair | Compromission du compte email |
| 🔴 P0 | Clé secrète faible | Forge de sessions admin |
| 🔴 P0 | Identifiants admin par défaut | Accès non autorisé |
| 🟠 P1 | Pas de CSRF | Actions forcées sur l'admin |
| 🟠 P1 | Pas de rate limiting | Brute force login |
| 🟠 P1 | Prix côté client | Commandes à prix modifié |
| 🟠 P1 | Code de reset faible | Prise de contrôle du compte |
| 🟡 P2 | Headers de sécurité manquants | Clickjacking, XSS |
| 🟡 P2 | XSS dans le panier | Exécution de code malveillant |
| 🟡 P2 | SQLite en production | Performance & fiabilité |
| 🔵 P3 | Logging, tests, rôles | Maintenabilité & robustesse |

---

> 💡 **Recommandation globale** : Commencez par les failles **P0** (1 jour de travail), puis passez aux **P1** (2-3 jours). Les P2/P3 peuvent être planifiés sur 1-2 semaines.
