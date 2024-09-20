# ChessMates

A Python-based Chess game with integrated Stockfish AI. Players can play against the AI and receive move feedback based on Stockfish’s analysis. The game dynamically adjusts the AI's difficulty based on the player’s performance.

## Features
- **Play Against AI**: Engage in a chess match against Stockfish, one of the strongest chess engines.
- **AI Difficulty Adjustment**: The AI difficulty dynamically changes based on the player’s material advantage or disadvantage.
- **Move Feedback**: After every game, get detailed feedback on each move (e.g., Good move, Okay move, Mistake, or Blunder).
- **Pawn Promotion**: Fully supports pawn promotion with a choice of Queen, Rook, Knight, or Bishop.
- **Resignation Option**: Players can resign during a game, and the AI will automatically be declared the winner.
- **Captured Pieces Display**: Track captured pieces and material advantages for both sides.
- **Game States**: Detects checkmate, stalemate, and draw conditions (e.g., insufficient material, 75-move rule).

## Requirements
- **Python**: 3.8+
- **Libraries**: 
  - Pillow (for images)
  - python-chess (for chess logic)
  - Tkinter (for GUI)
  - Stockfish (for AI)

### Python Libraries:
Install the required libraries by running:
```bash
pip install pillow python-chess stockfish
```

## How to Run
### Clone the repository:
```
git clone https://github.com/huynhloc03/ChessMates.git
cd ChessMates
```
### Install the required dependencies:
```
pip install -r requirements.txt
```
## Download and place Stockfish in the stockfish/ directory:
### You can adjust the path in the script if needed:
```
stockfish = Stockfish("stockfish/stockfish-windows-x86-64-avx2.exe")
```

## Run the game:
```
python main.py
```

## How to play:
### Choose Your Color:
At the start of the game, you will be prompted to choose your color (White or Black).

## Gameplay:
- Click on your pieces to highlight legal moves.
- After selecting your move, the AI will respond with its move.
- The game continues until checkmate, stalemate, or resignation.

## Feedback:
After the game ends, a feedback dialog will display each move's analysis, showing if it was a "Good move," "Okay move," "Mistake," or "Blunder."

## Resign:
You can resign at any point in the game using the Resign button.







