"""
Database and data models for the slot machine application.
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Dict, Optional, Any

from django.db import models
from django.contrib.auth.models import User
import uuid

from .interfaces import SymbolName, ReelResult, WinData


class Symbol(models.Model):
    """Database model for slot machine symbols."""
    name = models.CharField(max_length=50)
    image_path = models.CharField(max_length=200)
    payout_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Player(models.Model):
    """Database model for players."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    total_won = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_wager = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Player: {self.user.username}"


class Game(models.Model):
    """Database model for game sessions."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='games')
    machine_balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id}"


class Spin(models.Model):
    """Database model for individual spins."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='spins')
    bet_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    result = models.JSONField()  # Store the spin result as JSON
    win_data = models.JSONField(null=True, blank=True)  # Win information
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Spin {self.id} for Game {self.game.id}"


# Data models for the application logic

@dataclass
class SpinConfig:
    """Configuration for a spin."""
    num_reels: int
    visible_rows: int


@dataclass
class SpinResult:
    """Result of a spin operation."""
    result: ReelResult
    win_data: Optional[WinData]
    payout: Decimal

    @property
    def is_win(self) -> bool:
        """Check if this spin resulted in a win."""
        return self.win_data is not None and self.payout > 0


@dataclass
class SpinResponse:
    """API response for a spin operation."""
    success: bool
    spin_id: Optional[str] = None
    result: Optional[ReelResult] = None
    win_data: Optional[WinData] = None
    payout: Optional[Decimal] = None
    current_balance: Optional[Decimal] = None
    message: Optional[str] = None
