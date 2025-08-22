#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRT Busca - Exa Client Stub
Cliente stub para Exa (não implementado)
"""

import logging

logger = logging.getLogger(__name__)

class ExaClient:
    """Cliente stub para Exa"""
    
    def __init__(self):
        self.enabled = False
        logger.warning("⚠️ Exa Client é um stub - não implementado")
    
    def is_available(self):
        """Verifica se o cliente está disponível"""
        return False
    
    def search(self, query):
        return {"success": False, "error": "Exa não implementado"}

# Instância global
exa_client = ExaClient()

def extract_content_with_exa(url):
    """Função stub para extração com Exa"""
    return {"success": False, "error": "Exa não implementado"}

