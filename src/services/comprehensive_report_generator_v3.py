#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v3.0 - Comprehensive Report Generator V3
Compilador de relatório final a partir dos módulos gerados
"""

import os
import logging
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class ComprehensiveReportGeneratorV3:
    """Compilador de relatório final ultra robusto"""

    def __init__(self):
        """Inicializa o compilador"""
        # Ordem atualizada dos módulos, incluindo os novos módulos de CPL
        self.modules_order = [
            'anti_objecao',
            'avatars', 
            'concorrencia',
            'drivers_mentais',
            'funil_vendas',
            'insights_mercado',
            'palavras_chave',
            'plano_acao',
            'posicionamento',
            'pre_pitch',
            'predicoes_futuro',
            'provas_visuais',
            'metricas_conversao',
            'estrategia_preco',
            'canais_aquisicao',
            'cronograma_lancamento',
            # Novos módulos de CPL adicionados conforme instruções do CPL.txt
            'cpl_protocol_1',
            'cpl_protocol_2',
            'cpl_protocol_3',
            'cpl_protocol_4',
            'cpl_protocol_5'
        ]

        # Títulos atualizados, incluindo os novos módulos de CPL
        self.module_titles = {
            'anti_objecao': 'Sistema Anti-Objeção',
            'avatars': 'Avatares do Público-Alvo',
            'concorrencia': 'Análise Competitiva',
            'drivers_mentais': 'Drivers Mentais',
            'funil_vendas': 'Funil de Vendas',
            'insights_mercado': 'Insights de Mercado',
            'palavras_chave': 'Estratégia de Palavras-Chave',
            'plano_acao': 'Plano de Ação',
            'posicionamento': 'Estratégia de Posicionamento',
            'pre_pitch': 'Estrutura de Pré-Pitch',
            'predicoes_futuro': 'Predições de Mercado',
            'provas_visuais': 'Sistema de Provas Visuais',
            'metricas_conversao': 'Métricas de Conversão',
            'estrategia_preco': 'Estratégia de Precificação',
            'canais_aquisicao': 'Canais de Aquisição',
            'cronograma_lancamento': 'Cronograma de Lançamento',
            # Novos títulos de módulos de CPL adicionados conforme instruções do CPL.txt
            'cpl_protocol_1': 'Arquitetura do Evento Magnético',
            'cpl_protocol_2': 'CPL1 - A Oportunidade Paralisante',
            'cpl_protocol_3': 'CPL2 - A Transformação Impossível',
            'cpl_protocol_4': 'CPL3 - O Caminho Revolucionário',
            'cpl_protocol_5': 'CPL4 - A Decisão Inevitável'
        }

        logger.info("📋 Comprehensive Report Generator ULTRA ROBUSTO inicializado")

    def compile_final_markdown_report(self, session_id: str, predictive_insights: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Compila relatório final a partir dos módulos gerados

        Args:
            session_id: ID da sessão
            predictive_insights: Insights preditivos opcionais para incorporar ao relatório

        Returns:
            Dict com informações do relatório compilado
        """
        logger.info(f"📋 Compilando relatório final para sessão: {session_id}")

        try:
            # 1. Verifica estrutura de diretórios
            session_dir = Path(f"analyses_data/{session_id}")
            modules_dir = session_dir / "modules"
            files_dir = Path(f"analyses_data/files/{session_id}")

            if not session_dir.exists():
                raise Exception(f"Diretório da sessão não encontrado: {session_dir}")

            # 2. Carrega módulos disponíveis
            available_modules = self._load_available_modules(modules_dir)

            # 3. Carrega screenshots disponíveis
            screenshot_paths = self._load_screenshot_paths(files_dir)
            
            # 4. Carrega imagens virais extraídas
            viral_images = self._load_viral_images(session_id)

            # 5. Compila relatório (com insights preditivos e imagens virais)
            final_report = self._compile_report_content(
                session_id, 
                available_modules, 
                screenshot_paths,
                viral_images,
                predictive_insights
            )

            # 6. Salva relatório final
            report_path = self._save_final_report(session_id, final_report)

            # 7. Gera estatísticas
            statistics = self._generate_report_statistics(
                available_modules, 
                screenshot_paths, 
                viral_images,
                final_report
            )

            logger.info(f"✅ Relatório final compilado: {report_path}")

            return {
                "success": True,
                "session_id": session_id,
                "report_path": report_path,
                "modules_compiled": len(available_modules),
                "screenshots_included": len(screenshot_paths),
                "viral_images_included": len(viral_images),
                "estatisticas_relatorio": statistics,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Erro na compilação: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }

    def _load_available_modules(self, modules_dir: Path) -> Dict[str, str]:
        """Carrega módulos disponíveis"""
        available_modules = {}

        try:
            if not modules_dir.exists():
                logger.warning(f"⚠️ Diretório de módulos não existe: {modules_dir}")
                return available_modules

            for module_name in self.modules_order:
                # Primeiro tenta carregar arquivo .md
                module_file = modules_dir / f"{module_name}.md"
                if module_file.exists():
                    with open(module_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if content.strip():
                            available_modules[module_name] = content
                            logger.debug(f"✅ Módulo carregado: {module_name}")
                        else:
                            logger.warning(f"⚠️ Módulo vazio: {module_name}")
                else:
                    # Se não encontrar .md, tenta carregar arquivo .json (para módulos CPL)
                    module_file_json = modules_dir / f"{module_name}.json"
                    if module_file_json.exists():
                        try:
                            with open(module_file_json, 'r', encoding='utf-8') as f:
                                json_content = json.load(f)
                                # Converte o conteúdo JSON em uma representação em texto
                                content = json.dumps(json_content, indent=2, ensure_ascii=False)
                                available_modules[module_name] = content
                                logger.debug(f"✅ Módulo JSON carregado: {module_name}")
                        except Exception as e:
                            logger.warning(f"⚠️ Erro ao carregar módulo JSON {module_name}: {e}")
                    else:
                        logger.warning(f"⚠️ Módulo não encontrado: {module_name}")

            logger.info(f"📊 {len(available_modules)}/{len(self.modules_order)} módulos carregados")
            return available_modules

        except Exception as e:
            logger.error(f"❌ Erro ao carregar módulos: {e}")
            return available_modules

    def _load_screenshot_paths(self, files_dir: Path) -> List[str]:
        """Carrega caminhos dos screenshots"""
        screenshot_paths = []

        try:
            if not files_dir.exists():
                logger.warning(f"⚠️ Diretório de arquivos não existe: {files_dir}")
                return screenshot_paths

            # Busca por arquivos PNG (screenshots)
            for screenshot_file in files_dir.glob("*.png"):
                relative_path = f"files/{files_dir.name}/{screenshot_file.name}"
                screenshot_paths.append(relative_path)
                logger.debug(f"📸 Screenshot encontrado: {screenshot_file.name}")

            logger.info(f"📸 {len(screenshot_paths)} screenshots encontrados")
            return screenshot_paths

        except Exception as e:
            logger.error(f"❌ Erro ao carregar screenshots: {e}")
            return screenshot_paths
    
    def _load_viral_images(self, session_id: str) -> List[Dict[str, Any]]:
        """Carrega imagens virais extraídas"""
        viral_images = []
        
        try:
            # Busca arquivo de metadados das imagens virais
            viral_images_dir = Path("viral_images")
            metadata_file = viral_images_dir / f"viral_images_metadata_{session_id}.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    viral_images = metadata.get('images', [])
                    
                logger.info(f"🖼️ {len(viral_images)} imagens virais carregadas")
            else:
                logger.info("📷 Nenhuma imagem viral encontrada para esta sessão")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar imagens virais: {e}")
            
        return viral_images

    def _compile_report_content(
        self, 
        session_id: str, 
        modules: Dict[str, str], 
        screenshots: List[str],
        viral_images: List[Dict[str, Any]],
        predictive_insights: Dict[str, Any] = None
    ) -> str:
        """Compila conteúdo do relatório final com insights preditivos e imagens virais"""

        # Cabeçalho do relatório
        report = f"""# RELATÓRIO FINAL - ARQV30 Enhanced v3.0

**Sessão:** {session_id}  
**Gerado em:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Módulos Compilados:** {len(modules)}/{len(self.modules_order)}  
**Screenshots Incluídos:** {len(screenshots)}  
**Imagens Virais Extraídas:** {len(viral_images)}

---

## SUMÁRIO EXECUTIVO

Este relatório consolida a análise ultra-detalhada realizada pelo sistema ARQV30 Enhanced v3.0, contemplando {len(modules)} módulos especializados de análise estratégica.

### Módulos Incluídos:
"""

        # Lista de módulos
        for i, module_name in enumerate(self.modules_order, 1):
            title = self.module_titles.get(module_name, module_name.replace('_', ' ').title())
            status = "✅" if module_name in modules else "❌"
            report += f"{i}. {status} {title}\n"

        report += "\n---\n\n"

        # Adiciona screenshots se disponíveis
        if screenshots:
            report += "## EVIDÊNCIAS VISUAIS\n\n"
            for i, screenshot in enumerate(screenshots, 1):
                report += f"### Screenshot {i}\n"
                report += f"![Screenshot {i}]({screenshot})\n\n"
            report += "---\n\n"
        
        # Adiciona imagens virais extraídas
        if viral_images:
            report += "## IMAGENS VIRAIS EXTRAÍDAS\n\n"
            report += f"**Total de imagens extraídas:** {len(viral_images)}  \n"
            
            # Agrupa por plataforma
            by_platform = {}
            for img in viral_images:
                platform = img.get('platform', 'Unknown')
                if platform not in by_platform:
                    by_platform[platform] = []
                by_platform[platform].append(img)
            
            report += f"**Plataformas:** {', '.join(by_platform.keys())}  \n\n"
            
            # Mostra top 10 imagens por score de viralidade
            top_images = sorted(viral_images, key=lambda x: x.get('virality_score', 0), reverse=True)[:10]
            
            for i, img in enumerate(top_images, 1):
                report += f"### Imagem Viral {i} - {img.get('platform', 'Unknown')}\n\n"
                report += f"**Título:** {img.get('title', 'Sem título')}  \n"
                report += f"**Score de Viralidade:** {img.get('virality_score', 0):.1f}/100  \n"
                
                metrics = img.get('engagement_metrics', {})
                if metrics:
                    report += "**Métricas de Engajamento:**  \n"
                    for metric, value in metrics.items():
                        if value > 0:
                            report += f"- {metric.title()}: {value:,}  \n"
                
                # Adiciona imagem se o caminho existir
                local_path = img.get('local_path', '')
                if local_path and os.path.exists(local_path):
                    # Converte para caminho relativo para o relatório
                    relative_path = local_path.replace('/workspace/project/v90/src/', '')
                    report += f"![Imagem Viral {i}]({relative_path})  \n\n"
                
                report += "---\n\n"

        # SEÇÃO DE INSIGHTS PREDITIVOS E CENÁRIOS FUTUROS
        if predictive_insights and predictive_insights.get("success", False):
            report += self._compile_predictive_insights_section(predictive_insights)

        # Compila módulos na ordem definida
        for module_name in self.modules_order:
            if module_name in modules:
                title = self.module_titles.get(module_name, module_name.replace('_', ' ').title())
                report += f"## {title}\n\n"
                
                # Trata módulos CPL de forma especial (JSON)
                if module_name.startswith('cpl_protocol_'):
                    try:
                        # Tenta parsear o conteúdo como JSON
                        module_content = json.loads(modules[module_name])
                        report += self._format_cpl_module_content(module_content)
                    except json.JSONDecodeError:
                        # Se não for JSON válido, adiciona o conteúdo como está
                        report += modules[module_name]
                else:
                    # Módulos normais em Markdown
                    report += modules[module_name]
                
                report += "\n\n---\n\n"

        # Rodapé
        report += f"""
## INFORMAÇÕES TÉCNICAS

**Sistema:** ARQV30 Enhanced v3.0  
**Sessão:** {session_id}  
**Data de Compilação:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}  
**Módulos Processados:** {len(modules)}/{len(self.modules_order)}  
**Status:** {'Completo' if len(modules) == len(self.modules_order) else 'Parcial'}

### Estatísticas de Compilação:
- ✅ Sucessos: {len(modules)}
- ❌ Falhas: {len(self.modules_order) - len(modules)}
- 📊 Taxa de Sucesso: {(len(modules)/len(self.modules_order)*100):.1f}%

---

*Relatório compilado automaticamente pelo ARQV30 Enhanced v3.0*
"""

        return report

    def _format_cpl_module_content(self, cpl_content: Dict[str, Any]) -> str:
        """Formata o conteúdo de um módulo CPL para exibição no relatório"""
        try:
            formatted_content = ""
            
            # Adiciona título e descrição se disponíveis
            if 'titulo' in cpl_content:
                formatted_content += f"**{cpl_content['titulo']}**\n\n"
            
            if 'descricao' in cpl_content:
                formatted_content += f"{cpl_content['descricao']}\n\n"
            
            # Adiciona fases se disponíveis
            if 'fases' in cpl_content:
                for fase_key, fase_data in cpl_content['fases'].items():
                    if isinstance(fase_data, dict):
                        # Título da fase
                        if 'titulo' in fase_data:
                            formatted_content += f"### {fase_data['titulo']}\n\n"
                        
                        # Descrição da fase
                        if 'descricao' in fase_data:
                            formatted_content += f"{fase_data['descricao']}\n\n"
                        
                        # Outros campos da fase
                        for key, value in fase_data.items():
                            if key not in ['titulo', 'descricao']:
                                if isinstance(value, str):
                                    formatted_content += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
                                elif isinstance(value, list):
                                    formatted_content += f"**{key.replace('_', ' ').title()}:**\n"
                                    for item in value:
                                        if isinstance(item, str):
                                            formatted_content += f"- {item}\n"
                                        elif isinstance(item, dict):
                                            formatted_content += f"- {json.dumps(item, ensure_ascii=False)}\n"
                                    formatted_content += "\n"
                                elif isinstance(value, dict):
                                    formatted_content += f"**{key.replace('_', ' ').title()}:**\n"
                                    for sub_key, sub_value in value.items():
                                        formatted_content += f"  - {sub_key}: {sub_value}\n"
                                    formatted_content += "\n"
                    
            # Adiciona considerações finais se disponíveis
            if 'consideracoes_finais' in cpl_content:
                formatted_content += "### Considerações Finais\n\n"
                for key, value in cpl_content['consideracoes_finais'].items():
                    if isinstance(value, str):
                        formatted_content += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
                    elif isinstance(value, list):
                        formatted_content += f"**{key.replace('_', ' ').title()}:**\n"
                        for item in value:
                            formatted_content += f"- {item}\n"
                        formatted_content += "\n"
            
            return formatted_content
            
        except Exception as e:
            logger.error(f"❌ Erro ao formatar conteúdo CPL: {e}")
            return f"*Erro ao formatar conteúdo do módulo CPL: {str(e)}*\n\n{json.dumps(cpl_content, indent=2, ensure_ascii=False)}"

    def _save_final_report(self, session_id: str, report_content: str) -> str:
        """Salva relatório final"""
        try:
            # Salva relatório compilado
            os.makedirs(f"analyses_data/{session_id}", exist_ok=True)
            final_report_path = f"analyses_data/{session_id}/relatorio_final.md"

            with open(final_report_path, 'w', encoding='utf-8') as f:
                f.write(report_content)

            return str(final_report_path)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar relatório: {e}")
            raise

    def _generate_report_statistics(
        self, 
        modules: Dict[str, str], 
        screenshots: List[str], 
        viral_images: List[Dict[str, Any]],
        report_content: str
    ) -> Dict[str, Any]:
        """Gera estatísticas do relatório"""
        
        # Estatísticas das imagens virais
        viral_stats = {
            "total_images": len(viral_images),
            "by_platform": {},
            "average_virality_score": 0.0,
            "total_engagement": 0
        }
        
        if viral_images:
            # Agrupa por plataforma
            for img in viral_images:
                platform = img.get('platform', 'Unknown')
                if platform not in viral_stats["by_platform"]:
                    viral_stats["by_platform"][platform] = 0
                viral_stats["by_platform"][platform] += 1
            
            # Calcula score médio
            scores = [img.get('virality_score', 0) for img in viral_images]
            viral_stats["average_virality_score"] = sum(scores) / len(scores) if scores else 0
            
            # Calcula engajamento total
            for img in viral_images:
                metrics = img.get('engagement_metrics', {})
                viral_stats["total_engagement"] += sum(metrics.values())

        return {
            "total_modules": len(self.modules_order),
            "modules_compiled": len(modules),
            "modules_missing": len(self.modules_order) - len(modules),
            "success_rate": (len(modules) / len(self.modules_order)) * 100,
            "screenshots_included": len(screenshots),
            "viral_images_stats": viral_stats,
            "total_characters": len(report_content),
            "estimated_pages": len(report_content) // 2000,  # ~2000 chars por página
            "compilation_timestamp": datetime.now().isoformat(),
            "paginas_estimadas": max(20, len(report_content) // 2000),  # Mínimo 20 páginas
            "secoes_geradas": len(modules),
            "taxa_completude": (len(modules) / len(self.modules_order)) * 100
        }

    def generate_final_report(self, session_id: str) -> Dict[str, Any]:
        """Método de compatibilidade"""
        return self.compile_final_markdown_report(session_id)

    def generate_detailed_report(
        self, 
        massive_data: Dict[str, Any], 
        modules_data: Dict[str, Any], 
        context: Dict[str, Any], 
        session_id: str
    ) -> Dict[str, Any]:
        """Gera relatório detalhado (método de compatibilidade)"""
        return self.compile_final_markdown_report(session_id)

    def _compile_predictive_insights_section(self, predictive_insights: Dict[str, Any]) -> str:
        """Compila seção de insights preditivos e cenários futuros"""
        
        section = """## 🔮 ANÁLISE PREDITIVA E CENÁRIOS FUTUROS

### Metodologia de Análise Preditiva
Esta seção apresenta insights avançados gerados através de análise preditiva ultra-avançada, utilizando técnicas de machine learning, processamento de linguagem natural e modelagem estatística para projetar cenários futuros e identificar oportunidades estratégicas.

"""
        
        # Insights Textuais
        if "textual_insights" in predictive_insights:
            textual = predictive_insights["textual_insights"]
            section += "### 📊 Insights Textuais Avançados\n\n"
            
            if "entities_found" in textual and textual["entities_found"]:
                section += "**Entidades-Chave Identificadas:**\n"
                entities = textual["entities_found"]
                for entity, count in list(entities.items())[:10]:
                    section += f"- {entity}: {count} menções\n"
                section += "\n"
            
            if "total_documents_processed" in textual:
                section += f"**Documentos Analisados:** {textual['total_documents_processed']}\n"
                section += f"**Palavras Processadas:** {textual.get('total_words_analyzed', 'N/A')}\n\n"
        
        # Previsões
        if "predictions" in predictive_insights:
            predictions = predictive_insights["predictions"]
            section += "### 🎯 Previsões Estratégicas\n\n"
            
            if "market_trends" in predictions:
                trends = predictions["market_trends"]
                section += "**Tendências de Mercado Previstas:**\n"
                for trend in trends.get("predicted_trends", [])[:5]:
                    if isinstance(trend, dict):
                        section += f"- {trend.get('trend', 'Tendência')}: {trend.get('probability', 'N/A')}% de probabilidade\n"
                    else:
                        section += f"- {trend}\n"
                section += "\n"
            
            if "growth_projections" in predictions:
                growth = predictions["growth_projections"]
                section += "**Projeções de Crescimento:**\n"
                section += f"- Crescimento Estimado (3 meses): {growth.get('short_term', 'N/A')}\n"
                section += f"- Crescimento Estimado (12 meses): {growth.get('long_term', 'N/A')}\n"
                section += f"- Confiança da Previsão: {growth.get('confidence', 'N/A')}\n\n"
        
        # Cenários
        if "scenarios" in predictive_insights:
            scenarios = predictive_insights["scenarios"]
            section += "### 🗺️ Cenários Futuros Modelados\n\n"
            
            for scenario_name, scenario_data in scenarios.items():
                if isinstance(scenario_data, dict) and scenario_name != "methodology":
                    section += f"**Cenário {scenario_name.title()}:**\n"
                    section += f"- Probabilidade: {scenario_data.get('probability', 'N/A')}\n"
                    section += f"- Impacto: {scenario_data.get('impact', 'N/A')}\n"
                    section += f"- Descrição: {scenario_data.get('description', 'N/A')}\n\n"
        
        # Avaliação de Riscos
        if "risk_assessment" in predictive_insights:
            risks = predictive_insights["risk_assessment"]
            section += "### ⚖️ Avaliação de Riscos e Oportunidades\n\n"
            
            if "identified_risks" in risks:
                section += "**Riscos Identificados:**\n"
                for risk in risks["identified_risks"][:5]:
                    if isinstance(risk, dict):
                        section += f"- {risk.get('risk', 'Risco')}: {risk.get('severity', 'N/A')} (Probabilidade: {risk.get('probability', 'N/A')})\n"
                    else:
                        section += f"- {risk}\n"
                section += "\n"
            
            if "opportunities" in risks:
                section += "**Oportunidades Estratégicas:**\n"
                for opp in risks["opportunities"][:5]:
                    if isinstance(opp, dict):
                        section += f"- {opp.get('opportunity', 'Oportunidade')}: {opp.get('potential', 'N/A')} (Viabilidade: {opp.get('feasibility', 'N/A')})\n"
                    else:
                        section += f"- {opp}\n"
                section += "\n"
        
        # Recomendações Estratégicas
        if "strategic_recommendations" in predictive_insights:
            recommendations = predictive_insights["strategic_recommendations"]
            section += "### 💡 Recomendações Estratégicas Baseadas em IA\n\n"
            
            if "immediate_actions" in recommendations:
                section += "**Ações Imediatas (0-30 dias):**\n"
                for action in recommendations["immediate_actions"][:5]:
                    if isinstance(action, dict):
                        section += f"- {action.get('action', 'Ação')}: {action.get('description', 'N/A')}\n"
                    else:
                        section += f"- {action}\n"
                section += "\n"
            
            if "medium_term_actions" in recommendations:
                section += "**Ações de Médio Prazo (1-6 meses):**\n"
                for action in recommendations["medium_term_actions"][:5]:
                    if isinstance(action, dict):
                        section += f"- {action.get('action', 'Ação')}: {action.get('description', 'N/A')}\n"
                    else:
                        section += f"- {action}\n"
                section += "\n"
        
        # Métricas de Confiança
        if "confidence_metrics" in predictive_insights:
            confidence = predictive_insights["confidence_metrics"]
            section += "### 📏 Métricas de Confiança da Análise\n\n"
            section += f"**Confiança Geral:** {confidence.get('overall_confidence', 'N/A')}\n"
            section += f"**Qualidade dos Dados:** {confidence.get('data_quality_score', 'N/A')}\n"
            section += f"**Cobertura da Análise:** {confidence.get('analysis_coverage', 'N/A')}\n\n"
        
        section += "---\n\n"
        return section

# Instância global
comprehensive_report_generator_v3 = ComprehensiveReportGeneratorV3()
