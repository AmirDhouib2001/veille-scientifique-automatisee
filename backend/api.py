"""
API Backend FastAPI pour la veille scientifique
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv

# Import des agents
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents import VeilleScientifiqueCrew

load_dotenv()

# Création de l'application FastAPI
app = FastAPI(
    title="Veille Scientifique API",
    description="API pour la recherche et l'analyse d'articles scientifiques",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== MODELS =====

class SearchRequest(BaseModel):
    """Modèle de requête pour la recherche"""
    keyword: str
    max_articles: int = 10


class SearchResponse(BaseModel):
    """Modèle de réponse pour la recherche"""
    success: bool
    keyword: Optional[str] = None
    articles_count: Optional[int] = None
    quick_summary: Optional[str] = None
    global_synthesis: Optional[str] = None
    article_summaries: Optional[list] = None
    pdf_path: Optional[str] = None
    error: Optional[str] = None


# ===== ENDPOINTS =====

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Veille Scientifique API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "database": "connected",
        "mcp": os.getenv('USE_MCP_ARXIV', 'false')
    }


@app.post("/api/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    """
    Recherche et analyse des articles scientifiques
    
    Args:
        request: Requête contenant le mot-clé et le nombre d'articles
        
    Returns:
        Résultats de la veille scientifique
    """
    try:
        # Validation
        if not request.keyword or request.keyword.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Le mot-clé ne peut pas être vide"
            )
        
        if request.max_articles < 1 or request.max_articles > 50:
            raise HTTPException(
                status_code=400,
                detail="Le nombre d'articles doit être entre 1 et 50"
            )
        
        # Création de l'équipe d'agents
        crew = VeilleScientifiqueCrew(
            keyword=request.keyword,
            max_articles=request.max_articles
        )
        
        # Exécution du workflow
        results = crew.run_complete_workflow()
        
        return SearchResponse(**results)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement : {str(e)}"
        )


@app.get("/api/config")
async def get_config():
    """Récupère la configuration de l'API"""
    return {
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "openai_model": os.getenv('OPENAI_MODEL', 'N/A'),
        "use_mcp": os.getenv('USE_MCP_ARXIV', 'false'),
        "max_articles_default": 10
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

