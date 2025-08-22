#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRT Busca - TrendFinder MCP Client
Cliente para análise de tendências via MCP
"""

import os
import logging
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TrendFinderClient:
    """Cliente para TrendFinder MCP"""

    def __init__(self):
        """Inicializa o cliente TrendFinder"""
        self.mcp_url = os.getenv('TRENDFINDER_MCP_URL')
        self.timeout = 60
        
        if not self.mcp_url:
            logger.warning("⚠️ TRENDFINDER_MCP_URL não configurado")
        else:
            logger.info(f"📈 TrendFinder Client inicializado: {self.mcp_url}")

    async def search(self, query: str, region: str = "BR") -> Dict[str, Any]:
        """
        Busca tendências relacionadas ao query
        
        Args:
            query: Termo de busca
            region: Região para análise (padrão: BR)
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'TRENDFINDER_MCP_URL não configurado',
                'source': 'TrendFinder'
            }

        try:
            logger.info(f"📈 Buscando tendências para: {query} (região: {region})")
            
            payload = {
                'method': 'trend_search',
                'params': {
                    'query': query,
                    'region': region,
                    'timeframe': '12m',  # últimos 12 meses
                    'category': 'all',
                    'include_related': True,
                    'include_rising': True
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'PRT-Busca-TrendFinder/1.0'
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    trends_data = {
                        'success': True,
                        'source': 'TrendFinder',
                        'query': query,
                        'region': region,
                        'timestamp': datetime.now().isoformat(),
                        'trends': data.get('result', {}).get('trends', []),
                        'related_queries': data.get('result', {}).get('related_queries', []),
                        'rising_queries': data.get('result', {}).get('rising_queries', []),
                        'interest_over_time': data.get('result', {}).get('interest_over_time', []),
                        'regional_interest': data.get('result', {}).get('regional_interest', []),
                        'top_charts': data.get('result', {}).get('top_charts', []),
                        'trending_searches': data.get('result', {}).get('trending_searches', [])
                    }
                    
                    logger.info(f"✅ TrendFinder: {len(trends_data['trends'])} tendências encontradas")
                    return trends_data
                    
                else:
                    error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ TrendFinder erro: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'source': 'TrendFinder'
                    }
                    
        except httpx.TimeoutException:
            error_msg = f"Timeout após {self.timeout}s"
            logger.error(f"❌ TrendFinder timeout: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'TrendFinder'
            }
            
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ TrendFinder erro: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'source': 'TrendFinder'
            }

    async def get_trending_topics(self, category: str = "all", region: str = "BR") -> Dict[str, Any]:
        """
        Obtém tópicos em alta
        
        Args:
            category: Categoria dos tópicos
            region: Região para análise
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'TRENDFINDER_MCP_URL não configurado',
                'source': 'TrendFinder'
            }

        try:
            payload = {
                'method': 'trending_topics',
                'params': {
                    'category': category,
                    'region': region,
                    'timeframe': 'now',
                    'limit': 50
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'source': 'TrendFinder',
                        'trending_topics': data.get('result', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'source': 'TrendFinder'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'TrendFinder'
            }

    async def compare_trends(self, queries: List[str], region: str = "BR") -> Dict[str, Any]:
        """
        Compara tendências entre múltiplos termos
        
        Args:
            queries: Lista de termos para comparar
            region: Região para análise
        """
        if not self.mcp_url:
            return {
                'success': False,
                'error': 'TRENDFINDER_MCP_URL não configurado',
                'source': 'TrendFinder'
            }

        try:
            payload = {
                'method': 'compare_trends',
                'params': {
                    'queries': queries,
                    'region': region,
                    'timeframe': '12m',
                    'include_forecast': True
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.mcp_url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'success': True,
                        'source': 'TrendFinder',
                        'comparison_data': data.get('result', {}),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'success': False,
                        'error': f"HTTP {response.status_code}",
                        'source': 'TrendFinder'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'source': 'TrendFinder'
            }

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível"""
        return bool(self.mcp_url)

# Instância global
trendfinder_client = TrendFinderClient()

