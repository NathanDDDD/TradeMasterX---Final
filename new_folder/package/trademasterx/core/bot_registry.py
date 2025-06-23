"""
TradeMasterX 2.0 - Bot Registry
Centralized bot management system with factory pattern implementation.
Handles bot lifecycle, discovery, and coordination.
"""

import asyncio
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Type
from abc import ABC, abstractmethod

from trademasterx.config.config_loader import ConfigLoader


class BaseBot(ABC):
    """Base class for all TradeMasterX bots"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"Bot.{name}")
        self.is_initialized = False
        self.is_running = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize bot resources"""
        pass
    
    @abstractmethod
    async def execute_cycle(self) -> Dict[str, Any]:
        """Execute one bot cycle"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup bot resources"""
        pass
    
    async def emergency_stop(self):
        """Emergency stop - override if needed"""
        self.is_running = False
        await self.cleanup()


class BotRegistry:
    """
    Centralized bot registry and management system
    
    Features:
    - Factory pattern for bot creation
    - Plugin-style bot discovery
    - Lifecycle management
    - Configuration injection
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        # If no config is provided, load default configuration
        if config is None:
            config_loader = ConfigLoader()
            self.config = config_loader.get_config('system', {})
        else:
            self.config = config
        
        self.logger = logging.getLogger("BotRegistry")
        
        # Bot storage
        self.bots: Dict[str, BaseBot] = {}
        self.bot_classes: Dict[str, Type[BaseBot]] = {}
          # Configuration
        self.bot_configs = self.config.get('bots', {})
        
        # Discover available bots
        self._discover_bots()
        
        self.logger.info("BotRegistry initialized")

    @property
    def registered_bots(self):
        """Get list of registered bot names"""
        return list(self.bot_classes.keys())

    def _discover_bots(self):
        """Discover available bot classes"""
        try:
            # Analytics bots
            self._register_bot_class("market_analysis", "trademasterx.bots.analytics.market_analysis", "MarketAnalysisBot")
            self._register_bot_class("sentiment", "trademasterx.bots.analytics.sentiment", "SentimentBot")
            
            # Strategy bots
            self._register_bot_class("strategy", "trademasterx.bots.strategy.strategy", "StrategyBot")
            
            # System bots            self._register_bot_class("risk", "trademasterx.bots.system.risk", "RiskBot")            self._register_bot_class("memory", "trademasterx.bots.system.memory", "MemoryBot")
            self._register_bot_class("logger", "trademasterx.bots.system.logger", "LoggerBot")
            self.logger.info(f"Discovered {len(self.bot_classes)} bot classes")
        except Exception as e:
            self.logger.error(f"Bot discovery error: {e}")

    def register_bot(self, bot_name: str, bot_class):
        """Register a bot class manually"""
        try:
            self.bot_classes[bot_name] = bot_class
            self.logger.info(f"Registered bot class: {bot_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register bot {bot_name}: {e}")
            return False

    def create_bot_instance(self, bot_name: str, config: Dict[str, Any] = None):
        """Create an instance of a registered bot"""
        try:
            if bot_name not in self.bot_classes:
                raise ValueError(f"Bot {bot_name} not registered")
            
            bot_class = self.bot_classes[bot_name]
            if config is None:
                config = self.bot_configs.get(bot_name, {})
            
            # Create bot instance
            bot_instance = bot_class(bot_name, config)
            self.bots[bot_name] = bot_instance
            self.logger.info(f"Created bot instance: {bot_name}")
            return bot_instance
            
        except Exception as e:
            self.logger.error(f"Failed to create bot instance {bot_name}: {e}")
            return None

    def create_bot(self, bot_name: str, config: Dict[str, Any] = None) -> str:
        """Create a bot instance and return its name for integration test expectations"""
        # Check if bot type exists first
        if bot_name not in self.bot_classes:
            raise ValueError(f"Bot {bot_name} not registered")
        
        bot_instance = self.create_bot_instance(bot_name, config)
        if bot_instance:
            return bot_name  # Return the bot name instead of the instance
        else:
            raise RuntimeError(f"Failed to create bot instance: {bot_name}")

    def remove_bot(self, bot_name: str) -> bool:
        """Remove a bot instance"""
        try:
            if bot_name in self.bots:
                # Run cleanup in background if it's async
                bot = self.bots[bot_name]
                if hasattr(bot, 'cleanup'):
                    # For sync context, we can't await, so just remove
                    pass
                del self.bots[bot_name]
                self.logger.info(f"Bot removed: {bot_name}")
                return True
            else:
                self.logger.warning(f"Bot not found for removal: {bot_name}")
                return False
        except Exception as e:
            self.logger.error(f"Error removing bot {bot_name}: {e}")
            return False

    def _register_bot_class(self, bot_name: str, module_path: str, class_name: str):
        """Register a bot class for later instantiation"""
        try:
            module = importlib.import_module(module_path)
            bot_class = getattr(module, class_name)
            
            if issubclass(bot_class, BaseBot):
                self.bot_classes[bot_name] = bot_class
                self.logger.debug(f"Registered bot class: {bot_name}")
            else:
                self.logger.warning(f"Bot class {class_name} does not inherit from BaseBot")
                
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"Could not register bot {bot_name}: {e}")

    async def initialize_all_bots(self):
        """Initialize all configured bots"""
        self.logger.info("Initializing all bots...")
        
        initialization_order = [
            "logger",      # Initialize logging first
            "memory",      # Memory management
            "risk",        # Risk management
            "market_analysis",  # Market data
            "sentiment",   # Sentiment analysis
            "strategy"     # Trading strategy
        ]
        
        # Initialize bots in order
        for bot_name in initialization_order:
            if bot_name in self.bot_configs:
                await self._initialize_bot(bot_name)
        
        # Initialize any remaining configured bots
        for bot_name in self.bot_configs:
            if bot_name not in self.bots:
                await self._initialize_bot(bot_name)
        
        self.logger.info(f"Initialized {len(self.bots)} bots")

    async def _initialize_bot(self, bot_name: str) -> bool:
        """Initialize a specific bot"""
        try:
            if bot_name in self.bots:
                self.logger.debug(f"Bot {bot_name} already initialized")
                return True
            
            if bot_name not in self.bot_classes:
                self.logger.error(f"Bot class not found: {bot_name}")
                return False
            
            # Get bot configuration
            bot_config = self.bot_configs.get(bot_name, {})
            bot_config.update(self.config.get('global', {}))  # Add global config
            
            # Create bot instance
            bot_class = self.bot_classes[bot_name]
            bot_instance = bot_class(bot_name, bot_config)
            
            # Initialize bot
            success = await bot_instance.initialize()
            
            if success:
                self.bots[bot_name] = bot_instance
                self.logger.info(f"✅ Bot initialized: {bot_name}")
                return True
            else:
                self.logger.error(f"❌ Bot initialization failed: {bot_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Bot initialization error ({bot_name}): {e}")
            return False

    def get_bot(self, bot_name: str) -> Optional[BaseBot]:
        """Get a specific bot instance"""
        return self.bots.get(bot_name)

    def get_all_bots(self) -> Dict[str, BaseBot]:
        """Get all bot instances"""
        return self.bots.copy()

    def get_bot_count(self) -> int:
        """Get number of active bots"""
        return len(self.bots)

    def get_bot_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all bots"""
        status = {}
        
        for bot_name, bot in self.bots.items():
            status[bot_name] = {
                "initialized": bot.is_initialized,
                "running": bot.is_running,
                "class": bot.__class__.__name__
            }
        
        return status

    async def execute_bot_cycle(self, bot_name: str) -> Optional[Dict[str, Any]]:
        """Execute a cycle for a specific bot"""
        bot = self.get_bot(bot_name)
        if bot and bot.is_initialized:
            try:
                return await bot.execute_cycle()
            except Exception as e:
                self.logger.error(f"Bot cycle error ({bot_name}): {e}")
                return None
        return None

    async def execute_all_cycles(self) -> Dict[str, Any]:
        """Execute cycles for all bots"""
        results = {}
        
        for bot_name, bot in self.bots.items():
            if bot.is_initialized:
                try:
                    result = await bot.execute_cycle()
                    results[bot_name] = result
                except Exception as e:
                    self.logger.error(f"Bot cycle error ({bot_name}): {e}")
                    results[bot_name] = {"error": str(e)}
        
        return results

    async def cleanup_all_bots(self):
        """Cleanup all bots"""
        self.logger.info("Cleaning up all bots...")
        
        for bot_name, bot in self.bots.items():
            try:
                await bot.cleanup()
                self.logger.debug(f"Bot cleaned up: {bot_name}")
            except Exception as e:
                self.logger.error(f"Bot cleanup error ({bot_name}): {e}")
        
        self.bots.clear()
        self.logger.info("All bots cleaned up")

    async def emergency_stop_all(self):
        """Emergency stop all bots"""
        self.logger.warning("🚨 Emergency stopping all bots")
        
        for bot_name, bot in self.bots.items():
            try:
                await bot.emergency_stop()
                self.logger.debug(f"Bot emergency stopped: {bot_name}")
            except Exception as e:
                self.logger.error(f"Bot emergency stop error ({bot_name}): {e}")

    def register_custom_bot(self, bot_name: str, bot_class: Type[BaseBot]):
        """Register a custom bot class at runtime"""
        if issubclass(bot_class, BaseBot):
            self.bot_classes[bot_name] = bot_class
            self.logger.info(f"Custom bot registered: {bot_name}")
        else:
            raise ValueError(f"Bot class must inherit from BaseBot")

    async def reload_bot(self, bot_name: str) -> bool:
        """Reload a specific bot"""
        try:
            # Cleanup existing bot
            if bot_name in self.bots:
                await self.bots[bot_name].cleanup()
                del self.bots[bot_name]
            
            # Reinitialize bot
            return await self._initialize_bot(bot_name)
            
        except Exception as e:
            self.logger.error(f"Bot reload error ({bot_name}): {e}")
            return False

    def get_available_bots(self) -> List[str]:
        """Get list of available bot classes"""
        return list(self.bot_classes.keys())

    def get_active_bots(self) -> List[str]:
        """Get list of active bot instances"""
        return list(self.bots.keys())


# Factory functions for common bot operations
async def create_bot_registry(config_path: str = "config/bots.yaml") -> BotRegistry:
    """Factory function to create and initialize bot registry"""
    config_loader = ConfigLoader()
    config = config_loader.load_bot_config(config_path)
    
    registry = BotRegistry(config)
    await registry.initialize_all_bots()
    
    return registry


def create_custom_bot(name: str, execute_func, initialize_func=None, cleanup_func=None) -> Type[BaseBot]:
    """Factory function to create custom bot classes"""
    
    class CustomBot(BaseBot):
        async def initialize(self) -> bool:
            if initialize_func:
                return await initialize_func(self)
            self.is_initialized = True
            return True
        
        async def execute_cycle(self) -> Dict[str, Any]:
            return await execute_func(self)
        
        async def cleanup(self):
            if cleanup_func:
                await cleanup_func(self)
    
    CustomBot.__name__ = f"{name}Bot"
    return CustomBot
