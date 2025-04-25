"""
Null objects for the slot machine application.
"""
from decimal import Decimal
from typing import List, Dict, Any, Iterator, Tuple


class NullWinData:
    """
    Null object for win data.
    
    This class implements the same interface as a win data dictionary
    but represents the absence of any wins.
    """
    
    def __bool__(self) -> bool:
        """Return False to indicate no wins."""
        return False
    
    def __len__(self) -> int:
        """Return 0 to indicate no wins."""
        return 0
    
    def __getitem__(self, key: Any) -> List[Any]:
        """Return an empty list for any key."""
        return []
    
    def __iter__(self) -> Iterator[Any]:
        """Return an empty iterator."""
        return iter(())
    
    def items(self) -> List[Tuple[Any, List[Any]]]:
        """Return an empty list of items."""
        return []
    
    def keys(self) -> List[Any]:
        """Return an empty list of keys."""
        return []
    
    def values(self) -> List[List[Any]]:
        """Return an empty list of values."""
        return []
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Return the default value for any key."""
        return default


# Singleton instance of NullWinData
NULL_WIN_DATA = NullWinData()