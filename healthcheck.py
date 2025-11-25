"""
Script de vérification de santé de l'application
"""
import os
import sys
from typing import Dict


def check_openai_api_key() -> bool:
    """Vérifie si la clé API OpenRouter est configurée"""
    api_key = os.getenv('OPENAI_API_KEY', '')
    return bool(api_key and api_key != 'your_openrouter_api_key_here' and api_key.startswith('sk-'))


def check_database_connection() -> bool:
    """Vérifie la connexion à la base de données"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'veille_scientifique'),
            user=os.getenv('DB_USER', 'veille_user'),
            password=os.getenv('DB_PASSWORD', 'veille_password')
        )
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur de connexion à la base de données : {e}")
        return False


def check_required_packages() -> Dict[str, bool]:
    """Vérifie que tous les packages requis sont installés"""
    packages = {
        'streamlit': False,
        'crewai': False,
        'arxiv': False,
        'langchain': False,
        'openai': False,
        'reportlab': False,
        'psycopg2': False,
        'pgvector': False
    }
    
    for package in packages.keys():
        try:
            __import__(package)
            packages[package] = True
        except ImportError:
            packages[package] = False
    
    return packages


def run_healthcheck() -> bool:
    """
    Exécute tous les tests de santé
    
    Returns:
        True si tous les tests passent, False sinon
    """
    print("🏥 Vérification de santé de l'application\n")
    
    all_ok = True
    
    # Vérification de la clé API
    print("1️⃣  Vérification de la clé API OpenRouter...")
    if check_openai_api_key():
        print("   ✅ Clé API OpenRouter configurée\n")
    else:
        print("   ❌ Clé API OpenRouter non configurée ou invalide\n")
        all_ok = False
    
    # Vérification de la base de données
    print("2️⃣  Vérification de la connexion à la base de données...")
    if check_database_connection():
        print("   ✅ Connexion à PostgreSQL réussie\n")
    else:
        print("   ❌ Impossible de se connecter à PostgreSQL\n")
        all_ok = False
    
    # Vérification des packages
    print("3️⃣  Vérification des packages Python...")
    packages = check_required_packages()
    all_installed = True
    for package, installed in packages.items():
        status = "✅" if installed else "❌"
        print(f"   {status} {package}")
        if not installed:
            all_installed = False
            all_ok = False
    print()
    
    # Résultat final
    print("=" * 50)
    if all_ok:
        print("✅ Tous les tests de santé ont réussi !")
        print("   L'application est prête à être utilisée.")
    else:
        print("❌ Certains tests ont échoué.")
        print("   Veuillez corriger les problèmes avant d'utiliser l'application.")
    print("=" * 50)
    
    return all_ok


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    success = run_healthcheck()
    sys.exit(0 if success else 1)

