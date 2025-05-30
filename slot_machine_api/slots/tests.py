"""
Tests for the slot machine application.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
import json

from .models import Player, Symbol, Game, Spin


class SlotMachineAPITests(TestCase):
    """Test cases for the slot machine API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create a player for the test user
        self.player = Player.objects.create(
            user=self.user,
            balance=1000.00
        )

        # Create symbols with payout multipliers
        Symbol.objects.create(
            name='diamond', 
            image_path='graphics/0/symbols/0_diamond.png',
            payout_multiplier=3.0
        )
        Symbol.objects.create(
            name='floppy', 
            image_path='graphics/0/symbols/0_floppy.png',
            payout_multiplier=2.0
        )
        Symbol.objects.create(
            name='hourglass', 
            image_path='graphics/0/symbols/0_hourglass.png',
            payout_multiplier=1.5
        )
        Symbol.objects.create(
            name='hourglass2', 
            image_path='graphics/0/symbols/0_hourglass.png',
            payout_multiplier=1.5
        )
        Symbol.objects.create(
            name='telephone', 
            image_path='graphics/0/symbols/0_telephone.png',
            payout_multiplier=2.5
        )

        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_player_me_endpoint(self):
        """Test the player-me endpoint returns the correct player data."""
        url = reverse('player-me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '1000.00')

    def test_spin_endpoint(self):
        """Test the spin endpoint processes a spin correctly."""
        url = reverse('spin-spin')
        data = {'bet_size': '10.00'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('result', response.data)
        self.assertIn('current_balance', response.data)

        # Check player balance was updated
        self.player.refresh_from_db()
        self.assertLessEqual(self.player.balance, Decimal('990.00') + response.data['payout'])

    def test_spin_insufficient_balance(self):
        """Test the spin endpoint returns an error when the player has insufficient balance."""
        # Set player balance to 0
        self.player.balance = 0
        self.player.save()

        url = reverse('spin-spin')
        data = {'bet_size': '10.00'}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_spin_history(self):
        """Test the spin history endpoint returns the player's spin history."""
        # Create a game and some spins
        game = Game.objects.create(player=self.player)
        Spin.objects.create(
            game=game,
            bet_amount=10.00,
            result={'0': ['diamond', 'floppy', 'hourglass'], '1': ['floppy', 'diamond', 'telephone']}
        )

        url = reverse('spin-history')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
