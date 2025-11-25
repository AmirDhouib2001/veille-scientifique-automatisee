"""
Agents CrewAI pour la veille scientifique automatisée
"""
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools.rag_tool import RAGTool
from tools.pdf_generator import generate_pdf_report
from typing import List, Dict
import os

# Désactiver la télémétrie CrewAI
os.environ['CREWAI_TELEMETRY_OPT_OUT'] = 'true'

# Configuration : utiliser MCP ou appel direct
USE_MCP_ARXIV = os.getenv('USE_MCP_ARXIV', 'true').lower() == 'true'

if USE_MCP_ARXIV:
    from tools.arxiv_mcp_client import search_arxiv_sync as search_arxiv
    print("🔌 Utilisation du serveur MCP arXiv")
else:
    from tools.arxiv_tool import search_arxiv
    print("📚 Utilisation de l'appel direct arXiv")


class VeilleScientifiqueCrew:
    """Équipe d'agents pour la veille scientifique"""
    
    def __init__(self, keyword: str, max_articles: int = 10):
        """
        Initialise l'équipe d'agents
        
        Args:
            keyword: Mot-clé de recherche
            max_articles: Nombre maximum d'articles à récupérer
        """
        self.keyword = keyword
        self.max_articles = max_articles
        self.rag_tool = RAGTool()
        
        # Initialisation du modèle LLM avec OpenRouter (Grok 4.1 Fast Free)
        self.llm = ChatOpenAI(
            model="openrouter/x-ai/grok-4.1-fast:free",  # xAI Grok 4.1 Fast Free via OpenRouter
            temperature=0.3,
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            openai_api_base=os.getenv('OPENAI_API_BASE', 'https://openrouter.ai/api/v1')
        )
        
        # Stockage des résultats intermédiaires
        self.articles = []
        self.article_summaries = []
    
    def create_collector_agent(self) -> Agent:
        """
        Crée l'agent Collector qui récupère les articles arXiv
        
        Returns:
            Agent Collector configuré
        """
        return Agent(
            role='Collecteur d\'Articles Scientifiques',
            goal=f'Récupérer les articles scientifiques les plus récents sur arXiv concernant le sujet : {self.keyword}',
            backstory=(
                'Expert en recherche scientifique avec une grande expérience '
                'dans la collecte et l\'organisation d\'articles académiques. '
                'Tu es capable d\'identifier rapidement les publications pertinentes '
                'et de les structurer pour une analyse ultérieure.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_summarizer_agent(self) -> Agent:
        """
        Crée l'agent Summarizer qui résume les articles
        
        Returns:
            Agent Summarizer configuré
        """
        return Agent(
            role='Analyseur et Résumeur d\'Articles',
            goal='Créer des résumés précis et concis des articles scientifiques en utilisant le contexte RAG',
            backstory=(
                'Chercheur scientifique spécialisé dans l\'analyse et la synthèse '
                'd\'articles académiques. Tu excelles dans l\'extraction des points clés '
                'et la création de résumés fidèles au contenu original, sans ajout d\'information.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_synthesizer_agent(self) -> Agent:
        """
        Crée l'agent Synthesizer qui crée la synthèse globale
        
        Returns:
            Agent Synthesizer configuré
        """
        return Agent(
            role='Synthétiseur de Veille Scientifique',
            goal='Créer une synthèse globale cohérente des tendances et découvertes scientifiques',
            backstory=(
                'Expert en veille scientifique avec une vision d\'ensemble exceptionnelle. '
                'Tu es capable d\'identifier les tendances émergentes, les points communs '
                'et les découvertes importantes à travers plusieurs articles scientifiques.'
            ),
            verbose=False,
            allow_delegation=False,
            llm=self.llm
        )
    
    def create_collection_task(self, agent: Agent) -> Task:
        """
        Crée la tâche de collecte d'articles
        
        Args:
            agent: Agent Collector
            
        Returns:
            Tâche de collecte configurée
        """
        return Task(
            description=(
                f'Rechercher et récupérer {self.max_articles} articles scientifiques récents '
                f'sur arXiv concernant le sujet : "{self.keyword}". '
                f'Pour chaque article, extraire : titre, auteurs, résumé, date de publication, et lien PDF. '
                f'Stocker les articles dans la base de données avec leurs embeddings vectoriels.'
            ),
            agent=agent,
            expected_output=(
                f'Liste de {self.max_articles} articles avec leurs métadonnées complètes, '
                f'stockés dans la base de données PostgreSQL avec pgvector.'
            )
        )
    
    def create_summarization_task(self, agent: Agent) -> Task:
        """
        Crée la tâche de résumé des articles
        
        Args:
            agent: Agent Summarizer
            
        Returns:
            Tâche de résumé configurée
        """
        return Task(
            description=(
                f'Pour chaque article collecté sur le sujet "{self.keyword}" : '
                f'1. Utiliser le contexte RAG pour récupérer les passages les plus pertinents. '
                f'2. Créer un résumé détaillé (5-8 phrases) basé UNIQUEMENT sur le contenu de l\'article. '
                f'3. Ne jamais inventer ou ajouter d\'informations non présentes dans l\'article. '
                f'4. Structurer le résumé de manière claire et cohérente.'
            ),
            agent=agent,
            expected_output=(
                'Liste de résumés détaillés pour chaque article, '
                'avec titre, auteurs, date, et résumé basé sur le contexte RAG.'
            )
        )
    
    def create_quick_summary_task(self, agent: Agent) -> Task:
        """
        Crée la tâche de résumé rapide (2-3 phrases)
        
        Args:
            agent: Agent Summarizer
            
        Returns:
            Tâche de résumé rapide configurée
        """
        return Task(
            description=(
                f'Créer un résumé ultra-concis (2-3 phrases maximum) des principales découvertes '
                f'concernant le sujet "{self.keyword}" basé sur les articles collectés. '
                f'Ce résumé doit être immédiatement compréhensible et informatif.'
            ),
            agent=agent,
            expected_output=(
                'Un résumé de 2-3 phrases présentant les points clés de la veille scientifique.'
            )
        )
    
    def create_synthesis_task(self, agent: Agent) -> Task:
        """
        Crée la tâche de synthèse globale
        
        Args:
            agent: Agent Synthesizer
            
        Returns:
            Tâche de synthèse configurée
        """
        return Task(
            description=(
                f'Créer une synthèse globale complète sur le sujet "{self.keyword}" en analysant '
                f'tous les résumés d\'articles. Identifier : '
                f'1. Les tendances principales et thèmes récurrents. '
                f'2. Les découvertes ou innovations importantes. '
                f'3. Les points de convergence entre les différents articles. '
                f'4. Les perspectives futures et implications. '
                f'La synthèse doit être structurée et d\'environ 10-15 phrases.'
            ),
            agent=agent,
            expected_output=(
                'Une synthèse globale structurée présentant les tendances, '
                'découvertes et implications de la veille scientifique.'
            )
        )
    
    def execute_collection(self) -> List[Dict]:
        """
        Exécute la collecte d'articles depuis arXiv et les stocke dans la base de données
        
        Returns:
            Liste des articles collectés
        """
        print(f"🔍 Recherche d'articles sur arXiv pour : {self.keyword}")
        
        # Recherche des articles
        self.articles = search_arxiv(self.keyword, self.max_articles)
        
        if not self.articles:
            print("❌ Aucun article trouvé")
            return []
        
        print(f"✅ {len(self.articles)} articles trouvés")
        
        # Stockage dans la base de données avec RAG
        print("💾 Stockage dans la base de données avec embeddings...")
        stored_count = self.rag_tool.store_multiple_articles(self.articles, self.keyword)
        print(f"✅ {stored_count} articles stockés avec succès")
        
        return self.articles
    
    def execute_summarization(self) -> List[Dict]:
        """
        Exécute la résumé des articles avec RAG
        
        Returns:
            Liste des articles avec leurs résumés
        """
        if not self.articles:
            print("❌ Aucun article à résumer")
            return []
        
        print(f"📝 Résumé de {len(self.articles)} articles avec RAG...")
        
        summarizer_agent = self.create_summarizer_agent()
        
        for idx, article in enumerate(self.articles, 1):
            print(f"  📄 [{idx}/{len(self.articles)}] Traitement : {article['title'][:60]}...")
            
            # Récupération du contexte RAG pour l'article
            context = self.rag_tool.get_context_for_summary(article['title'], self.keyword)
            
            # Création de la tâche de résumé pour cet article
            summary_task = Task(
                description=(
                    f'Résumer l\'article suivant en 5-8 phrases basées UNIQUEMENT sur le contenu fourni :\n\n'
                    f'Titre : {article["title"]}\n'
                    f'Résumé original : {article["summary"]}\n\n'
                    f'Contexte additionnel (si pertinent) :\n{context}\n\n'
                    f'Règles strictes :\n'
                    f'- Ne jamais inventer ou ajouter d\'informations\n'
                    f'- Rester fidèle au contenu de l\'article\n'
                    f'- Être clair et concis'
                ),
                agent=summarizer_agent,
                expected_output='Un résumé détaillé de 5-8 phrases'
            )
            
            # Création d'un crew temporaire pour cette tâche
            temp_crew = Crew(
                agents=[summarizer_agent],
                tasks=[summary_task],
                process=Process.sequential,
                verbose=False
            )
            
            # Exécution
            result = temp_crew.kickoff()
            print(f"  ✅ [{idx}/{len(self.articles)}] Résumé terminé")
            
            # Ajout du résumé à l'article
            self.article_summaries.append({
                'title': article['title'],
                'authors': article['authors'],
                'published': article['published'],
                'pdf_url': article['pdf_url'],
                'summary': str(result)
            })
        
        print(f"✅ {len(self.article_summaries)} articles résumés")
        return self.article_summaries
    
    def execute_quick_summary(self) -> str:
        """
        Génère un résumé rapide (2-3 phrases) pour affichage immédiat
        
        Returns:
            Résumé rapide
        """
        if not self.articles:
            return "Aucun article trouvé pour ce mot-clé."
        
        print("⚡ Génération du résumé rapide...")
        
        # Création du contexte pour le résumé rapide
        titles_and_summaries = "\n\n".join([
            f"- {article['title']}: {article['summary'][:200]}..."
            for article in self.articles[:3]  # Utilise les 3 premiers articles
        ])
        
        summarizer_agent = self.create_summarizer_agent()
        quick_task = Task(
            description=(
                f'Créer un résumé ultra-concis de 2-3 phrases maximum sur les principales découvertes '
                f'concernant "{self.keyword}" basé sur ces articles :\n\n'
                f'{titles_and_summaries}\n\n'
                f'Le résumé doit être immédiatement compréhensible et informatif.'
            ),
            agent=summarizer_agent,
            expected_output='Un résumé de 2-3 phrases maximum'
        )
        
        crew = Crew(
            agents=[summarizer_agent],
            tasks=[quick_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        quick_summary = str(result)
        
        print("✅ Résumé rapide généré")
        return quick_summary
    
    def execute_global_synthesis(self) -> str:
        """
        Génère la synthèse globale détaillée
        
        Returns:
            Synthèse globale
        """
        if not self.article_summaries:
            return "Aucun résumé disponible pour créer une synthèse."
        
        print("📊 Génération de la synthèse globale...")
        
        # Création du contexte pour la synthèse
        all_summaries = "\n\n".join([
            f"Article : {article['title']}\nRésumé : {article['summary']}"
            for article in self.article_summaries
        ])
        
        synthesizer_agent = self.create_synthesizer_agent()
        synthesis_task = Task(
            description=(
                f'Créer une synthèse globale complète sur "{self.keyword}" en analysant '
                f'les résumés suivants :\n\n{all_summaries}\n\n'
                f'Identifier :\n'
                f'1. Les tendances principales et thèmes récurrents\n'
                f'2. Les découvertes ou innovations importantes\n'
                f'3. Les points de convergence entre les articles\n'
                f'4. Les perspectives futures et implications\n\n'
                f'Synthèse de 10-15 phrases, structurée et cohérente.'
            ),
            agent=synthesizer_agent,
            expected_output='Une synthèse globale structurée de 10-15 phrases'
        )
        
        crew = Crew(
            agents=[synthesizer_agent],
            tasks=[synthesis_task],
            process=Process.sequential,
            verbose=False
        )
        
        result = crew.kickoff()
        global_synthesis = str(result)
        
        print("✅ Synthèse globale générée")
        return global_synthesis
    
    def generate_pdf_report(self, global_synthesis: str, output_dir: str = "reports") -> str:
        """
        Génère le rapport PDF final
        
        Args:
            global_synthesis: Synthèse globale
            output_dir: Répertoire de sortie
            
        Returns:
            Chemin du fichier PDF généré
        """
        print("📄 Génération du rapport PDF...")
        
        pdf_path = generate_pdf_report(
            keyword=self.keyword,
            global_summary=global_synthesis,
            article_summaries=self.article_summaries,
            output_dir=output_dir
        )
        
        if pdf_path:
            print(f"✅ Rapport PDF généré : {pdf_path}")
        else:
            print("❌ Erreur lors de la génération du PDF")
        
        return pdf_path
    
    def run_complete_workflow(self) -> Dict:
        """
        Exécute le workflow complet de veille scientifique
        
        Returns:
            Dictionnaire contenant tous les résultats
        """
        print(f"\n{'='*60}")
        print(f"🚀 DÉMARRAGE DE LA VEILLE SCIENTIFIQUE")
        print(f"   Mot-clé : {self.keyword}")
        print(f"   Nombre d'articles : {self.max_articles}")
        print(f"{'='*60}\n")
        
        # 1. Collecte des articles
        articles = self.execute_collection()
        
        if not articles:
            return {
                'success': False,
                'error': 'Aucun article trouvé',
                'quick_summary': 'Aucun article trouvé pour ce mot-clé.',
                'pdf_path': None
            }
        
        # 2. Génération du résumé rapide
        quick_summary = self.execute_quick_summary()
        
        # 3. Résumé des articles avec RAG
        article_summaries = self.execute_summarization()
        
        # 4. Synthèse globale
        global_synthesis = self.execute_global_synthesis()
        
        # 5. Génération du PDF
        pdf_path = self.generate_pdf_report(global_synthesis)
        
        print(f"\n{'='*60}")
        print(f"✅ VEILLE SCIENTIFIQUE TERMINÉE AVEC SUCCÈS")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'keyword': self.keyword,
            'articles_count': len(articles),
            'quick_summary': quick_summary,
            'global_synthesis': global_synthesis,
            'article_summaries': article_summaries,
            'pdf_path': pdf_path
        }