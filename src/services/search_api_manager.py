#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRT Busca - Search API Manager
Gerenciador de APIs de busca com rotação automática
"""

import os
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SearchAPIManager:
    """Gerenciador de APIs de busca com rotação automática"""

    def __init__(self):
        """Inicializa o gerenciador"""
        self.api_keys = self._load_api_keys()
        self.key_indices = {provider: 0 for provider in self.api_keys.keys()}
        self.provider_stats = {}
        
        logger.info(f"🔍 Search API Manager inicializado com {sum(len(keys) for keys in self.api_keys.values())} chaves")

    def _load_api_keys(self) -> Dict[str, List[str]]:
        """Carrega chaves de API do ambiente"""
        api_keys = {}
        
        providers = ['SERPER', 'GOOGLE', 'EXA', 'FIRECRAWL', 'JINA']
        
        for provider in providers:
            keys = []
            
            # Chave principal
            main_key = os.getenv(f"{provider}_API_KEY")
            if main_key:
                keys.append(main_key)
            
            # Chaves numeradas
            counter = 1
            while True:
                numbered_key = os.getenv(f"{provider}_API_KEY_{counter}")
                if numbered_key:
                    keys.append(numbered_key)
                    counter += 1
                else:
                    break
            
            if keys:
                api_keys[provider] = keys
                logger.info(f"✅ {provider}: {len(keys)} chaves carregadas")
        
        return api_keys

    def get_next_api_key(self, provider: str) -> Optional[str]:
        """Obtém próxima chave com rotação"""
        if provider not in self.api_keys or not self.api_keys[provider]:
            return None
        
        keys = self.api_keys[provider]
        current_index = self.key_indices[provider]
        
        key = keys[current_index]
        self.key_indices[provider] = (current_index + 1) % len(keys)
        
        # Atualiza estatísticas
        if provider not in self.provider_stats:
            self.provider_stats[provider] = {'requests': 0, 'successes': 0, 'failures': 0}
        self.provider_stats[provider]['requests'] += 1
        
        return key

    async def interleaved_search(self, query: str) -> Dict[str, Any]:
        """Executa busca intercalada com múltiplos provedores"""
        logger.info(f"🔍 Iniciando busca intercalada para: {query}")
        
        search_results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'all_results': [],
            'successful_searches': 0,
            'failed_searches': 0,
            'consolidated_urls': []
        }
        
        # Define provedores e suas funções
        search_tasks = []
        
        if 'SERPER' in self.api_keys:
            search_tasks.append(('SERPER', self._search_serper(query)))
        
        if 'GOOGLE' in self.api_keys:
            search_tasks.append(('GOOGLE', self._search_google(query)))
        
        if 'EXA' in self.api_keys:
            search_tasks.append(('EXA', self._search_exa(query)))
        
        if 'FIRECRAWL' in self.api_keys:
            search_tasks.append(('FIRECRAWL', self._search_firecrawl(query)))
        
        if 'JINA' in self.api_keys:
            search_tasks.append(('JINA', self._search_jina(query)))
        
        # Executa buscas em paralelo
        if search_tasks:
            tasks = [task[1] for task in search_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(results):
                provider_name = search_tasks[i][0]
                
                if isinstance(result, Exception):
                    logger.error(f"❌ Erro em {provider_name}: {result}")
                    search_results['failed_searches'] += 1
                    self.provider_stats[provider_name]['failures'] += 1
                    continue
                
                if result.get('success'):
                    search_results['all_results'].append(result)
                    search_results['successful_searches'] += 1
                    self.provider_stats[provider_name]['successes'] += 1
                    
                    # Coleta URLs
                    for item in result.get('results', []):
                        url = item.get('url') or item.get('link')
                        if url and url not in search_results['consolidated_urls']:
                            search_results['consolidated_urls'].append(url)
                else:
                    search_results['failed_searches'] += 1
                    self.provider_stats[provider_name]['failures'] += 1
        
        logger.info(f"✅ Busca intercalada concluída: {search_results['successful_searches']} sucessos")
        return search_results

    async def _search_serper(self, query: str) -> Dict[str, Any]:
        """Busca usando Serper API"""
        try:
            api_key = self.get_next_api_key('SERPER')
            if not api_key:
                return {'success': False, 'error': 'Serper API key não disponível'}
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'X-API-KEY': api_key,
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'q': f"{query} Brasil",
                    'gl': 'br',
                    'hl': 'pt',
                    'num': 15
                }
                
                async with session.post(
                    'https://google.serper.dev/search',
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('organic', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'serper'
                            })
                        
                        return {
                            'success': True,
                            'provider': 'SERPER',
                            'results': results
                        }
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            logger.error(f"❌ Erro Serper: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_google(self, query: str) -> Dict[str, Any]:
        """Busca usando Google Custom Search"""
        try:
            api_key = self.get_next_api_key('GOOGLE')
            cse_id = os.getenv('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                return {'success': False, 'error': 'Google API não configurado'}
            
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': api_key,
                    'cx': cse_id,
                    'q': f"{query} Brasil",
                    'num': 10,
                    'gl': 'br',
                    'hl': 'pt'
                }
                
                async with session.get(
                    'https://www.googleapis.com/customsearch/v1',
                    params=params,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('items', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('link', ''),
                                'snippet': item.get('snippet', ''),
                                'source': 'google'
                            })
                        
                        return {
                            'success': True,
                            'provider': 'GOOGLE',
                            'results': results
                        }
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            logger.error(f"❌ Erro Google: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_exa(self, query: str) -> Dict[str, Any]:
        """Busca usando Exa Neural Search"""
        try:
            api_key = self.get_next_api_key('EXA')
            if not api_key:
                return {'success': False, 'error': 'Exa API key não disponível'}
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'x-api-key': api_key,
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'query': f"{query} Brasil mercado",
                    'numResults': 10,
                    'useAutoprompt': True,
                    'type': 'neural'
                }
                
                async with session.post(
                    'https://api.exa.ai/search',
                    json=payload,
                    headers=headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = []
                        
                        for item in data.get('results', []):
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('text', '')[:300],
                                'source': 'exa'
                            })
                        
                        return {
                            'success': True,
                            'provider': 'EXA',
                            'results': results
                        }
                    else:
                        return {'success': False, 'error': f'HTTP {response.status}'}
        
        except Exception as e:
            logger.error(f"❌ Erro Exa: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_firecrawl(self, query: str) -> Dict[str, Any]:
        """Busca usando Firecrawl"""
        try:
            api_key = self.get_next_api_key('FIRECRAWL')
            if not api_key:
                return {'success': False, 'error': 'Firecrawl API key não disponível'}
            
            # Firecrawl é usado para extrair conteúdo, não para busca direta
            # Retorna resultado vazio por enquanto
            return {
                'success': True,
                'provider': 'FIRECRAWL',
                'results': []
            }
        
        except Exception as e:
            logger.error(f"❌ Erro Firecrawl: {e}")
            return {'success': False, 'error': str(e)}

    async def _search_jina(self, query: str) -> Dict[str, Any]:
        """Busca usando Jina AI"""
        try:
            api_key = self.get_next_api_key('JINA')
            if not api_key:
                return {'success': False, 'error': 'Jina API key não disponível'}
            
            # Jina é usado para leitura de conteúdo, não busca direta
            # Retorna resultado vazio por enquanto
            return {
                'success': True,
                'provider': 'JINA',
                'results': []
            }
        
        except Exception as e:
            logger.error(f"❌ Erro Jina: {e}")
            return {'success': False, 'error': str(e)}

    def get_provider_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas dos provedores"""
        return self.provider_stats.copy()

# Instância global
search_api_manager = SearchAPIManager()

