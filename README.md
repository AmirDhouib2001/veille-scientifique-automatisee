# 🔬 Veille Scientifique Automatisée

Application de veille scientifique automatisée utilisant CrewAI, Streamlit, PostgreSQL/pgvector et OpenRouter.

## 🚀 Démarrage Rapide

### Prérequis
- Docker et Docker Compose installés
- Clé API OpenRouter

### Installation

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd projet
```

2. **Configurer la clé API**
```bash
cp env.example .env
# Éditer .env et ajouter votre clé OpenRouter
```

3. **Lancer l'application**
```bash
docker-compose up --build
```

4. **Accéder à l'interface**
Ouvrir http://localhost:8501 dans votre navigateur

## 📋 Fonctionnalités

- 🔍 **Collecte automatique** : Récupération d'articles arXiv par mot-clé
- 💾 **Stockage vectoriel** : PostgreSQL + pgvector pour RAG
- 📝 **Résumés intelligents** : Résumés générés par GPT-4 avec contexte RAG
- 📊 **Synthèse globale** : Vue d'ensemble des tendances scientifiques
- 📄 **Rapport PDF** : Document téléchargeable avec sources arXiv

## 🏗️ Architecture

```
┌─────────────┐
│  Streamlit  │  Interface utilisateur
└──────┬──────┘
       │
┌──────▼──────────────────────────────┐
│         CrewAI Agents               │
│  ┌────────┐ ┌──────────┐ ┌────────┐│
│  │Collector│→│Summarizer│→│Synthesizer││
│  └────────┘ └──────────┘ └────────┘│
└──────┬──────────────────────────────┘
       │
┌──────▼──────────────────┐
│  PostgreSQL + pgvector  │  Base de données vectorielle
└─────────────────────────┘
```

## 🛠️ Technologies

- **Frontend** : Streamlit
- **Orchestration** : CrewAI
- **LLM** : OpenRouter (xAI Grok 4.1 Fast)
- **Base de données** : PostgreSQL avec pgvector
- **Vectorisation** : LangChain + OpenRouter Embeddings
- **PDF** : ReportLab
- **Articles** : arXiv API

## 📝 Utilisation

1. Entrez un mot-clé de recherche (ex: "machine learning")
2. Lancez la veille scientifique
3. Consultez le résumé rapide (2-3 phrases)
4. Téléchargez le rapport PDF complet

## 🔧 Configuration Avancée

### Variables d'environnement (.env)
```
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_API_BASE=https://openrouter.ai/api/v1
OPENAI_MODEL=x-ai/grok-2-1212
DB_HOST=postgres
DB_PORT=5432
DB_NAME=veille_scientifique
DB_USER=veille_user
DB_PASSWORD=veille_password
```

### Nombre d'articles
Ajustez via le slider dans la barre latérale (3-20 articles)

## 🐳 Docker

### Services
- **postgres** : PostgreSQL 16 avec pgvector (port 5432)
- **app** : Application Streamlit (port 8501)

### Commandes utiles
```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Voir les logs
docker-compose logs -f

# Reconstruire
docker-compose up --build
```

## 📂 Structure du Projet

```
projet/
├── app.py                 # Application Streamlit
├── agents.py              # Agents CrewAI
├── tools/                 # Outils (arXiv, RAG, PDF)
│   ├── arxiv_tool.py
│   ├── database.py
│   ├── rag_tool.py
│   └── pdf_generator.py
├── docker-compose.yml     # Configuration Docker
├── Dockerfile
├── requirements.txt
└── README.md
```

## ⚠️ Notes

- **OpenRouter** : Cette application utilise OpenRouter pour accéder aux modèles LLM. Obtenez votre clé sur https://openrouter.ai/
- Première exécution : Téléchargement des images Docker (~2-3 min)
- Temps de traitement : 1-2 minutes selon le nombre d'articles
- Les rapports PDF sont sauvegardés dans `/reports`
- Configuration PostgreSQL conservée (pas besoin de la modifier)