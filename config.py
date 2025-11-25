"""
Configuration de l'application
"""
import os
from typing import Dict


class Config:
    """Classe de configuration centralisée"""
    
    # Base de données
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'veille_scientifique')
    DB_USER = os.getenv('DB_USER', 'veille_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'veille_password')
    
    # OpenRouter (compatible avec l'API OpenAI)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://openrouter.ai/api/v1')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'openrouter/x-ai/grok-4.1-fast:free')  # Grok 4.1 Fast Free
    
    # Application
    MAX_ARTICLES_DEFAULT = int(os.getenv('MAX_ARTICLES_DEFAULT', '10'))
    REPORTS_DIR = os.getenv('REPORTS_DIR', 'reports')
    
    # RAG - OpenRouter utilise des modèles d'embeddings compatibles
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'openai/text-embedding-3-small')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '1536'))
    TOP_K_RETRIEVAL = int(os.getenv('TOP_K_RETRIEVAL', '5'))
    
    @classmethod
    def validate(cls) -> Dict[str, bool]:
        """
        Valide la configuration
        
        Returns:
            Dictionnaire avec les statuts de validation
        """
        return {
            'openai_api_key': bool(cls.OPENAI_API_KEY and cls.OPENAI_API_KEY != 'your_openrouter_api_key_here' and cls.OPENAI_API_KEY.startswith('sk-')),
            'db_config': all([cls.DB_HOST, cls.DB_PORT, cls.DB_NAME, cls.DB_USER, cls.DB_PASSWORD])
        }
    
    @classmethod
    def get_db_url(cls) -> str:
        """
        Retourne l'URL de connexion à la base de données
        
        Returns:
            URL de connexion PostgreSQL
        """
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"

