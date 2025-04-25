"""
Factory classes for creating service instances.
"""
from typing import Any, Callable, Type, Dict, List, Optional

from django.core.cache import cache

from .interfaces import IReelService, ISlotMachineService, SymbolProvider
from .services import ReelService, SlotMachineService


class ServiceFactory:
    """Factory for creating service instances."""
    
    @staticmethod
    def create_reel_service(symbols: List[SymbolProvider], symbol_provider: Callable) -> IReelService:
        """
        Create a ReelService instance.
        
        Args:
            symbols: List of symbols to use for reel generation
            symbol_provider: Function to retrieve symbol data by name
            
        Returns:
            An instance of IReelService
        """
        # Check if symbols are cached
        cache_key = 'slot_machine_symbols'
        cached_symbols = cache.get(cache_key)
        
        if cached_symbols is None:
            # Cache symbols for future use
            cache.set(cache_key, symbols, timeout=3600)  # Cache for 1 hour
        else:
            symbols = cached_symbols
        
        return ReelService(symbols, symbol_provider)
    
    @staticmethod
    def create_slot_machine_service(
        reel_service: IReelService,
        spin_model: Type[Any],
        game_model: Type[Any]
    ) -> ISlotMachineService:
        """
        Create a SlotMachineService instance.
        
        Args:
            reel_service: ReelService instance
            spin_model: Spin model class
            game_model: Game model class
            
        Returns:
            An instance of ISlotMachineService
        """
        return SlotMachineService(reel_service, spin_model, game_model)
    
    @classmethod
    def create_services(
        cls,
        symbols: List[SymbolProvider],
        symbol_provider: Callable,
        spin_model: Type[Any],
        game_model: Type[Any]
    ) -> Dict[str, Any]:
        """
        Create all required services.
        
        Args:
            symbols: List of symbols to use for reel generation
            symbol_provider: Function to retrieve symbol data by name
            spin_model: Spin model class
            game_model: Game model class
            
        Returns:
            Dictionary containing all service instances
        """
        reel_service = cls.create_reel_service(symbols, symbol_provider)
        slot_machine_service = cls.create_slot_machine_service(reel_service, spin_model, game_model)
        
        return {
            'reel_service': reel_service,
            'slot_machine_service': slot_machine_service
        }