"""
Memory Bot - Data management and intelligent caching system for TradeMasterX 2.0

This bot manages:
- Market data caching and retrieval
- Bot performance history
- Model states and checkpoints
- Configuration snapshots
- Memory optimization and cleanup
"""

import asyncio
import logging
import json
import pickle
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd
import numpy as np
from threading import Lock
import redis
from cachetools import TTLCache, LRUCache

from ...core.bot_registry import BaseBot


@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    memory_usage: float = 0.0
    last_updated: datetime = None
    
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


@dataclass
class DataEntry:
    """Generic data entry with metadata"""
    key: str
    data: Any
    timestamp: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    data_type: str = "unknown"
    size_bytes: int = 0
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
        if not self.size_bytes:
            self.size_bytes = self._calculate_size()
    
    def _calculate_checksum(self) -> str:
        """Calculate data checksum for integrity"""
        try:
            if isinstance(self.data, (dict, list)):
                data_str = json.dumps(self.data, sort_keys=True)
            elif isinstance(self.data, pd.DataFrame):
                data_str = self.data.to_string()
            else:
                data_str = str(self.data)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception:
            return "unknown"
    
    def _calculate_size(self) -> int:
        """Calculate approximate data size in bytes"""
        try:
            if isinstance(self.data, (dict, list)):
                return len(json.dumps(self.data).encode())
            elif isinstance(self.data, pd.DataFrame):
                return self.data.memory_usage(deep=True).sum()
            elif isinstance(self.data, str):
                return len(self.data.encode())
            else:
                return len(pickle.dumps(self.data))
        except Exception:
            return 0


class MemoryBot(BaseBot):
    """Intelligent memory management and caching system"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.max_memory_mb = config.get('max_memory_mb', 512)
        self.cache_ttl_hours = config.get('cache_ttl_hours', 24)
        self.cleanup_interval_minutes = config.get('cleanup_interval_minutes', 30)
        self.use_redis = config.get('use_redis', False)
        self.redis_url = config.get('redis_url', 'redis://localhost:6379')
        self.db_path = config.get('db_path', 'data/memory_bot.db')
        
        # Storage systems
        self._memory_cache = TTLCache(
            maxsize=1000,
            ttl=self.cache_ttl_hours * 3600
        )
        self._lru_cache = LRUCache(maxsize=500)
        self._persistent_storage = None
        self._redis_client = None
        
        # Metrics and monitoring
        self.metrics = CacheMetrics()
        self._lock = Lock()
        self._last_cleanup = datetime.now()
        
        # Data categories
        self.data_categories = {
            'market_data': {'ttl_hours': 1, 'priority': 'high'},
            'bot_performance': {'ttl_hours': 24, 'priority': 'medium'},
            'model_states': {'ttl_hours': 168, 'priority': 'high'},  # 1 week
            'configuration': {'ttl_hours': 48, 'priority': 'medium'},
            'analytics': {'ttl_hours': 6, 'priority': 'low'},
            'temp_data': {'ttl_hours': 1, 'priority': 'low'}
        }
        
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage backends"""
        try:
            # Initialize SQLite for persistent storage
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._persistent_storage = sqlite3.connect(
                self.db_path, 
                check_same_thread=False
            )
            self._create_tables()
            
            # Initialize Redis if enabled
            if self.use_redis:
                try:
                    import redis
                    self._redis_client = redis.from_url(self.redis_url)
                    self._redis_client.ping()
                    self.logger.info("Redis connection established")
                except Exception as e:
                    self.logger.warning(f"Redis connection failed: {e}")
                    self._redis_client = None
            
            self.logger.info("Memory storage systems initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables"""
        cursor = self._persistent_storage.cursor()
        
        # Main data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_entries (
                key TEXT PRIMARY KEY,
                data BLOB,
                timestamp TEXT,
                expires_at TEXT,
                access_count INTEGER DEFAULT 0,
                data_type TEXT,
                size_bytes INTEGER,
                checksum TEXT
            )
        """)
        
        # Cache metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cache_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                hits INTEGER,
                misses INTEGER,
                evictions INTEGER,
                memory_usage REAL
            )
        """)
        
        # Bot performance history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bot_performance (
                bot_id TEXT,
                timestamp TEXT,
                metrics TEXT,
                PRIMARY KEY (bot_id, timestamp)
            )
        """)
        
        self._persistent_storage.commit()
    
    async def start(self) -> bool:
        """Start the memory bot"""
        try:
            self.is_running = True
            self.logger.info("Starting MemoryBot")
            
            # Start cleanup task
            asyncio.create_task(self._cleanup_loop())
            
            # Load cached data from persistent storage
            await self._load_persistent_cache()
            
            self.logger.info("MemoryBot started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start MemoryBot: {e}")
            return False
    
    async def stop(self) -> bool:
        """Stop the memory bot"""
        try:
            self.is_running = False
            
            # Save cache to persistent storage
            await self._save_cache_to_persistent()
            
            # Close connections
            if self._persistent_storage:
                self._persistent_storage.close()
            
            if self._redis_client:
                self._redis_client.close()
            
            self.logger.info("MemoryBot stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping MemoryBot: {e}")
            return False
    
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data and manage caching"""
        try:
            action = data.get('action', 'store')
            
            if action == 'store':
                return await self._store_data(data)
            elif action == 'retrieve':
                return await self._retrieve_data(data)
            elif action == 'delete':
                return await self._delete_data(data)
            elif action == 'cleanup':
                return await self._perform_cleanup()
            elif action == 'get_metrics':
                return await self._get_metrics()
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}
                
        except Exception as e:
            self.logger.error(f"Error processing data: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _store_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Store data in appropriate cache layer"""
        try:
            key = request['key']
            data = request['data']
            data_type = request.get('data_type', 'unknown')
            priority = request.get('priority', 'medium')
            ttl_hours = request.get('ttl_hours')
            
            # Determine TTL based on data type
            if not ttl_hours and data_type in self.data_categories:
                ttl_hours = self.data_categories[data_type]['ttl_hours']
            elif not ttl_hours:
                ttl_hours = self.cache_ttl_hours
            
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            # Create data entry
            entry = DataEntry(
                key=key,
                data=data,
                timestamp=datetime.now(),
                expires_at=expires_at,
                data_type=data_type
            )
            
            # Store in appropriate cache layers
            with self._lock:
                # Always store in memory cache
                self._memory_cache[key] = entry
                
                # Store in LRU cache for frequently accessed data
                if priority in ['high', 'medium']:
                    self._lru_cache[key] = entry
                
                # Store in Redis if available and high priority
                if self._redis_client and priority == 'high':
                    await self._store_in_redis(key, entry)
                
                # Store in persistent storage for important data
                if data_type in ['model_states', 'bot_performance', 'configuration']:
                    await self._store_in_persistent(key, entry)
            
            self.logger.debug(f"Stored data: {key} ({data_type})")
            return {'success': True, 'key': key, 'expires_at': expires_at.isoformat()}
            
        except Exception as e:
            self.logger.error(f"Error storing data: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _retrieve_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve data from cache layers"""
        try:
            key = request['key']
            
            with self._lock:
                # Check memory cache first
                if key in self._memory_cache:
                    entry = self._memory_cache[key]
                    entry.access_count += 1
                    self.metrics.hits += 1
                    return {
                        'success': True,
                        'data': entry.data,
                        'metadata': {
                            'source': 'memory',
                            'timestamp': entry.timestamp.isoformat(),
                            'access_count': entry.access_count
                        }
                    }
                
                # Check LRU cache
                if key in self._lru_cache:
                    entry = self._lru_cache[key]
                    entry.access_count += 1
                    self.metrics.hits += 1
                    # Promote to memory cache
                    self._memory_cache[key] = entry
                    return {
                        'success': True,
                        'data': entry.data,
                        'metadata': {
                            'source': 'lru',
                            'timestamp': entry.timestamp.isoformat(),
                            'access_count': entry.access_count
                        }
                    }
                
                # Check Redis
                if self._redis_client:
                    entry = await self._retrieve_from_redis(key)
                    if entry:
                        entry.access_count += 1
                        self.metrics.hits += 1
                        # Promote to memory cache
                        self._memory_cache[key] = entry
                        return {
                            'success': True,
                            'data': entry.data,
                            'metadata': {
                                'source': 'redis',
                                'timestamp': entry.timestamp.isoformat(),
                                'access_count': entry.access_count
                            }
                        }
                
                # Check persistent storage
                entry = await self._retrieve_from_persistent(key)
                if entry:
                    entry.access_count += 1
                    self.metrics.hits += 1
                    # Promote to memory cache
                    self._memory_cache[key] = entry
                    return {
                        'success': True,
                        'data': entry.data,
                        'metadata': {
                            'source': 'persistent',
                            'timestamp': entry.timestamp.isoformat(),
                            'access_count': entry.access_count
                        }
                    }
                
                # Data not found
                self.metrics.misses += 1
                return {'success': False, 'error': 'Data not found'}
                
        except Exception as e:
            self.logger.error(f"Error retrieving data: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _delete_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Delete data from all cache layers"""
        try:
            key = request['key']
            
            with self._lock:
                # Remove from memory caches
                self._memory_cache.pop(key, None)
                self._lru_cache.pop(key, None)
                
                # Remove from Redis
                if self._redis_client:
                    await self._delete_from_redis(key)
                
                # Remove from persistent storage
                await self._delete_from_persistent(key)
            
            return {'success': True, 'key': key}
            
        except Exception as e:
            self.logger.error(f"Error deleting data: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _store_in_redis(self, key: str, entry: DataEntry):
        """Store data entry in Redis"""
        try:
            serialized = pickle.dumps(entry)
            ttl_seconds = int((entry.expires_at - datetime.now()).total_seconds())
            if ttl_seconds > 0:
                self._redis_client.setex(f"tmx:{key}", ttl_seconds, serialized)
        except Exception as e:
            self.logger.warning(f"Failed to store in Redis: {e}")
    
    async def _retrieve_from_redis(self, key: str) -> Optional[DataEntry]:
        """Retrieve data entry from Redis"""
        try:
            data = self._redis_client.get(f"tmx:{key}")
            if data:
                return pickle.loads(data)
        except Exception as e:
            self.logger.warning(f"Failed to retrieve from Redis: {e}")
        return None
    
    async def _delete_from_redis(self, key: str):
        """Delete data from Redis"""
        try:
            self._redis_client.delete(f"tmx:{key}")
        except Exception as e:
            self.logger.warning(f"Failed to delete from Redis: {e}")
    
    async def _store_in_persistent(self, key: str, entry: DataEntry):
        """Store data entry in persistent storage"""
        try:
            cursor = self._persistent_storage.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO data_entries 
                (key, data, timestamp, expires_at, access_count, data_type, size_bytes, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                key,
                pickle.dumps(entry.data),
                entry.timestamp.isoformat(),
                entry.expires_at.isoformat() if entry.expires_at else None,
                entry.access_count,
                entry.data_type,
                entry.size_bytes,
                entry.checksum
            ))
            self._persistent_storage.commit()
        except Exception as e:
            self.logger.warning(f"Failed to store in persistent storage: {e}")
    
    async def _retrieve_from_persistent(self, key: str) -> Optional[DataEntry]:
        """Retrieve data entry from persistent storage"""
        try:
            cursor = self._persistent_storage.cursor()
            cursor.execute("""
                SELECT data, timestamp, expires_at, access_count, data_type, size_bytes, checksum
                FROM data_entries WHERE key = ?
            """, (key,))
            
            row = cursor.fetchone()
            if row:
                data, timestamp, expires_at, access_count, data_type, size_bytes, checksum = row
                
                # Check if expired
                if expires_at:
                    expires_dt = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires_dt:
                        await self._delete_from_persistent(key)
                        return None
                
                return DataEntry(
                    key=key,
                    data=pickle.loads(data),
                    timestamp=datetime.fromisoformat(timestamp),
                    expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
                    access_count=access_count,
                    data_type=data_type,
                    size_bytes=size_bytes,
                    checksum=checksum
                )
        except Exception as e:
            self.logger.warning(f"Failed to retrieve from persistent storage: {e}")
        return None
    
    async def _delete_from_persistent(self, key: str):
        """Delete data from persistent storage"""
        try:
            cursor = self._persistent_storage.cursor()
            cursor.execute("DELETE FROM data_entries WHERE key = ?", (key,))
            self._persistent_storage.commit()
        except Exception as e:
            self.logger.warning(f"Failed to delete from persistent storage: {e}")
    
    async def _cleanup_loop(self):
        """Periodic cleanup of expired data"""
        while self.is_running:
            try:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                if self.is_running:
                    await self._perform_cleanup()
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    async def _perform_cleanup(self) -> Dict[str, Any]:
        """Perform cleanup of expired and old data"""
        try:
            cleanup_stats = {
                'expired_entries': 0,
                'memory_freed_mb': 0,
                'timestamp': datetime.now().isoformat()
            }
            
            with self._lock:
                # Clean expired entries from persistent storage
                cursor = self._persistent_storage.cursor()
                cursor.execute("""
                    DELETE FROM data_entries 
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (datetime.now().isoformat(),))
                cleanup_stats['expired_entries'] = cursor.rowcount
                self._persistent_storage.commit()
                
                # Calculate memory usage
                total_size = sum(
                    entry.size_bytes for entry in self._memory_cache.values()
                    if hasattr(entry, 'size_bytes')
                )
                self.metrics.memory_usage = total_size / (1024 * 1024)  # MB
                
                # Force cleanup if memory usage is high
                if self.metrics.memory_usage > self.max_memory_mb * 0.8:
                    # Remove least recently used items
                    items_to_remove = max(1, len(self._memory_cache) // 4)
                    for _ in range(items_to_remove):
                        if self._memory_cache:
                            self._memory_cache.popitem()
                            self.metrics.evictions += 1
                
                # Update metrics
                self.metrics.last_updated = datetime.now()
                
                # Save metrics to database
                cursor.execute("""
                    INSERT INTO cache_metrics (timestamp, hits, misses, evictions, memory_usage)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    self.metrics.last_updated.isoformat(),
                    self.metrics.hits,
                    self.metrics.misses,
                    self.metrics.evictions,
                    self.metrics.memory_usage
                ))
                self._persistent_storage.commit()
            
            self._last_cleanup = datetime.now()
            cleanup_stats['memory_freed_mb'] = self.max_memory_mb - self.metrics.memory_usage
            
            self.logger.info(f"Cleanup completed: {cleanup_stats}")
            return {'success': True, 'stats': cleanup_stats}
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _get_metrics(self) -> Dict[str, Any]:
        """Get current cache metrics"""
        return {
            'success': True,
            'metrics': {
                'hit_rate': self.metrics.hit_rate,
                'hits': self.metrics.hits,
                'misses': self.metrics.misses,
                'evictions': self.metrics.evictions,
                'memory_usage_mb': self.metrics.memory_usage,
                'max_memory_mb': self.max_memory_mb,
                'memory_cache_size': len(self._memory_cache),
                'lru_cache_size': len(self._lru_cache),
                'last_cleanup': self._last_cleanup.isoformat(),
                'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600
            }
        }
    
    async def _load_persistent_cache(self):
        """Load important data from persistent storage into memory"""
        try:
            cursor = self._persistent_storage.cursor()
            cursor.execute("""
                SELECT key, data, timestamp, expires_at, access_count, data_type, size_bytes, checksum
                FROM data_entries 
                WHERE data_type IN ('model_states', 'configuration')
                AND (expires_at IS NULL OR expires_at > ?)
                ORDER BY access_count DESC
                LIMIT 100
            """, (datetime.now().isoformat(),))
            
            for row in cursor.fetchall():
                key, data, timestamp, expires_at, access_count, data_type, size_bytes, checksum = row
                
                entry = DataEntry(
                    key=key,
                    data=pickle.loads(data),
                    timestamp=datetime.fromisoformat(timestamp),
                    expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
                    access_count=access_count,
                    data_type=data_type,
                    size_bytes=size_bytes,
                    checksum=checksum
                )
                
                self._memory_cache[key] = entry
                if data_type == 'model_states':
                    self._lru_cache[key] = entry
            
            self.logger.info("Loaded persistent cache into memory")
            
        except Exception as e:
            self.logger.warning(f"Failed to load persistent cache: {e}")
    
    async def _save_cache_to_persistent(self):
        """Save important cache data to persistent storage"""
        try:
            cursor = self._persistent_storage.cursor()
            
            for key, entry in self._memory_cache.items():
                if entry.data_type in ['model_states', 'bot_performance', 'configuration']:
                    cursor.execute("""
                        INSERT OR REPLACE INTO data_entries 
                        (key, data, timestamp, expires_at, access_count, data_type, size_bytes, checksum)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        key,
                        pickle.dumps(entry.data),
                        entry.timestamp.isoformat(),
                        entry.expires_at.isoformat() if entry.expires_at else None,
                        entry.access_count,
                        entry.data_type,
                        entry.size_bytes,
                        entry.checksum
                    ))
            
            self._persistent_storage.commit()
            self.logger.info("Saved cache to persistent storage")
            
        except Exception as e:
            self.logger.warning(f"Failed to save cache to persistent storage: {e}")

    async def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        try:
            metrics = await self._get_metrics()
            
            return {
                'bot_id': self.bot_id,
                'is_running': self.is_running,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'metrics': metrics.get('metrics', {}),
                'storage_backends': {
                    'memory_cache': True,
                    'lru_cache': True,
                    'redis': self._redis_client is not None,
                    'persistent': self._persistent_storage is not None
                },
                'configuration': {
                    'max_memory_mb': self.max_memory_mb,
                    'cache_ttl_hours': self.cache_ttl_hours,
                    'cleanup_interval_minutes': self.cleanup_interval_minutes
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting status: {e}")
            return {
                'bot_id': self.bot_id,
                'is_running': False,
                'error': str(e)
            }
    
    async def initialize(self) -> bool:
        """Initialize bot resources"""
        try:
            # Initialize cache directories
            self.cache_path.mkdir(parents=True, exist_ok=True)
            self.backup_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            await self._initialize_database()
            
            # Initialize Redis if configured
            if self.use_redis:
                await self._initialize_redis()
            
            # Start cleanup background task
            if self.cleanup_interval_minutes > 0:
                self._start_cleanup_task()
            
            self.is_initialized = True
            self.logger.info("MemoryBot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MemoryBot: {e}")
            return False
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute one bot cycle"""
        try:
            # Perform memory optimization
            await self._optimize_memory()
            
            # Update cache metrics
            self._update_cache_metrics()
            
            # Check memory usage
            current_usage = self._get_memory_usage()
            
            return {
                'status': 'success',
                'memory_usage_mb': current_usage,
                'cache_hit_rate': self.cache_metrics.hit_rate,
                'cached_items': len(self.data_cache),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in MemoryBot cycle: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def cleanup(self):
        """Cleanup bot resources"""
        try:
            # Stop background tasks
            if hasattr(self, '_cleanup_task'):
                self._cleanup_task.cancel()
            
            # Close Redis connection
            if self.redis_client:
                self.redis_client.close()
            
            # Close database connections
            if hasattr(self, '_db_connection'):
                self._db_connection.close()
            
            # Clear caches
            self.data_cache.clear()
            if hasattr(self, 'model_cache'):
                self.model_cache.clear()
            
            self.is_running = False
            self.logger.info("MemoryBot cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during MemoryBot cleanup: {e}")

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except Exception:
            return 0.0

    def _update_cache_metrics(self):
        """Update cache performance metrics"""
        try:
            if hasattr(self.data_cache, 'data'):
                # For TTLCache/LRUCache
                self.cache_metrics.memory_usage = sum(
                    entry.size_bytes for entry in self.data_cache.data.values()
                    if hasattr(entry, 'size_bytes')
                ) / 1024 / 1024  # Convert to MB
                
            self.cache_metrics.last_updated = datetime.now()
        except Exception as e:
            self.logger.error(f"Error updating cache metrics: {e}")

    async def _optimize_memory(self):
        """Perform memory optimization"""
        try:
            # Remove expired entries
            await self._cleanup_expired_data()
            
            # Check if memory limit is exceeded
            current_usage = self._get_memory_usage()
            if current_usage > self.max_memory_mb:
                await self._reduce_memory_usage()
                
        except Exception as e:
            self.logger.error(f"Error during memory optimization: {e}")

    async def _reduce_memory_usage(self):
        """Reduce memory usage when limit is exceeded"""
        try:
            # Clear least recently used items
            if hasattr(self.data_cache, 'data'):
                items_to_remove = max(1, len(self.data_cache) // 10)  # Remove 10%
                for _ in range(items_to_remove):
                    if self.data_cache:
                        self.data_cache.popitem(last=False)  # Remove oldest
                        
            self.logger.info(f"Reduced memory usage by clearing cache items")
            
        except Exception as e:
            self.logger.error(f"Error reducing memory usage: {e}")

    def _start_cleanup_task(self):
        """Start background cleanup task"""
        try:
            async def cleanup_loop():
                while self.is_running:
                    await asyncio.sleep(self.cleanup_interval_minutes * 60)
                    await self._cleanup_expired_data()
            
            self._cleanup_task = asyncio.create_task(cleanup_loop())
            
        except Exception as e:
            self.logger.error(f"Error starting cleanup task: {e}")

    async def _initialize_database(self):
        """Initialize SQLite database for persistent storage"""
        try:
            db_path = self.cache_path / "memory_cache.db"
            self._db_connection = sqlite3.connect(str(db_path))
            
            # Create tables
            cursor = self._db_connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    data BLOB,
                    timestamp TEXT,
                    expires_at TEXT,
                    data_type TEXT,
                    size_bytes INTEGER
                )
            """)
            self._db_connection.commit()
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")

    async def _initialize_redis(self):
        """Initialize Redis connection if enabled"""
        try:
            if self.redis_config:
                self.redis_client = redis.Redis(**self.redis_config)
                # Test connection
                self.redis_client.ping()
                self.logger.info("Redis connection established")
            
        except Exception as e:
            self.logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None
