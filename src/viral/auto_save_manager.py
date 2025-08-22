"""
Auto Save Manager - Sistema de salvamento automático ultra-robusto
Responsável por salvar dados intermediários e gerenciar cache
"""

import os
import json
import asyncio
import pickle
import gzip
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import time
import shutil
from pathlib import Path
import sqlite3
import logging


@dataclass
class SavedData:
    """Estrutura para dados salvos"""
    id: str
    data_type: str
    content: Any
    metadata: Dict[str, Any]
    timestamp: str
    size_bytes: int
    checksum: str


@dataclass
class CacheEntry:
    """Entrada de cache"""
    key: str
    value: Any
    expiry: datetime
    access_count: int
    last_accessed: datetime


class AutoSaveManager:
    """
    Sistema de salvamento automático ultra-robusto
    """
    
    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.join(os.getcwd(), 'analyses_data')
        self.cache_dir = os.path.join(self.base_dir, 'cache')
        self.backup_dir = os.path.join(self.base_dir, 'backups')
        self.temp_dir = os.path.join(self.base_dir, 'temp')
        
        # Cria diretórios necessários
        for directory in [self.base_dir, self.cache_dir, self.backup_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Cache em memória
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.cache_lock = threading.RLock()
        
        # Configurações
        self.max_cache_size = 1000  # Máximo de entradas em cache
        self.cache_cleanup_interval = 300  # 5 minutos
        self.backup_interval = 3600  # 1 hora
        self.compression_enabled = True
        
        # Database para metadados
        self.db_path = os.path.join(self.base_dir, 'metadata.db')
        self._init_database()
        
        # Thread para limpeza automática
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        
        # Configuração de logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """Inicializa database SQLite para metadados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS saved_data (
                id TEXT PRIMARY KEY,
                data_type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                size_bytes INTEGER,
                checksum TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                expiry DATETIME,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def save_data(self, data_id: str, data_type: str, content: Any, 
                       metadata: Dict[str, Any] = None) -> SavedData:
        """
        Salva dados com backup automático
        """
        if metadata is None:
            metadata = {}
        
        timestamp = datetime.now().isoformat()
        
        # Serializa conteúdo
        if isinstance(content, (dict, list)):
            serialized_content = json.dumps(content, ensure_ascii=False, indent=2)
            file_extension = '.json'
        else:
            serialized_content = pickle.dumps(content)
            file_extension = '.pkl'
        
        # Compressão opcional
        if self.compression_enabled and len(serialized_content) > 1024:  # > 1KB
            if isinstance(serialized_content, str):
                serialized_content = serialized_content.encode('utf-8')
            serialized_content = gzip.compress(serialized_content)
            file_extension += '.gz'
        
        # Calcula checksum
        if isinstance(serialized_content, str):
            checksum = hashlib.md5(serialized_content.encode('utf-8')).hexdigest()
        else:
            checksum = hashlib.md5(serialized_content).hexdigest()
        
        # Define caminho do arquivo
        safe_id = self._sanitize_filename(data_id)
        filename = f"{safe_id}_{data_type}_{int(time.time())}{file_extension}"
        file_path = os.path.join(self.base_dir, filename)
        
        # Salva arquivo
        try:
            if isinstance(serialized_content, str):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(serialized_content)
            else:
                with open(file_path, 'wb') as f:
                    f.write(serialized_content)
            
            size_bytes = os.path.getsize(file_path)
            
            # Salva metadados no database
            self._save_metadata_to_db(data_id, data_type, file_path, metadata, 
                                    timestamp, size_bytes, checksum)
            
            saved_data = SavedData(
                id=data_id,
                data_type=data_type,
                content=content,
                metadata=metadata,
                timestamp=timestamp,
                size_bytes=size_bytes,
                checksum=checksum
            )
            
            self.logger.info(f"Dados salvos: {data_id} ({size_bytes} bytes)")
            
            # Backup automático para dados importantes
            if data_type in ['analysis_results', 'final_report']:
                await self._create_backup(file_path)
            
            return saved_data
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados {data_id}: {e}")
            raise
    
    async def load_data(self, data_id: str, data_type: str = None) -> Optional[SavedData]:
        """
        Carrega dados salvos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if data_type:
                cursor.execute(
                    'SELECT * FROM saved_data WHERE id = ? AND data_type = ? ORDER BY created_at DESC LIMIT 1',
                    (data_id, data_type)
                )
            else:
                cursor.execute(
                    'SELECT * FROM saved_data WHERE id = ? ORDER BY created_at DESC LIMIT 1',
                    (data_id,)
                )
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            _, data_type, file_path, metadata_json, timestamp, size_bytes, checksum = row
            
            if not os.path.exists(file_path):
                self.logger.warning(f"Arquivo não encontrado: {file_path}")
                return None
            
            # Carrega conteúdo
            content = await self._load_file_content(file_path)
            
            # Verifica integridade
            if not self._verify_checksum(content, checksum):
                self.logger.warning(f"Checksum inválido para {data_id}")
            
            metadata = json.loads(metadata_json) if metadata_json else {}
            
            return SavedData(
                id=data_id,
                data_type=data_type,
                content=content,
                metadata=metadata,
                timestamp=timestamp,
                size_bytes=size_bytes,
                checksum=checksum
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados {data_id}: {e}")
            return None
    
    async def cache_set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """
        Define valor no cache com TTL
        """
        with self.cache_lock:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            
            self.memory_cache[key] = CacheEntry(
                key=key,
                value=value,
                expiry=expiry,
                access_count=0,
                last_accessed=datetime.now()
            )
            
            # Salva no disco para persistência
            await self._save_cache_to_disk(key, value, expiry)
            
            # Limpa cache se necessário
            if len(self.memory_cache) > self.max_cache_size:
                self._cleanup_cache()
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        """
        with self.cache_lock:
            # Verifica cache em memória
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                if datetime.now() < entry.expiry:
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    return entry.value
                else:
                    # Remove entrada expirada
                    del self.memory_cache[key]
            
            # Tenta carregar do disco
            cached_value = await self._load_cache_from_disk(key)
            if cached_value:
                # Adiciona de volta ao cache em memória
                self.memory_cache[key] = CacheEntry(
                    key=key,
                    value=cached_value,
                    expiry=datetime.now() + timedelta(hours=1),  # TTL padrão
                    access_count=1,
                    last_accessed=datetime.now()
                )
                return cached_value
            
            return None
    
    async def cache_delete(self, key: str):
        """
        Remove entrada do cache
        """
        with self.cache_lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remove do disco
            await self._delete_cache_from_disk(key)
    
    async def get_analysis_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna histórico de análises
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, data_type, metadata, timestamp, size_bytes
                FROM saved_data 
                WHERE data_type IN ('analysis_results', 'search_results', 'social_results')
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            history = []
            for row in rows:
                data_id, data_type, metadata_json, timestamp, size_bytes = row
                metadata = json.loads(metadata_json) if metadata_json else {}
                
                history.append({
                    'id': data_id,
                    'type': data_type,
                    'metadata': metadata,
                    'timestamp': timestamp,
                    'size_bytes': size_bytes
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Erro ao obter histórico: {e}")
            return []
    
    async def cleanup_old_data(self, days_old: int = 30):
        """
        Remove dados antigos
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Busca arquivos antigos
            cursor.execute(
                'SELECT file_path FROM saved_data WHERE created_at < ?',
                (cutoff_date.isoformat(),)
            )
            
            old_files = cursor.fetchall()
            
            # Remove arquivos
            removed_count = 0
            for (file_path,) in old_files:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed_count += 1
            
            # Remove registros do database
            cursor.execute('DELETE FROM saved_data WHERE created_at < ?', (cutoff_date.isoformat(),))
            conn.commit()
            conn.close()
            
            self.logger.info(f"Removidos {removed_count} arquivos antigos")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {e}")
    
    async def create_full_backup(self) -> str:
        """
        Cria backup completo do sistema
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"prt_busca_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Cria diretório de backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Copia database
            shutil.copy2(self.db_path, os.path.join(backup_path, 'metadata.db'))
            
            # Copia arquivos de dados
            data_backup_dir = os.path.join(backup_path, 'data')
            os.makedirs(data_backup_dir, exist_ok=True)
            
            for filename in os.listdir(self.base_dir):
                file_path = os.path.join(self.base_dir, filename)
                if os.path.isfile(file_path) and filename != 'metadata.db':
                    shutil.copy2(file_path, data_backup_dir)
            
            # Comprime backup
            archive_path = f"{backup_path}.tar.gz"
            shutil.make_archive(backup_path, 'gztar', backup_path)
            
            # Remove diretório temporário
            shutil.rmtree(backup_path)
            
            self.logger.info(f"Backup criado: {archive_path}")
            return archive_path
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            raise
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de armazenamento
        """
        try:
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(self.base_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        total_size += os.path.getsize(file_path)
                        file_count += 1
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM saved_data')
            saved_data_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM cache_entries')
            cache_entries_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'saved_data_count': saved_data_count,
                'cache_entries_count': cache_entries_count,
                'memory_cache_size': len(self.memory_cache),
                'directories': {
                    'base': self.base_dir,
                    'cache': self.cache_dir,
                    'backup': self.backup_dir,
                    'temp': self.temp_dir
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitiza nome do arquivo"""
        import re
        # Remove caracteres especiais
        sanitized = re.sub(r'[^\w\-_.]', '_', filename)
        # Limita tamanho
        return sanitized[:100]
    
    def _save_metadata_to_db(self, data_id: str, data_type: str, file_path: str,
                           metadata: Dict[str, Any], timestamp: str, 
                           size_bytes: int, checksum: str):
        """Salva metadados no database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO saved_data 
            (id, data_type, file_path, metadata, timestamp, size_bytes, checksum)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (data_id, data_type, file_path, json.dumps(metadata), 
              timestamp, size_bytes, checksum))
        
        conn.commit()
        conn.close()
    
    async def _load_file_content(self, file_path: str) -> Any:
        """Carrega conteúdo do arquivo"""
        try:
            # Verifica se é arquivo comprimido
            if file_path.endswith('.gz'):
                with gzip.open(file_path, 'rb') as f:
                    content = f.read()
                
                # Tenta decodificar como JSON
                if file_path.endswith('.json.gz'):
                    return json.loads(content.decode('utf-8'))
                else:
                    return pickle.loads(content)
            
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif file_path.endswith('.pkl'):
                with open(file_path, 'rb') as f:
                    return pickle.load(f)
            
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            self.logger.error(f"Erro ao carregar arquivo {file_path}: {e}")
            raise
    
    def _verify_checksum(self, content: Any, expected_checksum: str) -> bool:
        """Verifica integridade dos dados"""
        try:
            if isinstance(content, str):
                actual_checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
            else:
                serialized = pickle.dumps(content)
                actual_checksum = hashlib.md5(serialized).hexdigest()
            
            return actual_checksum == expected_checksum
        except:
            return False
    
    async def _save_cache_to_disk(self, key: str, value: Any, expiry: datetime):
        """Salva entrada de cache no disco"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{hashlib.md5(key.encode()).hexdigest()}.cache")
            
            cache_data = {
                'key': key,
                'value': value,
                'expiry': expiry.isoformat()
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            # Salva metadados no database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO cache_entries (key, file_path, expiry)
                VALUES (?, ?, ?)
            ''', (key, cache_file, expiry.isoformat()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache {key}: {e}")
    
    async def _load_cache_from_disk(self, key: str) -> Optional[Any]:
        """Carrega entrada de cache do disco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT file_path, expiry FROM cache_entries WHERE key = ?',
                (key,)
            )
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return None
            
            file_path, expiry_str = row
            expiry = datetime.fromisoformat(expiry_str)
            
            if datetime.now() >= expiry:
                # Cache expirado
                await self._delete_cache_from_disk(key)
                return None
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            return cache_data['value']
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar cache {key}: {e}")
            return None
    
    async def _delete_cache_from_disk(self, key: str):
        """Remove entrada de cache do disco"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT file_path FROM cache_entries WHERE key = ?', (key,))
            row = cursor.fetchone()
            
            if row:
                file_path = row[0]
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            cursor.execute('DELETE FROM cache_entries WHERE key = ?', (key,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Erro ao deletar cache {key}: {e}")
    
    async def _create_backup(self, file_path: str):
        """Cria backup de arquivo importante"""
        try:
            filename = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, f"backup_{int(time.time())}_{filename}")
            shutil.copy2(file_path, backup_path)
            self.logger.info(f"Backup criado: {backup_path}")
        except Exception as e:
            self.logger.error(f"Erro ao criar backup de {file_path}: {e}")
    
    def _cleanup_cache(self):
        """Limpa cache em memória baseado em LRU"""
        if len(self.memory_cache) <= self.max_cache_size:
            return
        
        # Ordena por último acesso
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].last_accessed
        )
        
        # Remove 25% das entradas mais antigas
        remove_count = len(self.memory_cache) // 4
        for key, _ in sorted_entries[:remove_count]:
            del self.memory_cache[key]
    
    def _cleanup_worker(self):
        """Worker thread para limpeza automática"""
        while True:
            try:
                time.sleep(self.cache_cleanup_interval)
                
                # Limpa cache expirado
                with self.cache_lock:
                    expired_keys = []
                    for key, entry in self.memory_cache.items():
                        if datetime.now() >= entry.expiry:
                            expired_keys.append(key)
                    
                    for key in expired_keys:
                        del self.memory_cache[key]
                
                # Limpa arquivos temporários antigos
                temp_cutoff = datetime.now() - timedelta(hours=24)
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if file_time < temp_cutoff:
                            os.remove(file_path)
                
            except Exception as e:
                self.logger.error(f"Erro no worker de limpeza: {e}")
                time.sleep(60)  # Espera 1 minuto antes de tentar novamente

