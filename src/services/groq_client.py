#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRT Busca - Groq Client Stub
Cliente stub para Groq (não implementado)
"""

import logging

logger = logging.getLogger(__name__)

class GroqClient:
    """Cliente stub para Groq"""
    
    def __init__(self):
        self.enabled = False
        logger.warning("⚠️ Groq Client é um stub - não implementado")
    
    def generate(self, prompt):
        return {"success": False, "error": "Groq não implementado"}

# Instância global
groq_client = GroqClient()

