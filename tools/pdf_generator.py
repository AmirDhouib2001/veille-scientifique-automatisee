"""
Générateur de rapports PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from typing import List, Dict
from datetime import datetime
import os


class PDFGenerator:
    """Générateur de rapports PDF pour la veille scientifique"""
    
    def __init__(self):
        """Initialise le générateur de PDF"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés pour le PDF"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor='#1a237e',
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les titres de section
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor='#283593',
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les titres d'articles
        self.styles.add(ParagraphStyle(
            name='ArticleTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor='#3949ab',
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour le texte justifié
        self.styles.add(ParagraphStyle(
            name='Justified',
            parent=self.styles['BodyText'],
            alignment=TA_JUSTIFY,
            fontSize=10,
            leading=14
        ))
    
    def generate_report(
        self, 
        keyword: str, 
        global_summary: str, 
        article_summaries: List[Dict], 
        output_path: str
    ) -> str:
        """
        Génère un rapport PDF complet
        
        Args:
            keyword: Mot-clé de recherche
            global_summary: Résumé global de la veille
            article_summaries: Liste des résumés d'articles avec leurs métadonnées
            output_path: Chemin du fichier PDF à générer
            
        Returns:
            Chemin du fichier PDF généré
        """
        try:
            # Création du document PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Contenu du PDF
            story = []
            
            # Page de garde
            story.extend(self._create_cover_page(keyword))
            story.append(PageBreak())
            
            # Résumé global
            story.extend(self._create_global_summary(global_summary))
            story.append(PageBreak())
            
            # Résumés individuels des articles
            story.extend(self._create_article_summaries(article_summaries))
            
            # Construction du PDF
            doc.build(story)
            
            return output_path
            
        except Exception as e:
            print(f"Erreur lors de la génération du PDF : {e}")
            return ""
    
    def _create_cover_page(self, keyword: str) -> List:
        """
        Crée la page de garde du rapport
        
        Args:
            keyword: Mot-clé de recherche
            
        Returns:
            Liste des éléments de la page de garde
        """
        elements = []
        
        # Titre principal
        elements.append(Spacer(1, 3*cm))
        title = Paragraph(
            "Rapport de Veille Scientifique",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 1*cm))
        
        # Mot-clé
        keyword_text = Paragraph(
            f"<b>Mot-clé :</b> {keyword}",
            self.styles['Heading2']
        )
        elements.append(keyword_text)
        elements.append(Spacer(1, 1*cm))
        
        # Date de génération
        date_text = Paragraph(
            f"<b>Date :</b> {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['Normal']
        )
        elements.append(date_text)
        
        return elements
    
    def _create_global_summary(self, global_summary: str) -> List:
        """
        Crée la section du résumé global
        
        Args:
            global_summary: Texte du résumé global
            
        Returns:
            Liste des éléments de la section
        """
        elements = []
        
        # Titre de section
        section_title = Paragraph(
            "Synthèse Globale",
            self.styles['SectionTitle']
        )
        elements.append(section_title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Contenu du résumé
        formatted_summary = global_summary.replace('\n', '<br/>')
        summary_paragraph = Paragraph(
            formatted_summary,
            self.styles['Justified']
        )
        elements.append(summary_paragraph)
        
        return elements
    
    def _create_article_summaries(self, article_summaries: List[Dict]) -> List:
        """
        Crée les sections des résumés individuels d'articles
        
        Args:
            article_summaries: Liste des articles avec leurs résumés
            
        Returns:
            Liste des éléments des sections
        """
        elements = []
        
        # Titre de section
        section_title = Paragraph(
            "Résumés des Articles",
            self.styles['SectionTitle']
        )
        elements.append(section_title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Parcours de chaque article
        for idx, article in enumerate(article_summaries, 1):
            # Numéro et titre de l'article
            article_title = Paragraph(
                f"<b>Article {idx} :</b> {article['title']}",
                self.styles['ArticleTitle']
            )
            elements.append(article_title)
            elements.append(Spacer(1, 0.2*cm))
            
            # Auteurs
            authors_text = ", ".join(article['authors'][:3])
            if len(article['authors']) > 3:
                authors_text += f" et {len(article['authors']) - 3} autres"
            
            authors = Paragraph(
                f"<b>Auteurs :</b> {authors_text}",
                self.styles['Normal']
            )
            elements.append(authors)
            elements.append(Spacer(1, 0.2*cm))
            
            # Date de publication
            published = Paragraph(
                f"<b>Date de publication :</b> {article['published']}",
                self.styles['Normal']
            )
            elements.append(published)
            elements.append(Spacer(1, 0.2*cm))
            
            # Résumé
            summary_text = article['summary'].replace('\n', '<br/>')
            summary = Paragraph(
                f"<b>Résumé :</b><br/>{summary_text}",
                self.styles['Justified']
            )
            elements.append(summary)
            elements.append(Spacer(1, 0.3*cm))
            
            # Lien arXiv
            link = Paragraph(
                f"<b>Lien arXiv :</b> <a href='{article['pdf_url']}'>{article['pdf_url']}</a>",
                self.styles['Normal']
            )
            elements.append(link)
            elements.append(Spacer(1, 0.5*cm))
            
            # Séparateur (sauf pour le dernier article)
            if idx < len(article_summaries):
                elements.append(Spacer(1, 0.3*cm))
        
        return elements


def generate_pdf_report(
    keyword: str,
    global_summary: str,
    article_summaries: List[Dict],
    output_dir: str = "reports"
) -> str:
    """
    Fonction helper pour générer un rapport PDF
    
    Args:
        keyword: Mot-clé de recherche
        global_summary: Résumé global
        article_summaries: Liste des résumés d'articles
        output_dir: Répertoire de sortie
        
    Returns:
        Chemin du fichier PDF généré
    """
    # Création du répertoire si nécessaire
    os.makedirs(output_dir, exist_ok=True)
    
    # Nom du fichier PDF
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"rapport_veille_{keyword.replace(' ', '_')}_{timestamp}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    # Génération du PDF
    generator = PDFGenerator()
    return generator.generate_report(keyword, global_summary, article_summaries, output_path)

