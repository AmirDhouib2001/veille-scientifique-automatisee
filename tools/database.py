"""
Gestion de la base de données PostgreSQL avec pgvector
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Optional
import json


class DatabaseManager:
    """Gestionnaire de la base de données PostgreSQL avec pgvector"""
    
    def __init__(self):
        """Initialise la connexion à la base de données"""
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'veille_scientifique'),
            'user': os.getenv('DB_USER', 'veille_user'),
            'password': os.getenv('DB_PASSWORD', 'veille_password')
        }
        self._init_database()
    
    def _get_connection(self):
        """Crée une nouvelle connexion à la base de données"""
        return psycopg2.connect(**self.connection_params)
    
    def _init_database(self):
        """Initialise la structure de la base de données"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Activation de l'extension pgvector
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Création de la table des articles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    entry_id VARCHAR(255) UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    published VARCHAR(20),
                    pdf_url TEXT,
                    categories TEXT,
                    keyword VARCHAR(255),
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Index pour les recherches vectorielles
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS articles_embedding_idx 
                ON articles USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation de la base de données : {e}")
    
    def insert_article(self, article: Dict, keyword: str, embedding: List[float]) -> bool:
        """
        Insert un article dans la base de données
        
        Args:
            article: Dictionnaire contenant les informations de l'article
            keyword: Mot-clé de recherche associé
            embedding: Vecteur d'embedding de l'article
            
        Returns:
            True si l'insertion a réussi, False sinon
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO articles 
                (entry_id, title, authors, summary, published, pdf_url, categories, keyword, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (entry_id) DO NOTHING;
            """, (
                article['entry_id'],
                article['title'],
                json.dumps(article['authors']),
                article['summary'],
                article['published'],
                article['pdf_url'],
                json.dumps(article.get('categories', [])),
                keyword,
                embedding
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'insertion de l'article : {e}")
            return False
    
    def search_similar_articles(self, query_embedding: List[float], keyword: str, limit: int = 5) -> List[Dict]:
        """
        Recherche les articles similaires via similarité cosinus
        
        Args:
            query_embedding: Vecteur d'embedding de la requête
            keyword: Mot-clé pour filtrer les résultats
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des articles les plus similaires
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT 
                    id, entry_id, title, authors, summary, published, 
                    pdf_url, categories,
                    1 - (embedding <=> %s::vector) as similarity
                FROM articles
                WHERE keyword = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
            """, (query_embedding, keyword, query_embedding, limit))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Conversion des résultats
            articles = []
            for row in results:
                article = dict(row)
                article['authors'] = json.loads(article['authors'])
                article['categories'] = json.loads(article['categories'])
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Erreur lors de la recherche d'articles similaires : {e}")
            return []
    
    def get_all_articles_by_keyword(self, keyword: str) -> List[Dict]:
        """
        Récupère tous les articles pour un mot-clé donné
        
        Args:
            keyword: Mot-clé de recherche
            
        Returns:
            Liste de tous les articles associés au mot-clé
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT id, entry_id, title, authors, summary, published, pdf_url, categories
                FROM articles
                WHERE keyword = %s
                ORDER BY published DESC;
            """, (keyword,))
            
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # Conversion des résultats
            articles = []
            for row in results:
                article = dict(row)
                article['authors'] = json.loads(article['authors'])
                article['categories'] = json.loads(article['categories'])
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"Erreur lors de la récupération des articles : {e}")
            return []
    
    def clear_articles_by_keyword(self, keyword: str) -> bool:
        """
        Supprime tous les articles associés à un mot-clé
        
        Args:
            keyword: Mot-clé de recherche
            
        Returns:
            True si la suppression a réussi
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM articles WHERE keyword = %s;", (keyword,))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erreur lors de la suppression des articles : {e}")
            return False

