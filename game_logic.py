import random

class Game:
    """Core game logic for Indian Poker"""
    
    CARD_VALUES = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
        'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    
    CARD_SUITS = ['♠', '♥', '♦', '♣']
    
    def __init__(self, player1_id, player2_id, starting_chips=100):
        self.player1_id = player1_id
        self.player2_id = player2_id
        
        # Chip stacks
        self.chips = {
            player1_id: starting_chips,
            player2_id: starting_chips
        }
        
        # Current hand state
        self.pot = 0
        self.current_bet = 0
        self.player_bets = {player1_id: 0, player2_id: 0}
        self.cards = {}
        self.folded = {player1_id: False, player2_id: False}
        self.raise_count = {player1_id: 0, player2_id: 0}
        self.last_raise_amount = 0
        self.current_player = player1_id
        self.hand_over = False
        self.winner = None
        self.hand_number = 0
        self.players_acted = set()  # Track which players have acted this round
        
    def start_new_hand(self):
        """Start a new hand - deal cards and post antes"""
        self.hand_number += 1
        self.pot = 0
        self.current_bet = 0
        self.player_bets = {self.player1_id: 0, self.player2_id: 0}
        self.folded = {self.player1_id: False, self.player2_id: False}
        self.raise_count = {self.player1_id: 0, self.player2_id: 0}
        self.last_raise_amount = 0
        self.hand_over = False
        self.winner = None
        self.players_acted = set()  # Reset for new hand
        
        # Deal cards
        deck = [(rank, suit) for rank in self.CARD_VALUES.keys() for suit in self.CARD_SUITS]
        random.shuffle(deck)
        
        self.cards = {
            self.player1_id: deck[0],
            self.player2_id: deck[1]
        }
        
        # Post antes (1 chip each)
        for player_id in [self.player1_id, self.player2_id]:
            if self.chips[player_id] >= 1:
                self.chips[player_id] -= 1
                self.player_bets[player_id] = 1
                self.pot += 1
            else:
                # Player is all-in with ante
                ante = self.chips[player_id]
                self.chips[player_id] = 0
                self.player_bets[player_id] = ante
                self.pot += ante
        
        self.current_bet = 1
        # Player 1 acts first
        self.current_player = self.player1_id
        
    def can_check(self, player_id):
        """Check if player can check"""
        return self.player_bets[player_id] == self.current_bet
    
    def can_raise(self, player_id):
        """Check if player can raise (hasn't raised 2 times yet)"""
        return self.raise_count[player_id] < 2 and self.chips[player_id] > 0
    
    def get_min_raise(self):
        """Get minimum raise amount (2x the last raise)"""
        if self.last_raise_amount == 0:
            # First raise can be any amount
            return 1
        return self.last_raise_amount * 2
    
    def process_action(self, player_id, action, amount=0):
        """Process a player action and return result"""
        if self.hand_over:
            return {'success': False, 'message': 'Hand is over'}
        
        if player_id != self.current_player:
            return {'success': False, 'message': 'Not your turn'}
        
        if action == 'fold':
            self.folded[player_id] = True
            self.hand_over = True
            other_player = self.get_other_player(player_id)
            self.winner = other_player
            self.chips[other_player] += self.pot
            return {'success': True, 'message': 'Folded'}
        
        elif action == 'check':
            if not self.can_check(player_id):
                return {'success': False, 'message': 'Cannot check - must call or raise'}
            
            self.players_acted.add(player_id)
            
            # Check if both players have acted and bets are equal
            other_player = self.get_other_player(player_id)
            if self.player_bets[player_id] == self.player_bets[other_player] and len(self.players_acted) == 2:
                # Both players have checked, go to showdown
                self.showdown()
            else:
                # Pass action to other player
                self.current_player = other_player
            
            return {'success': True, 'message': 'Checked'}
        
        elif action == 'call':
            call_amount = self.current_bet - self.player_bets[player_id]
            
            if call_amount <= 0:
                return {'success': False, 'message': 'Nothing to call'}
            
            # Handle all-in
            if call_amount >= self.chips[player_id]:
                call_amount = self.chips[player_id]
            
            self.chips[player_id] -= call_amount
            self.player_bets[player_id] += call_amount
            self.pot += call_amount
            
            # After call, go to showdown
            self.showdown()
            
            return {'success': True, 'message': f'Called {call_amount}'}
        
        elif action == 'raise':
            if not self.can_raise(player_id):
                return {'success': False, 'message': 'Cannot raise - already raised 2 times'}
            
            # Calculate raise amount
            call_amount = self.current_bet - self.player_bets[player_id]
            min_raise = self.get_min_raise()
            
            if amount < min_raise:
                return {'success': False, 'message': f'Minimum raise is {min_raise}'}
            
            total_amount = call_amount + amount
            
            # Handle all-in
            if total_amount >= self.chips[player_id]:
                total_amount = self.chips[player_id]
                amount = total_amount - call_amount
            
            self.chips[player_id] -= total_amount
            self.player_bets[player_id] += total_amount
            self.pot += total_amount
            self.current_bet = self.player_bets[player_id]
            self.last_raise_amount = amount
            self.raise_count[player_id] += 1
            
            # When someone raises, reset the players_acted tracker
            self.players_acted = {player_id}  # Only the raiser has acted in this new round
            
            # Switch to other player
            self.current_player = self.get_other_player(player_id)
            
            return {'success': True, 'message': f'Raised by {amount}'}
        
        return {'success': False, 'message': 'Invalid action'}
    
    def showdown(self):
        """Determine winner and award pot"""
        self.hand_over = True
        
        # Compare cards
        card1_value = self.CARD_VALUES[self.cards[self.player1_id][0]]
        card2_value = self.CARD_VALUES[self.cards[self.player2_id][0]]
        
        if card1_value > card2_value:
            self.winner = self.player1_id
        elif card2_value > card1_value:
            self.winner = self.player2_id
        else:
            # Tie - split pot
            self.winner = 'tie'
            self.chips[self.player1_id] += self.pot // 2
            self.chips[self.player2_id] += self.pot // 2
            return
        
        self.chips[self.winner] += self.pot
    
    def get_other_player(self, player_id):
        """Get the other player's ID"""
        return self.player2_id if player_id == self.player1_id else self.player1_id
    
    def get_card_string(self, card):
        """Convert card tuple to string"""
        return f"{card[0]}{card[1]}"


class GameRoom:
    """Manages a game room with two players"""
    
    def __init__(self, room_code):
        self.room_code = room_code
        self.players = {}  # {session_id: player_name}
        self.game = None
        
    def add_player(self, session_id, player_name):
        """Add a player to the room"""
        self.players[session_id] = player_name
        
    def is_full(self):
        """Check if room has 2 players"""
        return len(self.players) >= 2
    
    def start_new_hand(self):
        """Start a new hand"""
        if len(self.players) != 2:
            return False
        
        player_ids = list(self.players.keys())
        
        if self.game is None:
            self.game = Game(player_ids[0], player_ids[1])
        
        self.game.start_new_hand()
        return True
    
    def reset_game(self):
        """Reset game to starting state"""
        player_ids = list(self.players.keys())
        self.game = Game(player_ids[0], player_ids[1])
    
    def process_action(self, player_id, action, amount=0):
        """Process a player action"""
        if self.game is None:
            return {'success': False, 'message': 'Game not started'}
        
        return self.game.process_action(player_id, action, amount)
    
    def get_other_player_sid(self, player_id):
        """Get the other player's session ID"""
        for sid in self.players.keys():
            if sid != player_id:
                return sid
        return None
    
    def can_continue(self):
        """Check if game can continue (both players have chips)"""
        if self.game is None:
            return False
        
        for player_id in self.players.keys():
            if self.game.chips[player_id] <= 0:
                return False
        
        return True
    
    def get_winner_info(self):
        """Get winner information when game is over"""
        if self.game is None:
            return {}
        
        winner_sid = None
        for sid in self.players.keys():
            if self.game.chips[sid] > 0:
                winner_sid = sid
                break
        
        return {
            'winner': self.players.get(winner_sid, 'Unknown'),
            'chips': self.game.chips
        }
    
    def get_game_state_for_player(self, player_id):
        """Get game state from a player's perspective"""
        if self.game is None:
            return {}
        
        other_player_id = self.get_other_player_sid(player_id)
        
        # Player sees opponent's card but not their own
        return {
            'room_code': self.room_code,
            'hand_number': self.game.hand_number,
            'your_chips': self.game.chips[player_id],
            'opponent_chips': self.game.chips[other_player_id],
            'your_name': self.players[player_id],
            'opponent_name': self.players[other_player_id],
            'pot': self.game.pot,
            'current_bet': self.game.current_bet,
            'your_bet': self.game.player_bets[player_id],
            'opponent_bet': self.game.player_bets[other_player_id],
            'opponent_card': self.game.get_card_string(self.game.cards[other_player_id]),
            'your_card': self.game.get_card_string(self.game.cards[player_id]) if self.game.hand_over else None,
            'is_your_turn': self.game.current_player == player_id,
            'hand_over': self.game.hand_over,
            'winner': self.players.get(self.game.winner, 'Tie') if self.game.hand_over else None,
            'can_check': self.game.can_check(player_id),
            'can_raise': self.game.can_raise(player_id),
            'min_raise': self.game.get_min_raise(),
            'raises_left': 2 - self.game.raise_count[player_id]
        }
