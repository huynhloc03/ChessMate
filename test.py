import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
import chess
from stockfish import Stockfish
import os
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from tkinter import PhotoImage, Label



# Set the path to your chess piece images folder
IMAGE_PATH = "D:/ChessMates/image"  # Ensure the path uses forward slashes

# Load piece images into a dictionary
pieces_names = ['white-rook', 'white-knight', 'white-bishop', 'white-queen', 'white-king', 'white-pawn',
                'black-rook', 'black-knight', 'black-bishop', 'black-queen', 'black-king', 'black-pawn']

pieces_images = {name: Image.open(os.path.join(IMAGE_PATH, f"{name}.png")).resize((125, 125)) for name in pieces_names}

# Initialize Stockfish AI
stockfish = Stockfish("D:/ChessMates/stockfish/stockfish-windows-x86-64-avx2.exe")  # Ensure path uses forward slashes
stockfish.set_skill_level(1)  # Set the AI's starting skill level

# Global variable to track if player is white
player_is_white = True

# Initialize the chess board
# board = chess.Board("8/7P/8/8/8/8/8/8 w - - 0 1")  # Initialize the board to the starting position
# board = chess.Board(fen="8/7P/8/8/8/8/8/7k w - - 0 1") 
# board = chess.Board(fen="8/7P/8/4k3/7p/5K2/8/8 w - - 0 1")
board = chess.Board()
# Function to adjust AI rank based on difficulty changes
def get_title_by_difficulty_changes(skill_level):
    if skill_level >= 9:
        return "Grandmaster"
    elif skill_level >= 7:
        return "International Master"
    elif skill_level >= 5:
        return "Master"
    elif skill_level >= 3:
        return "Expert"
    elif skill_level >= 2:
        return "Intermediate"
    else:
        return "Beginner"


def get_title_by_elo(elo):
    if elo >= 2500:
        return "Grandmaster"
    elif elo >= 2300:
        return "International Master"
    elif elo >= 2000:
        return "Master"
    elif elo >= 1700:
        return "Expert"
    elif elo >= 1400:
        return "Intermediate"
    elif elo >= 1100:
        return "Novice"
    else:
        return "Beginner"

    
# Initialize global variables for tracking rank increments
ai_skill_level = 3  # Default starting skill level (you can adjust this as needed)
ai_difficulty_changes = 1  # Counter for how many times AI difficulty has been increased
player_difficulty_changes = 1  # You can also add this for player rank logic
player_captured_pieces = 0
ai_captured_pieces = 0
move_feedback = []


piece_values = {
    'pawn': 1,
    'knight': 3,
    'bishop': 3,
    'rook': 5,
    'queen': 9,
    'king': 0  # King's value is not counted
}



# Global variables to store captured pieces and their values
player_captured = []
ai_captured = []
player_material = 0
ai_material = 0




# Get title by Elo for Player and AI
player_title = get_title_by_difficulty_changes(ai_difficulty_changes)
ai_title = get_title_by_difficulty_changes(player_difficulty_changes)

# Tkinter window setup
window = tk.Tk()
window.title("Chess AI")
# Function to render chessboard and UI


# Center the entire window on the screen
window.geometry("1400x1100")
window.update_idletasks()  # Force an update to calculate window dimensions

# Create frames for layout
main_frame = tk.Frame(window)
main_frame.pack(fill=tk.BOTH, expand=True)

# Chessboard canvas setup (adjusted to move to the right)
canvas = tk.Canvas(window, width=1000, height=1000)
canvas.pack(side=tk.LEFT, padx=60, pady=20)  # Keep the chessboard slightly to the right

# Move log, labels, and reset button frame (right side)
log_frame = tk.Frame(window)
log_frame.pack(side=tk.RIGHT, padx=30, pady=10)

# AI label with title at the top
ai_label = tk.Label(log_frame, text=f"AI - {ai_title}", font=("Arial", 14, "bold"))
ai_label.pack()# Add space between AI rank and move log

# AI Captures section
ai_captures_label = tk.Label(log_frame, text="AI Captures:")
ai_captures_label.pack(anchor="w", padx=10)  # Added padx for alignment

ai_captures_icons_frame = tk.Frame(log_frame)  # Frame for AI captured piece icons
ai_captures_icons_frame.pack(anchor="w", padx=10)

ai_material_label = tk.Label(log_frame, text="AI Material Advantage: 0")
ai_material_label.pack(anchor="w", padx=10)  # Added padx for alignment


# Move log Text widget (non-editable)
move_log = tk.Text(log_frame, height=35, width=40, state=tk.DISABLED)  # Increased height for more space
move_log.pack(pady=(0, 20))
# Configure tags for coloring moves
move_log.tag_configure("player_move", foreground="red")  # Player moves in red
move_log.tag_configure("ai_move", foreground="black")    # AI moves in black (default)


# Button to reset the game (below the move log)
reset_button = tk.Button(log_frame, text="Reset Game", command=lambda: reset_game())
reset_button.pack(pady=(0, 10))

# Add the Resign Button to the UI
resign_button = tk.Button(log_frame, text="Resign", command=lambda: resign_game())
resign_button.pack(pady=(0, 10))


# Player label and title at the bottom
player_label = tk.Label(log_frame, text=f"Player - {player_title}", font=("Arial", 14, "bold"))
player_label.pack(pady=(20, 0))  # Add space between reset button and Player label

# Frame for displaying captured pieces and material values
capture_frame = tk.Frame(log_frame)
capture_frame.pack(pady=(20, 0))

# Space between AI and Player sections
separator = tk.Label(capture_frame, text=" ", font=("Arial", 12))
separator.grid(row=2, column=0)

# Player Captures section
player_captures_label = tk.Label(log_frame, text="Player Captures:")
player_captures_label.pack(anchor="w", padx=10)  # Added padx for alignment

player_captures_icons_frame = tk.Frame(log_frame)  # Frame for Player captured piece icons
player_captures_icons_frame.pack(anchor="w", padx=10)

player_material_label = tk.Label(log_frame, text="Player Material Advantage: 0")
player_material_label.pack(anchor="w", padx=10)  # Added padx for alignment

# Fullscreen toggle
is_fullscreen = True  # Start in fullscreen mode

# Toggle fullscreen mode
def toggle_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    window.attributes("-fullscreen", is_fullscreen)
    adjust_log_position()  # Adjust the log position on fullscreen toggle

# Exit fullscreen mode
def exit_fullscreen(event=None):
    global is_fullscreen
    is_fullscreen = False
    window.attributes("-fullscreen", False)
    adjust_log_position()  # Adjust the log position when exiting fullscreen

# Adjust move_log position based on fullscreen state
def adjust_log_position():
    if is_fullscreen:
        log_frame.pack_configure(padx=150)  # Move the move_log closer when in fullscreen
    else:
        log_frame.pack_configure(padx=30)  # Default padding when not in fullscreen

# Bind the Escape key to exit full-screen mode
window.bind("<Escape>", exit_fullscreen)

# Bind the F11 key to toggle full-screen mode
window.bind("<F11>", toggle_fullscreen)

# Automatically start in fullscreen mode
window.attributes("-fullscreen", True)

# Adjust the move log position as we're starting in fullscreen
adjust_log_position()

# Global variables for tracking moves
selected_square = None  # Stores the first selected square (where the piece is)
player_turn = True  # True if it's the player's turn, False if it's the AI's turn
highlighted_moves = []  # List of valid squares for highlighting
capturable_squares = []  # List of squares where pieces can be captured

# Function to log player and AI moves
def log_move(move_san, player):
    move_log.config(state=tk.NORMAL)  # Enable text input

    if player == "Player":
        move_log.insert(tk.END, f"{player}: {move_san}\n", "player_move")  # Add a tag for player moves
    else:
        move_log.insert(tk.END, f"{player}: {move_san}\n", "ai_move")  # Add a tag for AI moves

    move_log.config(state=tk.DISABLED)  # Disable text input to make it non-editable
    move_log.see(tk.END)

    # Analyze the move and store feedback
    analyze_move(move_san, player)

    
# Function to convert a piece to its image file name
def get_piece_image(piece):
    if piece is None:
        return None
    piece_type = piece.piece_type
    color = 'white' if piece.color else 'black'
    
    # Mapping chess pieces from their internal representation to image names
    piece_dict = {
        chess.PAWN: 'pawn',
        chess.ROOK: 'rook',
        chess.KNIGHT: 'knight',
        chess.BISHOP: 'bishop',
        chess.QUEEN: 'queen',
        chess.KING: 'king'
    }
    
    piece_name = f"{color}-{piece_dict[piece_type]}"
    return pieces_images.get(piece_name)

# Function to render the chessboard using Pillow and include pieces, labels, and valid move dots
def render_board():
    # Create an empty image for the chessboard (with labels inside squares)
    img = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(img)

    # Chessboard square size
    square_size = 125
    colors = ['#D18B47', '#FFCE9E']  # Dark and light square colors
    dot_color = "#FF0000"  # Red dots for valid moves
    capture_color = "#FFA07A"  # Light red color for capturing pieces
    check_highlight_color = "#FF7F7F"  # Light red color for check or checkmate highlight
    
    # Define your custom font and size
    font_path = "arial.ttf"  # Path to your .ttf font file (you can choose any font)
    font_size = 15  # Adjust the size as needed
    font = ImageFont.truetype(font_path, font_size)

    # Determine if the board is in check or checkmate
    in_checkmate = board.is_checkmate()
    in_check = board.is_check()

    # Get the player's king color based on their side
    player_king_color = chess.WHITE if player_is_white else chess.BLACK
    opponent_king_color = chess.BLACK if player_is_white else chess.WHITE

    # Highlight the correct king if they are in check or checkmate
    king_square = None
    if in_check or in_checkmate:
        if board.turn == player_king_color:  # If it's the player's turn and they are in check
            king_square = board.king(player_king_color)  # Highlight the player's king
        else:
            king_square = board.king(opponent_king_color)  # Highlight the opponent's king

    for rank in range(8):
        for file in range(8):
            # Adjust rank and file based on player color
            real_rank = 7 - rank if player_is_white else rank
            real_file = file if player_is_white else 7 - file

            x0, y0 = file * square_size, rank * square_size
            x1, y1 = (file + 1) * square_size, (rank + 1) * square_size

            color = colors[(real_rank + real_file) % 2]  # Alternate colors for squares

            # Check or checkmate highlighting for the correct king's square
            square = chess.square(real_file, real_rank)
            if (in_check or in_checkmate) and square == king_square:
                draw.rectangle([x0, y0, x1, y1], fill=check_highlight_color)  # Highlight correct king's square
            else:
                draw.rectangle([x0, y0, x1, y1], fill=color)

            # Highlight valid moves and capture squares correctly
            if chess.square(real_file, real_rank) in highlighted_moves:
                dot_x, dot_y = (x0 + x1) // 2, (y0 + y1) // 2
                draw.ellipse((dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5), fill=dot_color)

            if chess.square(real_file, real_rank) in capturable_squares:
                draw.rectangle([x0, y0, x1, y1], fill=capture_color)

            # Get piece on the current square
            piece = board.piece_at(chess.square(real_file, real_rank))
            piece_image = get_piece_image(piece)
            if piece_image:
                img.paste(piece_image, (x0, y0), piece_image)

            # Draw labels for ranks (left side) and files (bottom side)
            if file == 0:
                draw.text((x0 + 5, y0 + 5), str(8 - rank if player_is_white else rank + 1), fill="black", font=font)
            if rank == 7:
                draw.text((x0 + square_size - 8, y0 + square_size - 15), chr(file + ord('a') if player_is_white else 104 - file), fill="black", font=font)

    # Convert the Pillow image to a format Tkinter can use
    img_tk = ImageTk.PhotoImage(img)

    # Display the chessboard on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
    canvas.image = img_tk  # Keep a reference to avoid garbage collection


def highlight_valid_moves(square):
    global highlighted_moves, capturable_squares
    highlighted_moves = []
    capturable_squares = []
    piece = board.piece_at(square)

    if piece and piece.color == (chess.WHITE if player_is_white else chess.BLACK):  # Only allow the player to move their pieces
        for move in board.legal_moves:
            if move.from_square == square:
                destination_piece = board.piece_at(move.to_square)
                if destination_piece and destination_piece.color != piece.color:
                    capturable_squares.append(move.to_square)  # Highlight capturable squares
                else:
                    highlighted_moves.append(move.to_square)  # Highlight empty valid squares
        print(f"Valid moves for {piece}: {highlighted_moves}")  # Debugging valid moves




# Graphical function to handle pawn promotion with images
def pawn_promotion_dialog():
    promotion_window = tk.Toplevel(window)
    
    # Set the title of the window
    promotion_window.title("Choose Promotion Piece")
    
    # Change the background color based on the player's color
    if player_is_white:
        bg_color = "black"  # Set to black if the player is white
        fg_color = "white"  # Text color for better contrast
    else:
        bg_color = "white"  # Set to white if the player is black
        fg_color = "black"  # Text color for better contrast
    
    promotion_window.configure(background=bg_color)  # Set the window's background color

    promotion_piece = tk.StringVar()  # Variable to store the chosen promotion piece

    def promote_to(piece_type):
        promotion_piece.set(piece_type)
        promotion_window.destroy()

    # Create a label with the background color adjusted to match the window
    tk.Label(promotion_window, text="Choose your promotion piece:", bg=bg_color, fg=fg_color).pack(pady=10)

    # Load images for the promotion options
    queen_img = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-queen.png")).resize((60, 60)))
    rook_img = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-rook.png")).resize((60, 60)))
    bishop_img = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-bishop.png")).resize((60, 60)))
    knight_img = ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-knight.png")).resize((60, 60)))

    # Create buttons with images for the promotion options
    queen_button = tk.Button(promotion_window, image=queen_img, command=lambda: promote_to('q'), bg=bg_color)
    queen_button.image = queen_img  # Keep a reference to avoid garbage collection
    queen_button.pack(side=tk.LEFT)

    rook_button = tk.Button(promotion_window, image=rook_img, command=lambda: promote_to('r'), bg=bg_color)
    rook_button.image = rook_img  # Keep a reference to avoid garbage collection
    rook_button.pack(side=tk.LEFT)

    bishop_button = tk.Button(promotion_window, image=bishop_img, command=lambda: promote_to('b'), bg=bg_color)
    bishop_button.image = bishop_img  # Keep a reference to avoid garbage collection
    bishop_button.pack(side=tk.LEFT)

    knight_button = tk.Button(promotion_window, image=knight_img, command=lambda: promote_to('n'), bg=bg_color)
    knight_button.image = knight_img  # Keep a reference to avoid garbage collection
    knight_button.pack(side=tk.LEFT)

    # Make the window wait until a selection is made
    window.wait_window(promotion_window)

    return promotion_piece.get()  # Return the chosen piece type ('q', 'r', 'b', 'n')


# Function to handle pawn promotion
def handle_pawn_promotion(move):
    piece = board.piece_at(move.from_square)
    if piece and piece.piece_type == chess.PAWN and (chess.square_rank(move.to_square) == 0 or chess.square_rank(move.to_square) == 7):
        promotion_piece = pawn_promotion_dialog()
        print(f"Promotion piece chosen: {promotion_piece}")  # Debug statement to check what is returned
        if promotion_piece:
            move = chess.Move.from_uci(move.uci() + promotion_piece)  # Add promotion symbol
            print(f"Pawn promoted to {promotion_piece}, new move: {move}")  # Debug statement for promotion
        else:
            move = chess.Move.from_uci(move.uci() + "q")  # Default to queen if nothing chosen
            print("Invalid input. Pawn promotion defaulted to queen.")  # Debugging default promotion
    return move


# Function to handle en passant move
def handle_en_passant(move):
    if board.is_en_passant(move):
        print(f"En passant move detected: {move}")
        # The captured pawn is on the same rank as the moved pawn's destination
        captured_pawn_square = chess.square(chess.square_file(move.to_square), chess.square_rank(move.from_square))
        board.remove_piece_at(captured_pawn_square)  # Remove the captured pawn


def adjust_ranks():
    global ai_skill_level, player_material, ai_material, ai_title

    print(f"Player material: {player_material}, AI material: {ai_material}")

    material_difference = ai_material - player_material  # AI's advantage in material

    # If the player is losing by 4 or more material points, decrease AI difficulty
    if material_difference >= 4:
        # Calculate how many times the AI should be reduced by dividing material difference by 4
        difficulty_decrease = material_difference // 4
        new_ai_skill_level = max(ai_skill_level - difficulty_decrease, 1)  # Ensure AI skill level doesn't drop below 1
        if new_ai_skill_level < ai_skill_level:
            ai_skill_level = new_ai_skill_level
            print(f"Player is losing. AI skill level decreased to {ai_skill_level}")
            # Update AI title based on difficulty changes
            ai_title = get_title_by_difficulty_changes(ai_skill_level)
            ai_label.config(text=f"AI - {ai_title}")  # Update the AI title in the UI
    # If the player is winning by 2 or more material points, increase AI difficulty
    elif player_material >= ai_material + 2:
        if ai_skill_level < 10:  # Cap the AI skill level at 10
            ai_skill_level += 1
            print(f"Player is winning. AI skill level increased to {ai_skill_level}")
            # Update AI title based on difficulty changes
            ai_title = get_title_by_difficulty_changes(ai_skill_level)
            ai_label.config(text=f"AI - {ai_title}")  # Update the AI title in the UI
        else:
            print("AI skill level is already at max.")

    # Set the new skill level in Stockfish
    stockfish.set_skill_level(ai_skill_level)
    print(f"Stockfish skill level set to: {ai_skill_level}")

def load_captured_piece_images():
    piece_icons = {
        'p': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "black-pawn.png")).resize((25, 25))),
        'r': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "black-rook.png")).resize((25, 25))),
        'n': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "black-knight.png")).resize((25, 25))),
        'b': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "black-bishop.png")).resize((25, 25))),
        'q': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "black-queen.png")).resize((25, 25))),
        'P': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-pawn.png")).resize((25, 25))),
        'R': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-rook.png")).resize((25, 25))),
        'N': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-knight.png")).resize((25, 25))),
        'B': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-bishop.png")).resize((25, 25))),
        'Q': ImageTk.PhotoImage(Image.open(os.path.join(IMAGE_PATH, "white-queen.png")).resize((25, 25))),
    }
    return piece_icons

piece_icons = load_captured_piece_images()



def get_piece_name_by_type(piece_type):
    piece_dict = {
        chess.PAWN: 'pawn',
        chess.ROOK: 'rook',
        chess.KNIGHT: 'knight',
        chess.BISHOP: 'bishop',
        chess.QUEEN: 'queen',
        chess.KING: 'king'
    }
    return piece_dict[piece_type]

# AI move handling
def ai_move():
    global player_turn, ai_material

    try:
        stockfish.set_fen_position(board.fen())  # Set FEN for the current board position
        move = stockfish.get_best_move()  # Get AI's best move

        if move:  # Ensure Stockfish provides a move
            move_san = board.san(chess.Move.from_uci(move))  # Get SAN notation before pushing
            captured_piece = board.piece_at(chess.Move.from_uci(move).to_square)
            if captured_piece:
                ai_captured.append(captured_piece.symbol().lower())
                ai_material += piece_values[get_piece_name_by_type(captured_piece.piece_type)]
                print(f"AI captured a piece: {captured_piece.symbol().lower()}")
                update_captured_pieces()  # Update UI with captured pieces and material values

            board.push_san(move)  # Push the move using UCI format
            
            # Log the AI move in SAN format
            log_move(move_san, "AI")
            
            render_board()
            check_game_over()  # Check if the game is over

            # Adjust AI rank after the move
            adjust_ranks()

        player_turn = True  # After AI's move, it's the player's turn again
    except Exception as e:
        print(f"Error during Stockfish move: {e}")
        messagebox.showerror("Stockfish Error", "The Stockfish process has crashed.")


piece_name_map = {
    'p': 'pawn',
    'r': 'rook',
    'n': 'knight',
    'b': 'bishop',
    'q': 'queen',
    'k': 'king'
}

def update_captured_pieces():
    global player_material, ai_material

    # Clear previous icons
    for widget in ai_captures_icons_frame.winfo_children():
        widget.destroy()

    for widget in player_captures_icons_frame.winfo_children():
        widget.destroy()

    # Display captured pieces for the player (with icons)
    for piece in player_captured:
        piece_name = piece_name_map.get(piece.lower(), 'pawn')  # Ensure lowercase lookup and map shorthand to full name
        if player_is_white:
            color = 'black'  # Player captured AI's black pieces
        else:
            color = 'white'  # Player captured AI's white pieces
        piece_image = PhotoImage(file=f"{IMAGE_PATH}/{color}-{piece_name}.png").subsample(3, 3)  # Scale down image
        piece_label = tk.Label(player_captures_icons_frame, image=piece_image)
        piece_label.image = piece_image  # Keep a reference to avoid garbage collection
        piece_label.pack(side="left")  # Stack the icons horizontally

    # Display captured pieces for the AI (with icons)
    for piece in ai_captured:
        piece_name = piece_name_map.get(piece.lower(), 'pawn')  # Ensure lowercase lookup and map shorthand to full name
        if player_is_white:
            color = 'white'  # AI captured player's white pieces
        else:
            color = 'black'  # AI captured player's black pieces
        piece_image = PhotoImage(file=f"{IMAGE_PATH}/{color}-{piece_name}.png").subsample(3, 3)  # Scale down image
        piece_label = tk.Label(ai_captures_icons_frame, image=piece_image)
        piece_label.image = piece_image  # Keep a reference to avoid garbage collection
        piece_label.pack(side="left")  # Stack the icons horizontally

    # Calculate material advantage
    material_difference = player_material - ai_material
    if material_difference > 0:
        player_material_label.config(text=f"Player Material Advantage: {material_difference}")
        ai_material_label.config(text=f"AI Material Advantage: 0")
    elif material_difference < 0:
        player_material_label.config(text=f"Player Material Advantage: 0")
        ai_material_label.config(text=f"AI Material Advantage: {-material_difference}")
    else:
        player_material_label.config(text="Player Material Advantage: 0")
        ai_material_label.config(text="AI Material Advantage: 0")





# Update captured pieces and material when a capture happens
def on_square_click(event):
    global selected_square, player_turn, highlighted_moves, capturable_squares, player_captured_pieces, player_material

    if not player_turn:
        return  # Ignore clicks if it's not the player's turn

    # Calculate which square was clicked
    x, y = event.x // 125, event.y // 125  # Each square is 125x125 pixels

    # Correct the clicked square based on player color
    if player_is_white:
        square = chess.square(x, 7 - y)  # White: normal
    else:
        square = chess.square(7 - x, y)  # Black: reverse

    if selected_square is None:
        # Select a piece and highlight valid moves
        piece = board.piece_at(square)
        if piece and piece.color == (chess.WHITE if player_is_white else chess.BLACK):  # Ensure the player is selecting their own piece
            selected_square = square
            highlight_valid_moves(selected_square)  # Highlight valid moves for the selected piece
            render_board()  # Show valid moves
        else:
            # If a non-player piece is selected or an empty square, deselect everything
            selected_square = None
            highlighted_moves = []
            capturable_squares = []
            render_board()  # Re-render the board to remove any dots
    else:
        # A piece is selected, so attempt to move to the clicked square
        move = chess.Move(selected_square, square)

        if move in board.legal_moves or chess.Move.from_uci(move.uci() + "q") in board.legal_moves:
            print(f"Move: {move}")  # Debug statement for move

            # Check if it's a promotion move
            if board.piece_at(selected_square).piece_type == chess.PAWN and (chess.square_rank(square) == 0 or chess.square_rank(square) == 7):
                # Handle promotion
                move = handle_pawn_promotion(move)
                print(f"Pawn promoted to {move.promotion}, new move: {move}")

            captured_piece = board.piece_at(square)

            handle_en_passant(move)

            # Track captured pieces
            if captured_piece:
                if player_turn:  # If it's the player's turn and they capture a piece
                    if captured_piece.color != (chess.WHITE if player_is_white else chess.BLACK):  # Player captures opponent's piece
                        piece_type = captured_piece.piece_type
                        player_captured.append(captured_piece.symbol().lower())
                        player_material += piece_values[get_piece_name_by_type(piece_type)]
                        print(f"Player captured a piece: {captured_piece.symbol().lower()}, total player captures: {len(player_captured)}")
                else:  # If it's the AI's turn and they capture a piece
                    piece_type = captured_piece.piece_type
                    ai_captured.append(captured_piece.symbol().lower())
                    ai_material += piece_values[get_piece_name_by_type(piece_type)]
                    print(f"AI captured a piece: {captured_piece.symbol().lower()}, total AI captures: {len(ai_captured)}")

                update_captured_pieces()  # Update the UI with captured pieces and material values

            # Get the SAN notation before pushing the move to the board
            move_san = board.san(move)  # Get the SAN (algebraic notation) of the move

            board.push(move)  # Push the move to the board

            # Log the move in SAN format
            log_move(move_san, "Player")

            render_board()
            check_game_over()  # Check if the game is over
            selected_square = None  # Reset the selection
            highlighted_moves = []  # Clear the highlighted moves
            capturable_squares = []  # Clear capturable squares

            # Switch to AI's turn if the player made a valid move
            player_turn = False
            window.after(1000, ai_move)  # Let the AI make a move after 1 second

            # Adjust ranks after the player's move
            adjust_ranks()

        else:
            selected_square = None
            highlighted_moves = []
            capturable_squares = []
            render_board()






def reset_game():
    global board, selected_square, player_turn, highlighted_moves, capturable_squares, player_captured_pieces, ai_captured_pieces
    global player_captured, ai_captured, player_material, ai_material

    # Reset the board to the starting position
    board = chess.Board()
    selected_square = None
    highlighted_moves = []
    capturable_squares = []
    player_captured_pieces = 0
    ai_captured_pieces = 0
    player_captured = []  # Clear the list of captured pieces for the player
    ai_captured = []  # Clear the list of captured pieces for the AI
    player_material = 0  # Reset material count for the player
    ai_material = 0  # Reset material count for the AI

    # Clear the move log
    move_log.delete(1.0, tk.END)

    # Reset material advantage labels
    player_material_label.config(text="Player Material Advantage: 0")
    ai_material_label.config(text="AI Material Advantage: 0")

    # Clear captured piece icons
    for widget in ai_captures_icons_frame.winfo_children():
        widget.destroy()

    for widget in player_captures_icons_frame.winfo_children():
        widget.destroy()

    # Ask the user to choose color after resetting
    choose_color()

    # Re-render the board
    render_board()

# Function to handle the resignation
def resign_game():
    # Player resigns, so the AI wins (or vice versa if you want to allow AI to resign as well)
    winner = "AI" if player_turn else "Player"
    
    # End the game with a resignation message
    messagebox.showinfo("Game Over", f"{winner} wins by resignation.")
    
    # Show the feedback dialog (same as checkmate or stalemate)
    show_feedback_dialog()


def analyze_move(move_san, player):
    stockfish.set_fen_position(board.fen())  # Set FEN to current board state

    # Get Stockfish's best move for comparison
    best_move = stockfish.get_best_move()

    # Evaluate the position after the player's move
    evaluation_after = stockfish.get_evaluation()  # Stockfish gives an evaluation after the move
    
    # Analyze and give feedback
    eval_difference = evaluation_after['value']  # Get the evaluation value after the move
    
    # Determine if the player's move was a good move, mistake, or neutral
    if eval_difference <= 10:
        feedback = "Good move"
    elif eval_difference > 50:
        feedback = "Mistake"
    else:
        feedback = "Okay move"
    
    # Add feedback to the global feedback list
    move_feedback.append((move_san, feedback, player))

def show_feedback_dialog():
    # Create the feedback window
    feedback_window = tk.Toplevel(window)
    feedback_window.title("Game Feedback")
    feedback_window.geometry("500x600")  # Set the window size

    # Create a frame for the scrollable area
    feedback_frame = tk.Frame(feedback_window)
    feedback_frame.pack(fill=tk.BOTH, expand=True)

    # Add a canvas to the frame
    feedback_canvas = tk.Canvas(feedback_frame)
    feedback_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = tk.Scrollbar(feedback_frame, orient=tk.VERTICAL, command=feedback_canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create a frame inside the canvas for the feedback
    feedback_inner_frame = tk.Frame(feedback_canvas)

    # Configure the canvas to scroll the inner frame
    feedback_canvas.create_window((0, 0), window=feedback_inner_frame, anchor="nw")
    feedback_canvas.config(yscrollcommand=scrollbar.set)

    # Ensure scrolling works properly
    def on_frame_configure(event):
        feedback_canvas.configure(scrollregion=feedback_canvas.bbox("all"))

    feedback_inner_frame.bind("<Configure>", on_frame_configure)

    # Add a label for feedback
    feedback_title = tk.Label(feedback_inner_frame, text="Move Feedback", font=("Arial", 16, "bold"))
    feedback_title.pack(pady=10)

    # Show the first 20 moves in the feedback
    for i, (move_san, feedback, player) in enumerate(move_feedback[:20]):
        move_label = tk.Label(feedback_inner_frame, text=f"Move {i+1}: {player}: {move_san} - {feedback}",
                              font=("Arial", 12))
        # Color the player's moves red
        if player == "Player":
            move_label.config(fg="red")
        move_label.pack(anchor="w")

    # Allow the user to scroll down for more moves
    for i, (move_san, feedback, player) in enumerate(move_feedback[20:], start=21):
        move_label = tk.Label(feedback_inner_frame, text=f"Move {i}: {player}: {move_san} - {feedback}",
                              font=("Arial", 12))
        # Color the player's moves red
        if player == "Player":
            move_label.config(fg="red")
        move_label.pack(anchor="w")
    
    # Update the scrollbar to work with the feedback
    feedback_canvas.update_idletasks()
    feedback_canvas.config(scrollregion=feedback_canvas.bbox("all"))


def check_game_over():
    if board.is_checkmate():
        if board.turn:  # If it's White's turn, it means White has no moves and is in checkmate, so Black (the other side) wins
            if player_is_white:
                winner = "AI"  # White is AI, so AI loses, Black (Player) wins
            else:
                winner = "Player"  # White is AI, so Black (Player) wins
        else:  # If it's Black's turn, it means Black has no moves and is in checkmate, so White wins
            if player_is_white:
                winner = "Player"  # Black is AI, White (Player) wins
            else:
                winner = "AI"  # Black is Player, so White (AI) wins
        print(f"Checkmate! {winner} wins.")
        messagebox.showinfo("Game Over", f"Checkmate! {winner} wins.")
        show_feedback_dialog()  # Show feedback after the game ends
    elif board.is_stalemate():
        print("Stalemate!")
        messagebox.showinfo("Game Over", "Stalemate!")
        show_feedback_dialog()  # Show feedback after a stalemate
    elif board.is_insufficient_material():
        print("Draw by insufficient material!")
        messagebox.showinfo("Game Over", "Draw by insufficient material!")
        show_feedback_dialog()  # Show feedback after a draw
    elif board.is_seventyfive_moves():
        print("Draw by 75-move rule!")
        messagebox.showinfo("Game Over", "Draw by 75-move rule!")
        show_feedback_dialog()  # Show feedback after the 75-move rule
    elif board.is_fivefold_repetition():
        print("Draw by fivefold repetition!")
        messagebox.showinfo("Game Over", "Draw by fivefold repetition!")
        show_feedback_dialog()  # Show feedback after the fivefold repetition



def choose_color():
    global ai_skill_level, ai_difficulty_changes, player_difficulty_changes

    # Set both AI and player starting ranks to Novice
    ai_skill_level = 3  # Novice skill level for AI
    ai_difficulty_changes = 0  # Reset AI difficulty changes
    player_difficulty_changes = 0  # Reset player difficulty changes

    # Update the labels to show "Novice" for both AI and player at the start
    ai_label.config(text=f"AI - Novice")
    player_label.config(text=f"Player - Novice")
    # Create the color selection window
    color_window = tk.Toplevel(window)
    color_window.title("Choose Color")

    # Get screen width and height to center the window
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 300
    window_height = 100
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    color_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def select_color(color):
        global player_is_white, player_turn
        player_is_white = (color == "white")
        player_turn = player_is_white
        color_window.destroy()  # Close the color selection window

        # Ensure the main window is shown and updated
        window.deiconify()  # Show the main window
        render_board()  # Render the board with the chosen color

        if not player_is_white:
            window.after(500, ai_move)  # Let AI play first if Black is chosen after a short delay to update the board

    # Add a label and buttons for choosing color
    tk.Label(color_window, text="Choose your color:").pack(pady=10)

    white_button = tk.Button(color_window, text="White", command=lambda: select_color("white"))
    black_button = tk.Button(color_window, text="Black", command=lambda: select_color("black"))

    white_button.pack(side=tk.LEFT, padx=30)
    black_button.pack(side=tk.RIGHT, padx=30)

    # Hide the main window while choosing color
    window.withdraw()




# Handle clicking on the chessboard
canvas.bind("<Button-1>", on_square_click)


# Ask for the color first, then render the board based on the player's choice
window.withdraw()  # Hide the window until the player chooses the color
choose_color()  # Ask the user to choose a color before starting the game

# Run Tkinter main loop
window.mainloop()
