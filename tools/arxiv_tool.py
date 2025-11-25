"""
Outil pour récupérer les articles depuis arXiv
"""
import arxiv
from typing import List, Dict


def search_arxiv(keyword: str, max_results: int = 10) -> List[Dict]:
    """
    Recherche des articles scientifiques sur arXiv
    
    Args:
        keyword: Mot-clé de recherche
        max_results: Nombre maximum de résultats (défaut: 10)
        
    Returns:
        Liste de dictionnaires contenant les informations des articles
    """
    try:
        # Recherche sur arXiv
        search = arxiv.Search(
            query=keyword,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        articles = []
        for result in search.results():
            article = {
                'title': result.title,
                'authors': [author.name for author in result.authors],
                'summary': result.summary,
                'published': result.published.strftime('%Y-%m-%d'),
                'pdf_url': result.pdf_url,
                'entry_id': result.entry_id,
                'categories': result.categories
            }
            articles.append(article)
        
        return articles
        
    except Exception as e:
        print(f"Erreur lors de la recherche arXiv : {e}")
        return []

