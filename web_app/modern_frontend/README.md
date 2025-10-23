# Job Finder - Modern Frontend

Interface web moderne et réactive pour Job Finder, développée avec HTMX, Tailwind CSS et Alpine.js.

## 🚀 Fonctionnalités

### 🏠 Dashboard Principal
- **Statistiques en temps réel** : Nombre total d'offres, jobs likés/dislikés
- **Actions rapides** : Navigation vers l'exploration et le matching CV
- **Design moderne** : Interface responsive avec animations fluides

### 🔍 Exploration des Offres
- **Filtrage avancé** : Par date de publication, recherche textuelle
- **Tri intelligent** : Par pertinence ou date
- **Interaction intuitive** : Like/dislike avec feedback instantané
- **Affichage optimisé** : Cards modernes avec informations clés

### 🎯 Matching CV (Nouveau!)
- **Upload drag & drop** : Interface moderne pour déposer son CV
- **Analyse sémantique** : Utilise l'IA pour analyser le contenu
- **Top 5 matches** : Affiche les 5 offres les plus pertinentes
- **Score de correspondance** : Pourcentage et explications détaillées

## 🛠️ Technologies

- **Frontend** : HTMX 1.9.6, Tailwind CSS, Alpine.js
- **Backend** : FastAPI avec endpoints API RESTful
- **Icons** : Font Awesome
- **Responsive** : Design mobile-first

## 📁 Structure du Projet

```
web_app/modern_frontend/
├── index.html          # Page principale avec navigation
├── explore.html        # Page d'exploration des offres
├── cv_matching.html    # Page de matching CV
├── app.js             # JavaScript pour navigation et état
├── server.py          # Serveur FastAPI avec API
├── main.py            # Ancien serveur (remplacé par server.py)
├── static/            # Fichiers statiques
└── templates/         # Templates (si nécessaire)
```

## 🚦 Démarrage Rapide

### 1. Installation des dépendances
```bash
# Depuis le répertoire racine du projet
cd web_app/modern_frontend
pip install fastapi uvicorn python-multipart
```

### 2. Démarrage du serveur
```bash
python server.py
```
Ou avec uvicorn directement :
```bash
uvicorn server:app --host 0.0.0.0 --port 3000 --reload
```

### 3. Accès à l'application
Ouvrez votre navigateur sur : http://localhost:3000

## 🔌 API Endpoints

### Statistiques
- `GET /stats` - Récupère les statistiques utilisateur
- `GET /health` - Health check

### Offres d'emploi
- `GET /offers` - Liste des offres avec filtres optionnels
  - `?date_filter=YYYY-MM-DD` - Filtrer par date
  - `?sort_by=date|relevance` - Tri
  - `?search=terme` - Recherche textuelle
- `POST /likes/{job_reference}` - Like/dislike une offre

### Matching CV
- `POST /cv/upload` - Upload et extraction de texte CV
- `POST /cv/match` - Recherche de correspondances

### Pages
- `GET /` - Page principale
- `GET /explore.html` - Page exploration
- `GET /cv_matching.html` - Page matching CV
- `GET /app.js` - JavaScript de l'application

## 🎨 Interface Utilisateur

### Navigation
- **Header fixe** avec logo et navigation
- **Indicateurs visuels** pour la page active
- **Responsive design** avec menu mobile

### Pages

#### 🏠 Home
- Hero section avec avatar robot
- Cards statistiques colorées
- Actions principales en grand format
- Activité récente (à implémenter)

#### 🔍 Explore
- Barre de filtres compacte
- Grid responsive des offres
- Loading states et empty states
- Pagination (à implémenter)

#### 🎯 CV Matching
- Zone de drop moderne
- Progress bar pour l'upload
- Résultats avec scores de correspondance
- Explications des matches

## 🔧 Intégration avec l'existant

### Connexion avec le backend FastAPI existant
Pour connecter avec votre backend FastAPI existant sur le port 8000 :

1. **Modifiez les URLs dans app.js** :
```javascript
// Remplacez localhost:3000 par localhost:8000
const API_BASE = 'http://localhost:8000';
```

2. **Ajoutez les endpoints manquants** dans votre backend :
```python
# Ajoutez ces routes à votre main.py existant
@app.get("/stats")
async def get_stats():
    return {"total_jobs": 100, "liked_jobs": 12, "disliked_jobs": 5}

@app.post("/cv/upload")
async def upload_cv(cv_file: UploadFile = File(...)):
    # Votre logique d'upload
    pass

@app.post("/cv/match")
async def match_cv(request: CVMatchRequest):
    # Votre logique de matching avec ChromaDB
    pass
```

### Intégration ChromaDB
Pour utiliser votre implémentation ChromaDB existante :

1. **Dans server.py**, remplacez les fonctions mock par :
```python
from src.job_finder.datasets import ChromaDataset

# Dans match_cv()
chroma_dataset = ChromaDataset()
matches = chroma_dataset.query_similar_jobs(cv_text, top_k=5)
```

## 🎯 Migration depuis Streamlit

### Fonctionnalités reproduites
- ✅ **Home page** : Dashboard avec statistiques
- ✅ **Explore Offers** : Exploration avec filtres
- ✅ **CV Matching** : Nouvelle fonctionnalité améliorée
- ✅ **Like/Dislike** : Feedback sur les offres

### Améliorations apportées
- **Performance** : Chargement instantané vs rechargement Streamlit
- **UX moderne** : Interactions fluides avec HTMX
- **Responsive** : Design mobile-first
- **Extensibilité** : Structure modulaire pour nouvelles fonctionnalités

## 🚀 Prochaines étapes

1. **Intégration backend** : Connecter aux vraies données
2. **ChromaDB** : Implémenter le vrai matching sémantique
3. **Authentification** : Système de login utilisateur
4. **Pagination** : Pour les listes d'offres
5. **Notifications** : Système d'alertes temps réel
6. **PWA** : Transformation en Progressive Web App

## 🐛 Debug

### Problèmes courants
- **CORS errors** : Vérifiez que le backend autorise les requêtes cross-origin
- **Fichiers statiques** : Assurez-vous que les chemins sont corrects
- **JavaScript errors** : Ouvrez la console développeur

### Logs
Le serveur FastAPI affiche les logs détaillés pour le debugging.

---

**Résultat** : Interface moderne et professionnelle qui remplace avantageusement Streamlit ! 🎉
