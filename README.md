# Indian Poker (Blind Man's Bluff)

A real-time online multiplayer card game where players see their opponent's card but not their own!

## Game Rules

- **Players**: 2 players (heads-up)
- **Starting Chips**: 100 chips each
- **Ante**: 1 chip per hand (forced bet)
- **Objective**: Win chips by having the higher card or making your opponent fold

### Betting Rules
- Each player can raise up to **2 times per hand**
- Minimum raise: **2x the previous raise amount**
- Actions available: **Check**, **Call**, **Raise**, **Fold**
- Players can go **all-in** with their remaining chips

### How to Play
1. Both players are dealt one card face-down
2. Each player places their card on their "forehead" (you see opponent's card, not yours)
3. Players bet based on what they see and how their opponent bets
4. After betting concludes, cards are revealed and highest card wins the pot
5. Continue playing hands until someone runs out of chips

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd indian-poker-game
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   - Go to `http://localhost:5000`
   - The game is now running locally!

## How to Play Online with a Friend

### Local Testing (Same Network)
1. Start the server with `python app.py`
2. Player 1 opens `http://localhost:5000` and creates a room
3. Player 2 opens `http://localhost:5000` in a different browser/tab and joins with the room code
4. Play!

### Playing Over the Internet

To play with someone not on your network, you'll need to deploy the app to a hosting service. Here are the easiest options:

#### Option 1: Render.com (Recommended - Free)

1. Create a free account at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (you'll need to push this code to GitHub first)
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. Click "Create Web Service"
6. Your game will be live at the provided URL!

#### Option 2: Railway.app (Also Free)

1. Create account at [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Railway auto-detects Python and deploys
5. Get your live URL and share with friends!

#### Option 3: Heroku

1. Install Heroku CLI
2. Create a `Procfile` with: `web: python app.py`
3. Run:
   ```bash
   heroku create your-poker-game
   git push heroku main
   ```

## Project Structure

```
indian-poker-game/
├── app.py                 # Flask server & WebSocket handlers
├── game_logic.py          # Core game logic (betting, cards, rules)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
└── static/
    ├── style.css         # Styling
    └── game.js           # Client-side JavaScript & WebSocket
```

## Features

✅ Real-time multiplayer using WebSockets  
✅ Room-based matchmaking with 4-letter codes  
✅ Beautiful, modern UI  
✅ Mobile-responsive design  
✅ Enforces all betting rules automatically  
✅ Tracks chip counts across multiple hands  
✅ Shows opponent's card but hides yours  
✅ Automatic hand progression  
✅ "New Game" button to reset chips  

## Technologies Used

- **Backend**: Python, Flask, Flask-SocketIO
- **Frontend**: HTML, CSS, JavaScript
- **Real-time Communication**: WebSockets (Socket.IO)
- **Deployment**: Ready for Render, Railway, or Heroku

## Troubleshooting

**Issue**: Can't connect to the game  
**Solution**: Make sure the server is running and you're using the correct URL

**Issue**: Opponent disconnected  
**Solution**: The page will automatically reload. Create a new room and share the code again

**Issue**: Buttons not working  
**Solution**: Make sure it's your turn (turn indicator shows "Your Turn" in green)

## Future Enhancements (Optional)

- [ ] Add sound effects
- [ ] Add chat functionality
- [ ] Support for more than 2 players
- [ ] Leaderboard/statistics
- [ ] Custom chip amounts
- [ ] Tournament mode

---

Enjoy playing Indian Poker! 🃏
