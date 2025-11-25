"""
Application Streamlit pour la veille scientifique automatisée
"""
import streamlit as st
import os
from dotenv import load_dotenv
import requests
import time

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page
st.set_page_config(
    page_title="Veille Scientifique Automatisée",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: bold;
        color: #1a237e;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1976d2;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #43a047;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #fb8c00;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialise les variables de session"""
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'keyword_history' not in st.session_state:
        st.session_state.keyword_history = []


def display_header():
    """Affiche l'en-tête de l'application"""
    st.markdown('<h1 class="main-title">🔬 Veille Scientifique Automatisée</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="subtitle">Recherchez des articles scientifiques sur arXiv et obtenez une synthèse automatique</p>',
        unsafe_allow_html=True
    )


def display_sidebar():
    """Affiche la barre latérale avec les informations"""
    with st.sidebar:
        st.header("ℹ️ À propos")
        st.markdown("""
        Cette application utilise :
        - **arXiv** pour la recherche d'articles
        - **CrewAI** pour l'orchestration des agents
        - **PostgreSQL + pgvector** pour le RAG
        - **OpenRouter (xAI Grok 4.1 Fast)** pour les résumés
        - **ReportLab** pour la génération de PDF
        """)
        
        st.header("🎯 Fonctionnalités")
        st.markdown("""
        1. 🔍 Collecte automatique d'articles
        2. 💾 Stockage vectoriel (RAG)
        3. 📝 Résumés intelligents
        4. 📊 Synthèse globale
        5. 📄 Rapport PDF téléchargeable
        """)
        
        st.header("⚙️ Configuration")
        
        # Vérification de la clé API
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key.startswith('sk-'):
            st.success("✅ Clé API OpenRouter configurée")
        else:
            st.error("❌ Clé API OpenRouter manquante")
            st.info("Ajoutez votre clé dans le fichier .env")
        
        # Paramètres
        st.subheader("Paramètres de recherche")
        max_articles = st.slider(
            "Nombre d'articles",
            min_value=3,
            max_value=20,
            value=10,
            help="Nombre maximum d'articles à récupérer sur arXiv"
        )
        
        st.session_state.max_articles = max_articles
        
        # Historique
        if st.session_state.keyword_history:
            st.header("📜 Historique")
            for keyword in st.session_state.keyword_history[-5:]:
                st.text(f"• {keyword}")


def process_search(keyword: str, max_articles: int):
    """
    Traite la recherche de veille scientifique via l'API Backend
    
    Args:
        keyword: Mot-clé de recherche
        max_articles: Nombre maximum d'articles
    """
    try:
        # URL du backend API
        backend_url = os.getenv('BACKEND_API_URL', 'http://backend:8000')
        
        # Requête vers le backend
        with st.spinner('🔍 Envoi de la requête au backend...'):
            response = requests.post(
                f"{backend_url}/api/search",
                json={
                    "keyword": keyword,
                    "max_articles": max_articles
                },
                timeout=300  # 5 minutes max
            )
        
        # Vérification de la réponse
        if response.status_code == 200:
            results = response.json()
            
            # Stockage des résultats
            st.session_state.results = results
            
            # Ajout à l'historique
            if keyword not in st.session_state.keyword_history:
                st.session_state.keyword_history.append(keyword)
            
            return results
        else:
            error_detail = response.json().get('detail', 'Erreur inconnue')
            st.error(f"❌ Erreur API ({response.status_code}): {error_detail}")
            return None
        
    except requests.exceptions.Timeout:
        st.error(f"❌ Timeout : La requête a pris trop de temps (> 5 minutes)")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Erreur de connexion : Impossible de joindre le backend")
        st.info("Vérifiez que le backend est démarré (docker-compose)")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {str(e)}")
        return None


def display_results(results: dict):
    """
    Affiche les résultats de la veille scientifique
    
    Args:
        results: Dictionnaire contenant les résultats
    """
    if not results or not results.get('success'):
        st.markdown(
            '<div class="warning-box">⚠️ Aucun article trouvé pour ce mot-clé. Essayez un autre terme de recherche.</div>',
            unsafe_allow_html=True
        )
        return
    
    # Résumé rapide
    st.markdown("### ⚡ Résumé Rapide")
    st.markdown(
        f'<div class="success-box">{results["quick_summary"]}</div>',
        unsafe_allow_html=True
    )
    
    # Statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Articles trouvés", results['articles_count'])
    with col2:
        st.metric("📝 Articles résumés", len(results.get('article_summaries', [])))
    with col3:
        if results.get('pdf_path'):
            st.metric("✅ Rapport PDF", "Prêt")
        else:
            st.metric("❌ Rapport PDF", "Erreur")
    
    # Bouton de téléchargement du PDF
    if results.get('pdf_path') and os.path.exists(results['pdf_path']):
        st.markdown("---")
        st.markdown("### 📄 Télécharger le Rapport Complet")
        
        with open(results['pdf_path'], 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
            
            st.download_button(
                label="📥 Télécharger le rapport PDF",
                data=pdf_bytes,
                file_name=os.path.basename(results['pdf_path']),
                mime="application/pdf",
                use_container_width=True
            )
    
    # Synthèse globale (optionnel, affichable dans un expander)
    with st.expander("📊 Voir la synthèse globale détaillée"):
        st.markdown(results.get('global_synthesis', 'Non disponible'))
    
    # Liste des articles (optionnel)
    with st.expander("📚 Voir la liste des articles"):
        for idx, article in enumerate(results.get('article_summaries', []), 1):
            st.markdown(f"**{idx}. {article['title']}**")
            st.markdown(f"*Auteurs : {', '.join(article['authors'][:3])}{'...' if len(article['authors']) > 3 else ''}*")
            st.markdown(f"*Date : {article['published']}*")
            st.markdown(f"[🔗 Lien arXiv]({article['pdf_url']})")
            st.markdown("---")


def main():
    """Fonction principale de l'application"""
    # Initialisation
    init_session_state()
    
    # Affichage de l'en-tête
    display_header()
    
    # Barre latérale
    display_sidebar()
    
    # Zone de recherche principale
    st.markdown("---")
    
    # Formulaire de recherche
    with st.form(key='search_form'):
        keyword = st.text_input(
            "🔎 Entrez un mot-clé de recherche",
            placeholder="Ex: machine learning, quantum computing, climate change...",
            help="Saisissez un mot-clé ou une expression pour rechercher des articles scientifiques"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button(
                label="🚀 Lancer la veille scientifique",
                use_container_width=True
            )
    
    # Traitement de la recherche
    if submit_button:
        if not keyword or keyword.strip() == "":
            st.warning("⚠️ Veuillez entrer un mot-clé de recherche")
        else:
            # Vérification de la clé API
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key or not api_key.startswith('sk-'):
                st.error("❌ Clé API OpenRouter non configurée. Veuillez ajouter votre clé dans le fichier .env")
                return
            
            # Traitement
            st.markdown("---")
            st.markdown("### 🔄 Traitement en cours...")
            
            # Création d'une zone de progression
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulation de progression (les vraies étapes sont dans les agents)
            steps = [
                ("🔍 Recherche d'articles sur arXiv...", 20),
                ("💾 Stockage dans la base de données...", 40),
                ("📝 Résumé des articles avec RAG...", 60),
                ("📊 Génération de la synthèse globale...", 80),
                ("📄 Création du rapport PDF...", 100)
            ]
            
            for step_text, progress in steps:
                status_text.text(step_text)
                progress_bar.progress(progress)
                time.sleep(0.5)
            
            # Exécution réelle
            max_articles = st.session_state.get('max_articles', 10)
            results = process_search(keyword.strip(), max_articles)
            
            # Nettoyage de la barre de progression
            progress_bar.empty()
            status_text.empty()
            
            # Affichage des résultats
            if results:
                st.success("✅ Veille scientifique terminée avec succès !")
                st.markdown("---")
                display_results(results)
    
    # Affichage des résultats précédents si disponibles
    elif st.session_state.results:
        st.markdown("---")
        st.markdown("### 📊 Résultats de la dernière recherche")
        display_results(st.session_state.results)
    
    # Message d'accueil si aucune recherche n'a été effectuée
    else:
        st.markdown(
            '<div class="info-box">👋 Bienvenue ! Entrez un mot-clé ci-dessus pour commencer votre veille scientifique automatisée.</div>',
            unsafe_allow_html=True
        )
        
        # Exemples de mots-clés
        st.markdown("### 💡 Exemples de mots-clés")
        examples = [
            "machine learning",
            "quantum computing",
            "climate change",
            "artificial intelligence",
            "renewable energy",
            "biotechnology"
        ]
        
        cols = st.columns(3)
        for idx, example in enumerate(examples):
            with cols[idx % 3]:
                st.code(example)


if __name__ == "__main__":
    main()

