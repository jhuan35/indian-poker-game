from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
from game_logic import Game, GameRoom

app = Flask(__name__)
app.config['SECRET_KEY'] = 'indian-poker-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active game rooms
game_rooms = {}

def generate_room_code():
    """Generate a random 4-letter room code"""
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=4))
        if code not in game_rooms:
            return code

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_room')
def handle_create_room(data):
    """Create a new game room"""
    room_code = generate_room_code()
    player_name = data.get('player_name', 'Player 1')
    
    game_rooms[room_code] = GameRoom(room_code)
    game_rooms[room_code].add_player(request.sid, player_name)
    
    join_room(room_code)
    emit('room_created', {'room_code': room_code, 'player_name': player_name})

@socketio.on('join_room')
def handle_join_room(data):
    """Join an existing game room"""
    room_code = data.get('room_code', '').upper()
    player_name = data.get('player_name', 'Player 2')
    
    if room_code not in game_rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = game_rooms[room_code]
    
    if room.is_full():
        emit('error', {'message': 'Room is full'})
        return
    
    room.add_player(request.sid, player_name)
    join_room(room_code)
    
    # Notify both players that the game is starting
    emit('player_joined', {'player_name': player_name}, room=room_code)
    
    # Start the game
    room.start_new_hand()
    emit('game_state', room.get_game_state_for_player(request.sid), room=request.sid)
    
    # Send game state to the other player
    other_player_sid = room.get_other_player_sid(request.sid)
    emit('game_state', room.get_game_state_for_player(other_player_sid), room=other_player_sid)

@socketio.on('player_action')
def handle_player_action(data):
    """Handle player actions: check, call, raise, fold"""
    room_code = data.get('room_code')
    action = data.get('action')
    amount = data.get('amount', 0)
    
    if room_code not in game_rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = game_rooms[room_code]
    
    # Process the action
    result = room.process_action(request.sid, action, amount)
    
    if not result['success']:
        emit('error', {'message': result['message']})
        return
    
    # Send updated game state to both players
    for player_sid in room.players.keys():
        emit('game_state', room.get_game_state_for_player(player_sid), room=player_sid)
    
    # If hand is over, just send game over if someone is out of chips
    if room.game.hand_over:
        if not room.can_continue():
            # Game over - someone is out of chips
            emit('game_over', room.get_winner_info(), room=room_code)

@socketio.on('next_hand')
def handle_next_hand(data):
    """Start the next hand (called when player clicks Next Hand button)"""
    room_code = data.get('room_code')
    
    if room_code not in game_rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = game_rooms[room_code]
    
    if room.can_continue():
        room.start_new_hand()
        for player_sid in room.players.keys():
            emit('game_state', room.get_game_state_for_player(player_sid), room=player_sid)
    else:
        emit('game_over', room.get_winner_info(), room=room_code)

@socketio.on('new_game')
def handle_new_game(data):
    """Start a completely new game (reset chips to 100)"""
    room_code = data.get('room_code')
    
    if room_code not in game_rooms:
        emit('error', {'message': 'Room not found'})
        return
    
    room = game_rooms[room_code]
    room.reset_game()
    room.start_new_hand()
    
    for player_sid in room.players.keys():
        emit('game_state', room.get_game_state_for_player(player_sid), room=player_sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle player disconnection"""
    # Find and clean up the room
    for room_code, room in list(game_rooms.items()):
        if request.sid in room.players:
            emit('player_disconnected', room=room_code)
            del game_rooms[room_code]
            break

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
