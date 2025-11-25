"""
Serveur MCP pour la recherche d'articles scientifiques sur arXiv
"""
import asyncio
import arxiv
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import json


# Création du serveur MCP
app = Server("arxiv-search-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Liste les outils disponibles dans ce serveur MCP
    
    Returns:
        Liste des outils exposés par le serveur
    """
    return [
        Tool(
            name="search_arxiv",
            description=(
                "Recherche des articles scientifiques récents sur arXiv. "
                "Retourne les informations détaillées des articles : titre, auteurs, résumé, "
                "date de publication, lien PDF et catégories. Les résultats sont triés par date "
                "de soumission (plus récents en premier)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Mot-clé ou expression de recherche pour trouver des articles scientifiques"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Nombre maximum d'articles à récupérer (défaut: 10, min: 1, max: 50)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 50
                    }
                },
                "required": ["keyword"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    Exécute un outil du serveur MCP
    
    Args:
        name: Nom de l'outil à exécuter
        arguments: Arguments pour l'outil
        
    Returns:
        Liste de contenus textuels avec les résultats
    """
    if name == "search_arxiv":
        return await search_arxiv_tool(arguments)
    else:
        raise ValueError(f"Outil inconnu: {name}")


async def search_arxiv_tool(arguments: dict) -> list[TextContent]:
    """
    Outil de recherche sur arXiv
    
    Args:
        arguments: Dictionnaire contenant 'keyword' et optionnellement 'max_results'
        
    Returns:
        Liste de TextContent avec les résultats JSON
    """
    keyword = arguments.get("keyword")
    max_results = arguments.get("max_results", 10)
    
    if not keyword:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": "Le paramètre 'keyword' est requis",
                "success": False
            }, ensure_ascii=False, indent=2)
        )]
    
    try:
        # Recherche sur arXiv
        search = arxiv.Search(
            query=keyword,
            max_results=min(max_results, 50),  # Limite à 50 maximum
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        articles = []
        for result in search.results():
            article = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "summary": result.summary,
                "published": result.published.strftime('%Y-%m-%d'),
                "pdf_url": result.pdf_url,
                "entry_id": result.entry_id,
                "categories": result.categories,
                "primary_category": result.primary_category
            }
            articles.append(article)
        
        result_data = {
            "success": True,
            "keyword": keyword,
            "count": len(articles),
            "articles": articles
        }
        
        return [TextContent(
            type="text",
            text=json.dumps(result_data, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Erreur lors de la recherche arXiv: {str(e)}",
                "success": False
            }, ensure_ascii=False, indent=2)
        )]


async def main():
    """Point d'entrée principal du serveur MCP"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

