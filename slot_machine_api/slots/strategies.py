"""
Strategy classes for the slot machine application.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Set

from .constants import MIN_MATCHING_SYMBOLS
from .interfaces import ReelResult, WinData, SymbolName
from .null_objects import NULL_WIN_DATA
from .utils import find_longest_sequence, transpose_matrix


class WinStrategy(ABC):
    """Abstract base class for win checking strategies."""
    
    @abstractmethod
    def check_wins(self, result: ReelResult) -> WinData:
        """
        Check for winning combinations in the spin result.
        
        Args:
            result: The spin result to check
            
        Returns:
            Win data if there are wins, NULL_WIN_DATA otherwise
        """
        pass


class HorizontalWinStrategy(WinStrategy):
    """Strategy for checking horizontal wins."""
    
    def check_wins(self, result: ReelResult) -> WinData:
        """
        Check for horizontal winning combinations.
        
        Args:
            result: The spin result to check
            
        Returns:
            Win data if there are wins, NULL_WIN_DATA otherwise
        """
        hits = {}
        horizontal = self._get_horizontal_rows(result)
        
        for row_idx, row in enumerate(horizontal):
            self._check_row_for_wins(row, row_idx, hits)
        
        return hits if hits else NULL_WIN_DATA
    
    def _get_horizontal_rows(self, result: ReelResult) -> List[List[SymbolName]]:
        """Convert vertical reels to horizontal rows."""
        # Extract values from the result dictionary
        reels = []
        for i in range(len(result)):
            reels.append(result[i])
        
        # Transpose the matrix to get horizontal rows
        return transpose_matrix(reels)
    
    def _check_row_for_wins(self, row: List[SymbolName], row_idx: int, hits: WinData) -> None:
        """Check a single row for winning combinations."""
        # Get unique symbols in the row
        unique_symbols: Set[SymbolName] = set(row)
        
        for sym in unique_symbols:
            if row.count(sym) >= MIN_MATCHING_SYMBOLS:  # Potential win
                possible_win = [idx for idx, val in enumerate(row) if sym == val]
                
                # Check possible_win for a subsequence longer than minimum required
                longest = find_longest_sequence(possible_win)
                if len(longest) >= MIN_MATCHING_SYMBOLS:
                    hits[row_idx + 1] = [sym, longest]


class DiagonalWinStrategy(WinStrategy):
    """Strategy for checking diagonal wins."""
    
    def check_wins(self, result: ReelResult) -> WinData:
        """
        Check for diagonal winning combinations.
        
        Args:
            result: The spin result to check
            
        Returns:
            Win data if there are wins, NULL_WIN_DATA otherwise
        """
        hits = {}
        horizontal = self._get_horizontal_rows(result)
        
        # Check main diagonal (top-left to bottom-right)
        self._check_diagonal(horizontal, 0, 0, 1, 1, hits, 'main')
        
        # Check anti-diagonal (top-right to bottom-left)
        self._check_diagonal(horizontal, 0, len(horizontal[0])-1, 1, -1, hits, 'anti')
        
        return hits if hits else NULL_WIN_DATA
    
    def _get_horizontal_rows(self, result: ReelResult) -> List[List[SymbolName]]:
        """Convert vertical reels to horizontal rows."""
        # Extract values from the result dictionary
        reels = []
        for i in range(len(result)):
            reels.append(result[i])
        
        # Transpose the matrix to get horizontal rows
        return transpose_matrix(reels)
    
    def _check_diagonal(self, grid: List[List[SymbolName]], start_row: int, start_col: int, 
                        row_step: int, col_step: int, hits: WinData, diag_name: str) -> None:
        """Check a diagonal for winning combinations."""
        rows, cols = len(grid), len(grid[0])
        diagonal = []
        positions = []
        
        # Extract the diagonal
        row, col = start_row, start_col
        while 0 <= row < rows and 0 <= col < cols:
            diagonal.append(grid[row][col])
            positions.append((row, col))
            row += row_step
            col += col_step
        
        # Check for wins in the diagonal
        if len(diagonal) >= MIN_MATCHING_SYMBOLS:
            unique_symbols: Set[SymbolName] = set(diagonal)
            
            for sym in unique_symbols:
                if diagonal.count(sym) >= MIN_MATCHING_SYMBOLS:
                    # Find indices of the symbol in the diagonal
                    indices = [i for i, val in enumerate(diagonal) if val == sym]
                    
                    # Check for consecutive indices
                    longest = find_longest_sequence(indices)
                    if len(longest) >= MIN_MATCHING_SYMBOLS:
                        # Use positions to map back to the grid
                        win_positions = [positions[i] for i in longest]
                        hits[f"{diag_name}_diagonal"] = [sym, win_positions]


class CompositeWinStrategy(WinStrategy):
    """Composite strategy that combines multiple win strategies."""
    
    def __init__(self, strategies: List[WinStrategy]):
        """
        Initialize with a list of strategies.
        
        Args:
            strategies: List of win checking strategies
        """
        self.strategies = strategies
    
    def check_wins(self, result: ReelResult) -> WinData:
        """
        Check for winning combinations using all strategies.
        
        Args:
            result: The spin result to check
            
        Returns:
            Combined win data from all strategies
        """
        combined_hits = {}
        
        for strategy in self.strategies:
            strategy_hits = strategy.check_wins(result)
            if strategy_hits:  # Not NULL_WIN_DATA
                combined_hits.update(strategy_hits)
        
        return combined_hits if combined_hits else NULL_WIN_DATA


# Factory function to create the default win strategy
def create_default_win_strategy() -> WinStrategy:
    """Create the default composite win strategy."""
    return CompositeWinStrategy([
        HorizontalWinStrategy(),
        DiagonalWinStrategy()
    ])