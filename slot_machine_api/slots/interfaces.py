"""
Interfaces for the slot machine services.
"""
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Optional, Any, TypeVar, Protocol

# Type aliases for better readability
SymbolName = str
ReelIndex = int
RowIndex = int
ReelResult = Dict[ReelIndex, List[SymbolName]]
WinData = Dict[int, List[Any]]  # Row number -> [symbol_name, indices]

# Generic type for models
T = TypeVar('T')


class SymbolProvider(Protocol):
    """Protocol for objects that provide symbol data."""
    @property
    def name(self) -> str:
        """Get the symbol name."""
        ...
    @property
    def payout_multiplier(self) -> Decimal:
        """Get the symbol payout multiplier."""
        ...


class IReelService(ABC):
    """Interface for reel services."""
    @abstractmethod
    def generate_spin(self, num_reels: int, visible_rows: int) -> ReelResult:
        """Generate a random spin result."""
        pass
    @abstractmethod
    def flip_horizontal(self, result: ReelResult) -> List[List[SymbolName]]:
        """Convert vertical reels to horizontal rows for win checking."""
        pass
    @abstractmethod
    def check_wins(self, result: ReelResult) -> Optional[WinData]:
        """Check for winning combinations in the spin result."""
        pass
    @abstractmethod
    def calculate_payout(self, win_data: Optional[WinData], bet_size: Decimal) -> Decimal:
        """Calculate payout based on win data and bet size."""
        pass

class ISlotMachineService(ABC):
    """Interface for slot machine services."""
    
    @abstractmethod
    def play_spin(self, player: Any, bet_size: Decimal) -> Dict[str, Any]:
        """Process a single spin of the slot machine."""
        pass
