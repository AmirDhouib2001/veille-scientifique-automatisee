"""
Outil RAG (Retrieval-Augmented Generation) avec pgvector
"""
from typing import List, Dict
from langchain_openai import OpenAIEmbeddings
from tools.database import DatabaseManager
import os


class RAGTool:
    """Outil pour la récupération augmentée par génération (RAG)"""
    
    def __init__(self):
        """Initialise le RAG avec OpenRouter embeddings et la base de données"""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('OPENAI_API_BASE', 'https://openrouter.ai/api/v1'),
            model="openai/text-embedding-3-small"
        )
        self.db_manager = DatabaseManager()
    
    def embed_and_store_article(self, article: Dict, keyword: str) -> bool:
        """
        Génère l'embedding d'un article et le stocke dans la base de données
        
        Args:
            article: Dictionnaire contenant les informations de l'article
            keyword: Mot-clé de recherche associé
            
        Returns:
            True si le stockage a réussi
        """
        try:
            # Création du texte à embedder (titre + résumé)
            text_to_embed = f"{article['title']}\n\n{article['summary']}"
            
            # Génération de l'embedding
            embedding = self.embeddings.embed_query(text_to_embed)
            
            # Stockage dans la base de données
            return self.db_manager.insert_article(article, keyword, embedding)
            
        except Exception as e:
            print(f"Erreur lors de l'embedding et du stockage : {e}")
            return False
    
    def retrieve_relevant_articles(self, query: str, keyword: str, top_k: int = 5) -> List[Dict]:
        """
        Récupère les articles les plus pertinents pour une requête
        
        Args:
            query: Requête de recherche
            keyword: Mot-clé pour filtrer les articles
            top_k: Nombre d'articles à récupérer
            
        Returns:
            Liste des articles les plus pertinents
        """
        try:
            # Génération de l'embedding de la requête
            query_embedding = self.embeddings.embed_query(query)
            
            # Recherche des articles similaires
            articles = self.db_manager.search_similar_articles(
                query_embedding, 
                keyword, 
                limit=top_k
            )
            
            return articles
            
        except Exception as e:
            print(f"Erreur lors de la récupération des articles : {e}")
            return []
    
    def get_context_for_summary(self, article_title: str, keyword: str) -> str:
        """
        Récupère le contexte pertinent pour résumer un article spécifique
        
        Args:
            article_title: Titre de l'article à résumer
            keyword: Mot-clé pour filtrer les articles
            
        Returns:
            Contexte sous forme de texte
        """
        try:
            # Récupération des articles similaires basés sur le titre
            articles = self.retrieve_relevant_articles(article_title, keyword, top_k=3)
            
            # Construction du contexte
            context_parts = []
            for article in articles:
                context_parts.append(
                    f"Titre: {article['title']}\n"
                    f"Résumé: {article['summary']}\n"
                )
            
            return "\n---\n".join(context_parts)
            
        except Exception as e:
            print(f"Erreur lors de la récupération du contexte : {e}")
            return ""
    
    def store_multiple_articles(self, articles: List[Dict], keyword: str) -> int:
        """
        Stocke plusieurs articles avec leurs embeddings
        
        Args:
            articles: Liste des articles à stocker
            keyword: Mot-clé de recherche associé
            
        Returns:
            Nombre d'articles stockés avec succès
        """
        success_count = 0
        for article in articles:
            if self.embed_and_store_article(article, keyword):
                success_count += 1
        
        return success_count
    
    def get_all_articles(self, keyword: str) -> List[Dict]:
        """
        Récupère tous les articles pour un mot-clé
        
        Args:
            keyword: Mot-clé de recherche
            
        Returns:
            Liste de tous les articles
        """
        return self.db_manager.get_all_articles_by_keyword(keyword)

