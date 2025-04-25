"""
Service classes for the slot machine application.
"""
import random
from decimal import Decimal
from typing import List, Dict, Optional, Any, Sequence, cast

from django.db import transaction
from django.core.cache import cache

from .constants import DEFAULT_NUM_REELS, DEFAULT_VISIBLE_ROWS, MIN_MATCHING_SYMBOLS
from .interfaces import IReelService, ISlotMachineService, SymbolProvider, ReelResult, WinData, SymbolName
from .models import SpinConfig, SpinResult, SpinResponse
from .utils import find_longest_sequence, transpose_matrix
from .strategies import create_default_win_strategy


class ReelGenerator:
    """Responsible for generating random reel results."""

    def __init__(self, symbols: Sequence[SymbolProvider]):
        """
        Initialize the reel generator.

        Args:
            symbols: Collection of symbols to use for generation
        """
        self.symbols = symbols

    def generate_spin(self, config: SpinConfig) -> ReelResult:
        """
        Generate a random spin result.

        Args:
            config: Configuration for the spin

        Returns:
            A dictionary mapping reel indices to lists of symbol names
        """
        result = {}
        for reel in range(config.num_reels):
            # Select random symbols for this reel
            shuffled_symbols = random.sample(list(self.symbols), len(self.symbols))
            result[reel] = [shuffled_symbols[i].name for i in range(config.visible_rows)]
        return result


class PayoutCalculator:
    """Responsible for calculating payouts based on win data."""

    def __init__(self, symbol_provider: Any):
        """
        Initialize the payout calculator.

        Args:
            symbol_provider: A function or object that can retrieve symbol data
        """
        self.symbol_provider = symbol_provider

    def calculate_payout(self, win_data: Optional[WinData], bet_size: Decimal) -> Decimal:
        """
        Calculate payout based on win data and bet size.

        Args:
            win_data: The win data to calculate payout for
            bet_size: The bet size for this spin

        Returns:
            The calculated payout amount
        """
        if not win_data:
            return Decimal('0.00')

        total_payout = Decimal('0.00')

        for row_number, win_info in win_data.items():
            sym_name, indices = win_info
            symbol = self.symbol_provider(name=sym_name)
            combo_length = len(indices)
            total_payout += Decimal(bet_size) * combo_length * symbol.payout_multiplier

        return total_payout


class ReelService(IReelService):
    """Service for reel operations."""

    def __init__(self, symbols: Sequence[SymbolProvider], symbol_provider: Any):
        """
        Initialize the reel service.

        Args:
            symbols: Collection of symbols to use for generation
            symbol_provider: Function to retrieve symbol data by name
        """
        self.generator = ReelGenerator(symbols)
        self.win_strategy = create_default_win_strategy()
        self.payout_calculator = PayoutCalculator(symbol_provider)

    def generate_spin(self, num_reels: int = DEFAULT_NUM_REELS, 
                     visible_rows: int = DEFAULT_VISIBLE_ROWS) -> ReelResult:
        """
        Generate a random spin result.

        Args:
            num_reels: Number of reels to generate
            visible_rows: Number of visible symbols per reel

        Returns:
            A dictionary mapping reel indices to lists of symbol names
        """
        config = SpinConfig(num_reels=num_reels, visible_rows=visible_rows)
        return self.generator.generate_spin(config)

    def flip_horizontal(self, result: ReelResult) -> List[List[SymbolName]]:
        """
        Convert vertical reels to horizontal rows for win checking.

        Args:
            result: The spin result with vertical reels

        Returns:
            A list of horizontal rows
        """
        # Extract values from the result dictionary
        reels = []
        for i in range(len(result)):
            reels.append(result[i])

        # Transpose the matrix to get horizontal rows
        return transpose_matrix(reels)

    def check_wins(self, result: ReelResult) -> Optional[WinData]:
        """
        Check for winning combinations in the spin result.

        Args:
            result: The spin result to check

        Returns:
            Win data if there are wins, None otherwise
        """
        win_data = self.win_strategy.check_wins(result)
        return win_data if win_data else None

    def calculate_payout(self, win_data: Optional[WinData], bet_size: Decimal) -> Decimal:
        """
        Calculate payout based on win data and bet size.

        Args:
            win_data: The win data to calculate payout for
            bet_size: The bet size for this spin

        Returns:
            The calculated payout amount
        """
        return self.payout_calculator.calculate_payout(win_data, bet_size)


class SlotMachineService(ISlotMachineService):
    """Service for slot machine operations."""

    def __init__(self, reel_service: IReelService, spin_model: Any, game_model: Any):
        """
        Initialize the slot machine service.

        Args:
            reel_service: Service for reel operations
            spin_model: Model class for spins
            game_model: Model class for games
        """
        self.reel_service = reel_service
        self.spin_model = spin_model
        self.game_model = game_model

    @transaction.atomic
    def play_spin(self, player: Any, bet_size: Decimal) -> Dict[str, Any]:
        """
        Process a single spin of the slot machine.

        Args:
            player: The player making the spin
            bet_size: The bet size for this spin

        Returns:
            A dictionary with the spin result
        """
        # Check if player has enough balance
        if player.balance < Decimal(bet_size):
            return SpinResponse(
                success=False,
                message='Insufficient balance'
            ).__dict__

        # Update player balance
        player.balance -= Decimal(bet_size)
        player.total_wager += Decimal(bet_size)
        player.save()

        try:
            # Generate spin result
            result = self.reel_service.generate_spin()

            # Check for wins
            win_data = self.reel_service.check_wins(result)
            payout = Decimal('0.00')

            # Calculate and process payout if there's a win
            if win_data:
                payout = self.reel_service.calculate_payout(win_data, bet_size)
                player.balance += payout
                player.total_won += payout
                player.save()

            # Create and return the spin record
            game, _ = self.game_model.objects.get_or_create(player=player)

            spin = self.spin_model.objects.create(
                game=game,
                bet_amount=bet_size,
                payout=payout,
                result=result,
                win_data=win_data
            )

            return SpinResponse(
                success=True,
                spin_id=str(spin.id),
                result=result,
                win_data=win_data,
                payout=payout,
                current_balance=player.balance
            ).__dict__

        except Exception as e:
            # Rollback is automatic due to transaction.atomic
            return SpinResponse(
                success=False,
                message=f"Error processing spin: {str(e)}"
            ).__dict__
