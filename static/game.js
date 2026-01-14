const socket = io();

let currentRoomCode = '';
let playerName = '';

// Screen management
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 3000);
}

// Lobby actions
document.getElementById('create-btn').addEventListener('click', () => {
    const name = document.getElementById('create-name').value.trim();
    if (!name) {
        showError('Please enter your name');
        return;
    }
    playerName = name;
    socket.emit('create_room', { player_name: name });
});

document.getElementById('join-btn').addEventListener('click', () => {
    const name = document.getElementById('join-name').value.trim();
    const code = document.getElementById('room-code').value.trim().toUpperCase();
    
    if (!name) {
        showError('Please enter your name');
        return;
    }
    if (!code || code.length !== 4) {
        showError('Please enter a valid 4-letter room code');
        return;
    }
    
    playerName = name;
    socket.emit('join_room', { player_name: name, room_code: code });
});

// Socket event handlers
socket.on('room_created', (data) => {
    currentRoomCode = data.room_code;
    document.getElementById('display-room-code').textContent = data.room_code;
    showScreen('waiting-screen');
});

socket.on('player_joined', (data) => {
    // Game is starting
    showScreen('game-screen');
});

socket.on('game_state', (state) => {
    updateGameState(state);
});

socket.on('error', (data) => {
    showError(data.message);
});

socket.on('player_disconnected', () => {
    showError('Opponent disconnected');
    setTimeout(() => {
        location.reload();
    }, 2000);
});

socket.on('game_over', (data) => {
    showError(`Game Over! ${data.winner} wins!`);
});

// Game state update
function updateGameState(state) {
    currentRoomCode = state.room_code;
    
    // Update header info
    document.getElementById('hand-number').textContent = state.hand_number;
    document.getElementById('pot').textContent = state.pot;
    document.getElementById('game-room-code').textContent = state.room_code;
    
    // Update player info
    document.getElementById('your-name').textContent = state.your_name;
    document.getElementById('opponent-name').textContent = state.opponent_name;
    document.getElementById('your-chips').textContent = state.your_chips;
    document.getElementById('opponent-chips').textContent = state.opponent_chips;
    document.getElementById('your-bet').textContent = state.your_bet;
    document.getElementById('opponent-bet').textContent = state.opponent_bet;
    
    // Update cards
    const opponentCard = document.getElementById('opponent-card');
    opponentCard.querySelector('.card-content').textContent = state.opponent_card;
    
    // Color the opponent card based on suit
    const suit = state.opponent_card.slice(-1);
    if (suit === '♥' || suit === '♦') {
        opponentCard.style.color = 'red';
    } else {
        opponentCard.style.color = 'black';
    }
    
    const yourCard = document.getElementById('your-card');
    if (state.hand_over && state.your_card) {
        yourCard.classList.remove('card-back');
        yourCard.querySelector('.card-content').textContent = state.your_card;
        
        // Color your card based on suit
        const yourSuit = state.your_card.slice(-1);
        if (yourSuit === '♥' || yourSuit === '♦') {
            yourCard.style.color = 'red';
        } else {
            yourCard.style.color = 'black';
        }
    } else {
        yourCard.classList.add('card-back');
        yourCard.querySelector('.card-content').textContent = '?';
        yourCard.style.color = 'white';
    }
    
    // Update turn indicator and buttons
    const turnIndicator = document.getElementById('turn-indicator');
    const actionButtons = document.getElementById('action-buttons');
    const resultArea = document.getElementById('result-area');
    
    if (state.hand_over) {
        turnIndicator.textContent = 'Hand Over';
        turnIndicator.classList.remove('your-turn');
        actionButtons.style.display = 'none';
        document.getElementById('raise-controls').style.display = 'none';
        resultArea.style.display = 'block';
        
        // Show result message
        const resultMessage = document.getElementById('result-message');
        if (state.winner === state.your_name) {
            resultMessage.textContent = `🎉 You Win! 🎉`;
            resultMessage.style.color = '#28a745';
        } else if (state.winner === state.opponent_name) {
            resultMessage.textContent = `You Lose`;
            resultMessage.style.color = '#dc3545';
        } else {
            resultMessage.textContent = `It's a Tie!`;
            resultMessage.style.color = '#667eea';
        }
        
        // Show next hand button if both players have chips
        if (state.your_chips > 0 && state.opponent_chips > 0) {
            document.getElementById('next-hand-btn').style.display = 'inline-block';
        } else {
            document.getElementById('next-hand-btn').style.display = 'none';
        }
    } else {
        resultArea.style.display = 'none';
        actionButtons.style.display = 'flex';
        
        if (state.is_your_turn) {
            turnIndicator.textContent = 'Your Turn';
            turnIndicator.classList.add('your-turn');
            updateActionButtons(state);
        } else {
            turnIndicator.textContent = 'Waiting for opponent...';
            turnIndicator.classList.remove('your-turn');
            disableAllButtons();
        }
    }
}

function updateActionButtons(state) {
    const foldBtn = document.getElementById('fold-btn');
    const checkBtn = document.getElementById('check-btn');
    const callBtn = document.getElementById('call-btn');
    const raiseBtn = document.getElementById('raise-btn');
    
    // Always enable fold
    foldBtn.disabled = false;
    
    // Check button
    if (state.can_check) {
        checkBtn.disabled = false;
        checkBtn.style.display = 'inline-block';
    } else {
        checkBtn.disabled = true;
        checkBtn.style.display = 'none';
    }
    
    // Call button
    const callAmount = state.current_bet - state.your_bet;
    if (callAmount > 0) {
        callBtn.disabled = false;
        callBtn.style.display = 'inline-block';
        document.getElementById('call-amount').textContent = callAmount;
    } else {
        callBtn.disabled = true;
        callBtn.style.display = 'none';
    }
    
    // Raise button
    if (state.can_raise) {
        raiseBtn.disabled = false;
        document.getElementById('min-raise').textContent = state.min_raise;
        document.getElementById('raises-left').textContent = state.raises_left;
    } else {
        raiseBtn.disabled = true;
    }
}

function disableAllButtons() {
    document.getElementById('fold-btn').disabled = true;
    document.getElementById('check-btn').disabled = true;
    document.getElementById('call-btn').disabled = true;
    document.getElementById('raise-btn').disabled = true;
}

// Action button handlers
document.getElementById('fold-btn').addEventListener('click', () => {
    socket.emit('player_action', {
        room_code: currentRoomCode,
        action: 'fold'
    });
});

document.getElementById('check-btn').addEventListener('click', () => {
    socket.emit('player_action', {
        room_code: currentRoomCode,
        action: 'check'
    });
});

document.getElementById('call-btn').addEventListener('click', () => {
    socket.emit('player_action', {
        room_code: currentRoomCode,
        action: 'call'
    });
});

document.getElementById('raise-btn').addEventListener('click', () => {
    document.getElementById('action-buttons').style.display = 'none';
    document.getElementById('raise-controls').style.display = 'block';
    document.getElementById('raise-amount').value = '';
    document.getElementById('raise-amount').focus();
});

document.getElementById('confirm-raise-btn').addEventListener('click', () => {
    const amount = parseInt(document.getElementById('raise-amount').value);
    const minRaise = parseInt(document.getElementById('min-raise').textContent);
    
    if (!amount || amount < minRaise) {
        showError(`Minimum raise is ${minRaise}`);
        return;
    }
    
    socket.emit('player_action', {
        room_code: currentRoomCode,
        action: 'raise',
        amount: amount
    });
    
    document.getElementById('raise-controls').style.display = 'none';
    document.getElementById('action-buttons').style.display = 'flex';
});

document.getElementById('cancel-raise-btn').addEventListener('click', () => {
    document.getElementById('raise-controls').style.display = 'none';
    document.getElementById('action-buttons').style.display = 'flex';
});

document.getElementById('new-game-btn').addEventListener('click', () => {
    socket.emit('new_game', { room_code: currentRoomCode });
});

document.getElementById('next-hand-btn').addEventListener('click', () => {
    socket.emit('next_hand', { room_code: currentRoomCode });
});

// Allow Enter key for inputs
document.getElementById('create-name').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('create-btn').click();
    }
});

document.getElementById('room-code').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('join-btn').click();
    }
});

document.getElementById('raise-amount').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('confirm-raise-btn').click();
    }
});
