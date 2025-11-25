"""
Client MCP pour interagir avec le serveur arXiv
"""
import json
import subprocess
import asyncio
from typing import List, Dict, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class ArxivMCPClient:
    """Client pour interagir avec le serveur MCP arXiv"""
    
    def __init__(self):
        """Initialise le client MCP"""
        self.session: Optional[ClientSession] = None
        self._read_stream = None
        self._write_stream = None
        self._exit_stack = None
    
    async def connect(self):
        """Établit la connexion avec le serveur MCP arXiv"""
        server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_servers.arxiv_server"],
            env=None
        )
        
        # Utilisation du gestionnaire de contexte
        from contextlib import AsyncExitStack
        self._exit_stack = AsyncExitStack()
        
        self._read_stream, self._write_stream = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(self._read_stream, self._write_stream)
        )
        
        await self.session.initialize()
    
    async def disconnect(self):
        """Ferme la connexion avec le serveur MCP"""
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
            self.session = None
    
    async def search_arxiv(self, keyword: str, max_results: int = 10) -> List[Dict]:
        """
        Recherche des articles sur arXiv via MCP
        
        Args:
            keyword: Mot-clé de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des articles trouvés
        """
        if not self.session:
            await self.connect()
        
        try:
            # Appel de l'outil via MCP
            result = await self.session.call_tool(
                "search_arxiv",
                arguments={
                    "keyword": keyword,
                    "max_results": max_results
                }
            )
            
            # Extraction des résultats
            if result and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    data = json.loads(content.text)
                    if data.get("success"):
                        return data.get("articles", [])
                    else:
                        print(f"Erreur MCP: {data.get('error', 'Erreur inconnue')}")
                        return []
            
            return []
            
        except Exception as e:
            print(f"Erreur lors de l'appel MCP arXiv: {e}")
            return []


def search_arxiv_sync(keyword: str, max_results: int = 10) -> List[Dict]:
    """
    Version synchrone de la recherche arXiv via MCP
    
    Args:
        keyword: Mot-clé de recherche
        max_results: Nombre maximum de résultats
        
    Returns:
        Liste des articles trouvés
    """
    import concurrent.futures
    import threading
    
    async def _search():
        client = ArxivMCPClient()
        try:
            await client.connect()
            results = await client.search_arxiv(keyword, max_results)
            return results
        finally:
            await client.disconnect()
    
    def run_in_thread():
        """Exécute la coroutine dans un thread séparé avec son propre event loop"""
        return asyncio.run(_search())
    
    # Exécuter dans un thread séparé pour éviter les conflits avec l'event loop de FastAPI
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result(timeout=120)  # Timeout de 2 minutes

