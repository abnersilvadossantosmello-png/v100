#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRT Busca - Selenium Checker
Verificador de configuração do Selenium
"""

import os
import logging
import shutil

logger = logging.getLogger(__name__)

class SeleniumChecker:
    """Verificador de configuração do Selenium"""
    
    def __init__(self):
        self.chrome_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/chromium-browser',
            '/usr/bin/chromium',
            '/snap/bin/chromium'
        ]
    
    def full_check(self):
        """Executa verificação completa do Selenium"""
        try:
            # Verifica se Chrome está disponível
            best_chrome_path = None
            for path in self.chrome_paths:
                if os.path.exists(path):
                    best_chrome_path = path
                    break
            
            # Verifica chromedriver
            chromedriver_available = shutil.which('chromedriver') is not None
            
            selenium_ready = best_chrome_path is not None and chromedriver_available
            
            return {
                'selenium_ready': selenium_ready,
                'best_chrome_path': best_chrome_path,
                'chromedriver_available': chromedriver_available
            }
        except Exception as e:
            logger.error(f"Erro na verificação do Selenium: {e}")
            return {
                'selenium_ready': False,
                'best_chrome_path': None,
                'chromedriver_available': False
            }

# Instância global
selenium_checker = SeleniumChecker()

